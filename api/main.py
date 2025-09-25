"""
API FastAPI para análise de risco multimodal
"""
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Imports do nosso core
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import inference_engine
from core.schemas import AnalysisResponse, HealthCheckResponse
from core.ollama_client import ollama_client

# Configuração da aplicação FastAPI
app = FastAPI(
    title="PoC: Análise de Risco Multimodal",
    description="API para análise de risco baseada em dados multimodais usando IA",
    version="1.0.0"
)

# Configuração CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origins específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "PoC: Análise de Risco Multimodal com IA",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Verifica o status da aplicação e dependências"""
    ollama_status = await ollama_client.health_check()
    
    return HealthCheckResponse(
        status="healthy" if ollama_status else "degraded",
        ollama_available=ollama_status,
        timestamp=datetime.now().isoformat()
    )


@app.get("/strategies")
async def get_strategies():
    """Lista as estratégias de análise disponíveis"""
    strategies = inference_engine.get_available_strategies()
    return {
        "available_strategies": strategies,
        "total": len(strategies)
    }


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_risk(
    image: UploadFile = File(..., description="Imagem do rosto para análise"),
    strategy: str = Form(..., description="Nome da estratégia de análise"),
    weight_kg: float = Form(..., description="Peso em quilogramas"),
    additional_metadata: str = Form(default="{}", description="Metadados adicionais em JSON")
):
    """
    Endpoint principal para análise de risco multimodal
    
    Args:
        image: Arquivo de imagem (JPG, PNG, etc.)
        strategy: Nome da estratégia ("basic_risk_assessment" ou "detailed_indicator_analysis")
        weight_kg: Peso da pessoa em kg
        additional_metadata: JSON string com metadados adicionais opcionais
    
    Returns:
        AnalysisResponse com o resultado da análise
    """
    
    # Validação do arquivo de imagem
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo deve ser uma imagem válida (JPG, PNG, etc.)"
        )
    
    # Validação do tamanho do arquivo (máximo 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    image_data = await image.read()
    if len(image_data) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo de imagem muito grande. Máximo permitido: 10MB"
        )
    
    # Validação da estratégia
    available_strategies = inference_engine.get_available_strategies()
    if strategy not in available_strategies:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estratégia '{strategy}' não encontrada. "
                   f"Estratégias disponíveis: {list(available_strategies.keys())}"
        )
    
    # Validação do peso
    if weight_kg <= 0 or weight_kg > 500:  # Limites razoáveis
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Peso deve ser um valor válido entre 0.1 e 500 kg"
        )
    
    # Processa metadados adicionais
    try:
        extra_metadata = json.loads(additional_metadata) if additional_metadata.strip() else {}
        if not isinstance(extra_metadata, dict):
            extra_metadata = {}
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Metadados adicionais devem estar em formato JSON válido"
        )
    
    # Monta os metadados completos
    metadata = {
        "weight_kg": weight_kg,
        **extra_metadata
    }
    
    try:
        # Executa a análise usando o motor de inferência
        result = await inference_engine.run(
            image_data=image_data,
            metadata=metadata,
            strategy_name=strategy
        )
        
        return result
        
    except Exception as e:
        # Log do erro (em produção, usar logging apropriado)
        print(f"Erro na análise: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante análise: {str(e)}"
        )


@app.exception_handler(413)
async def request_entity_too_large_handler(request, exc):
    """Handler customizado para arquivos muito grandes"""
    return JSONResponse(
        status_code=413,
        content={"detail": "Arquivo muito grande. Máximo permitido: 10MB"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )

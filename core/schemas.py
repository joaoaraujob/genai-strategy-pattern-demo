"""
Schemas Pydantic para validação de dados
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, validator


class BasicRiskResponse(BaseModel):
    """Schema para resposta da estratégia básica de avaliação de risco"""
    risk_level: str = Field(..., description="Nível de risco: Baixo, Médio ou Alto")
    reason: str = Field(..., description="Justificativa para o nível de risco")
    
    @validator('risk_level')
    def validate_risk_level(cls, v):
        allowed_levels = ['Baixo', 'Médio', 'Alto', 'Indeterminado']
        if v not in allowed_levels:
            return 'Indeterminado'
        return v


class DetailedIndicatorResponse(BaseModel):
    """Schema para resposta da estratégia detalhada de análise de indicadores"""
    risk_score: float = Field(..., ge=0, le=10, description="Score de risco de 0 a 10")
    indicators: List[str] = Field(..., description="Lista de indicadores identificados")
    summary: str = Field(..., description="Resumo da análise")
    confidence_level: Optional[str] = Field(default="Média", description="Nível de confiança da análise")
    
    @validator('risk_score')
    def validate_risk_score(cls, v):
        if not 0 <= v <= 10:
            return 5.0  # valor padrão se fora do range
        return v
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v):
        if v is None:
            return "Média"
        allowed_levels = ['Alta', 'Média', 'Baixa']
        if v not in allowed_levels:
            return 'Média'
        return v
    
    @validator('indicators')
    def validate_indicators(cls, v):
        if not v or not isinstance(v, list):
            return ["Nenhum indicador identificado"]
        # Limita a 5 indicadores para evitar respostas muito longas
        return v[:5]


class AnalysisRequest(BaseModel):
    """Schema para requisição de análise"""
    strategy: str = Field(..., description="Nome da estratégia a ser utilizada")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")


class AnalysisResponse(BaseModel):
    """Schema para resposta geral de análise"""
    success: bool = Field(..., description="Se a análise foi bem-sucedida")
    strategy: str = Field(..., description="Estratégia utilizada")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado da análise")
    error: Optional[str] = Field(None, description="Mensagem de erro, se houver")
    raw_response: Optional[str] = Field(None, description="Resposta bruta do modelo")
    parse_error: Optional[bool] = Field(False, description="Se houve erro no parsing")
    processing_time: Optional[float] = Field(None, description="Tempo de processamento em segundos")


class HealthCheckResponse(BaseModel):
    """Schema para resposta de health check"""
    status: str = Field(..., description="Status do serviço")
    ollama_available: bool = Field(..., description="Se o Ollama está disponível")
    timestamp: str = Field(..., description="Timestamp da verificação")

"""
Motor de inferência - Orquestrador das estratégias de análise
"""
import time
from typing import Dict, Any, Optional
from pydantic import ValidationError

from .schemas import AnalysisResponse, BasicRiskResponse, DetailedIndicatorResponse
from strategies.base import InferenceStrategy
from strategies.zero_shot_risk_assessment import ZeroShotRiskAssessmentStrategy
from strategies.few_shot_indicator_analysis import FewShotIndicatorAnalysisStrategy


class InferenceEngine:
    """Motor de inferência que orquestra as diferentes estratégias de análise"""
    
    def __init__(self):
        self.strategies = {
            "zero_shot_risk_assessment": ZeroShotRiskAssessmentStrategy(),
            "few_shot_indicator_analysis": FewShotIndicatorAnalysisStrategy()
        }
        
        # Mapeia estratégias para seus schemas de validação
        self.strategy_schemas = {
            "zero_shot_risk_assessment": BasicRiskResponse,
            "few_shot_indicator_analysis": DetailedIndicatorResponse
        }
    
    def get_available_strategies(self) -> Dict[str, str]:
        """Retorna estratégias disponíveis e suas descrições"""
        return {
            name: strategy.description 
            for name, strategy in self.strategies.items()
        }
    
    def get_strategy(self, strategy_name: str) -> Optional[InferenceStrategy]:
        """Obtém uma estratégia pelo nome"""
        return self.strategies.get(strategy_name)
    
    async def run(
        self, 
        image_data: bytes, 
        metadata: Dict[str, Any], 
        strategy_name: str
    ) -> AnalysisResponse:
        """
        Executa análise usando a estratégia especificada
        
        Args:
            image_data: Bytes da imagem
            metadata: Metadados adicionais
            strategy_name: Nome da estratégia a usar
            
        Returns:
            AnalysisResponse com o resultado da análise
        """
        start_time = time.time()
        
        # Verifica se a estratégia existe
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            return AnalysisResponse(
                success=False,
                strategy=strategy_name,
                error=f"Estratégia '{strategy_name}' não encontrada. "
                      f"Estratégias disponíveis: {list(self.strategies.keys())}",
                processing_time=time.time() - start_time
            )
        
        try:
            # Executa a estratégia
            result = await strategy.execute(image_data, metadata)
            
            if not result.get("success", False):
                return AnalysisResponse(
                    success=False,
                    strategy=strategy_name,
                    error=result.get("error", "Erro desconhecido na estratégia"),
                    processing_time=time.time() - start_time
                )
            
            # Tenta validar o resultado usando o schema apropriado
            validated_result = self._validate_result(strategy_name, result.get("result", {}))
            
            return AnalysisResponse(
                success=True,
                strategy=strategy_name,
                result=validated_result,
                raw_response=result.get("raw_response"),
                parse_error=result.get("parse_error", False),
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            return AnalysisResponse(
                success=False,
                strategy=strategy_name,
                error=f"Erro no motor de inferência: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def _validate_result(self, strategy_name: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o resultado usando o schema Pydantic apropriado
        
        Args:
            strategy_name: Nome da estratégia
            result: Resultado a ser validado
            
        Returns:
            Resultado validado ou resultado original se validação falhar
        """
        schema_class = self.strategy_schemas.get(strategy_name)
        if not schema_class:
            return result
        
        try:
            # Tenta validar usando o schema
            validated = schema_class(**result)
            return validated.dict()
        except ValidationError as e:
            # Se validação falhar, retorna resultado original com informação do erro
            return {
                **result,
                "_validation_error": str(e),
                "_validation_failed": True
            }
        except Exception:
            # Para qualquer outro erro, retorna resultado original
            return result


# Instância global do motor de inferência
inference_engine = InferenceEngine()

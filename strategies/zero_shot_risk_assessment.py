"""
Estratégia Zero-Shot para avaliação de risco
"""
import json
from typing import Dict, Any
from .base import InferenceStrategy
from core.ollama_client import ollama_client


class ZeroShotRiskAssessmentStrategy(InferenceStrategy):
    """Estratégia Zero-Shot: Análise de risco sem exemplos prévios, apenas instruções diretas"""
    
    @property
    def strategy_name(self) -> str:
        return "zero_shot_risk_assessment"
    
    @property
    def description(self) -> str:
        return "Zero-Shot: Análise de risco sem exemplos prévios, baseada apenas em instruções"
    
    async def execute(self, image_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa avaliação Zero-Shot de risco
        
        Args:
            image_data: Bytes da imagem do rosto
            metadata: Metadados como peso, etc.
            
        Returns:
            Dict com risk_level e reason
        """
        # Formata os metadados para o prompt
        metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items()])
        
        # ZERO-SHOT: Prompt direto sem exemplos, apenas instruções claras
        prompt = f"""Você é um analista especializado em avaliação de risco para seguros de saúde. 

TAREFA: Analise a imagem fornecida junto com os metadados ({metadata_str}) e determine o nível de risco.

INSTRUÇÕES:
- Observe indicadores visuais gerais na imagem
- Considere os dados fornecidos
- Classifique o risco como: Baixo, Médio ou Alto
- Forneça uma justificativa técnica clara

FORMATO DE RESPOSTA (JSON apenas):
{{
    "risk_level": "[Baixo/Médio/Alto]",
    "reason": "justificativa técnica baseada na análise visual e metadados"
}}

IMPORTANTE: Responda APENAS com o JSON, sem texto adicional."""

        try:
            # Chama o cliente Ollama
            result = await ollama_client.generate_with_image(
                prompt=prompt,
                image_bytes=image_data,
                model="llava"
            )
            
            if not result["success"]:
                return {
                    "success": False,
                    "error": result["error"],
                    "strategy": self.strategy_name
                }
            
            # Tenta extrair JSON da resposta
            response_text = result["response"].strip()
            
            # Remove possíveis prefixos/sufixos não-JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Tenta fazer parse do JSON
            try:
                parsed_result = json.loads(response_text)
                return {
                    "success": True,
                    "strategy": self.strategy_name,
                    "result": parsed_result,
                    "raw_response": result["response"],
                    "approach": "zero-shot"
                }
            except json.JSONDecodeError:
                # Se não conseguir fazer parse, retorna a resposta raw
                return {
                    "success": True,
                    "strategy": self.strategy_name,
                    "result": {
                        "risk_level": "Indeterminado",
                        "reason": "Erro ao processar resposta do modelo (Zero-Shot)"
                    },
                    "raw_response": result["response"],
                    "parse_error": True,
                    "approach": "zero-shot"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na estratégia Zero-Shot: {str(e)}",
                "strategy": self.strategy_name
            }

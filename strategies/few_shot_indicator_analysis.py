"""
Estratégia Few-Shot para análise de indicadores
"""
import json
from typing import Dict, Any
from .base import InferenceStrategy
from core.ollama_client import ollama_client


class FewShotIndicatorAnalysisStrategy(InferenceStrategy):
    """Estratégia Few-Shot: Análise de risco com exemplos prévios para guiar o modelo"""
    
    @property
    def strategy_name(self) -> str:
        return "few_shot_indicator_analysis"
    
    @property
    def description(self) -> str:
        return "Few-Shot: Análise de risco com exemplos prévios para melhor precisão"
    
    async def execute(self, image_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa análise Few-Shot de indicadores
        
        Args:
            image_data: Bytes da imagem do rosto
            metadata: Metadados como peso, etc.
            
        Returns:
            Dict com risk_score, indicators e summary
        """
        # Formata os metadados para o prompt
        metadata_str = ", ".join([f"{k}: {v}" for k, v in metadata.items()])
        
        # FEW-SHOT: Prompt com exemplos específicos para guiar o modelo
        prompt = f"""Você é um analista especializado em avaliação de risco para seguros de saúde. 

EXEMPLOS DE ANÁLISES ANTERIORES (Few-Shot Learning):

EXEMPLO 1:
Imagem: Pessoa jovem, aparência saudável
Metadados: peso: 70kg, idade: 25
Análise:
{{
    "risk_score": 2,
    "indicators": ["Aparência jovem e saudável", "Peso dentro da faixa normal", "Sem sinais visuais de preocupação"],
    "summary": "Perfil de baixo risco baseado na idade jovem e aparência saudável observada",
    "confidence_level": "Alta"
}}

EXEMPLO 2:
Imagem: Pessoa meia-idade, alguns sinais de cansaço
Metadados: peso: 95kg, idade: 45
Análise:
{{
    "risk_score": 6,
    "indicators": ["Sinais de fadiga visível", "Peso acima do ideal", "Faixa etária de risco médio"],
    "summary": "Risco moderado devido ao peso elevado e sinais visuais que sugerem possível estresse ou cansaço",
    "confidence_level": "Média"
}}

EXEMPLO 3:
Imagem: Pessoa idosa, aparência frágil
Metadados: peso: 55kg, idade: 70
Análise:
{{
    "risk_score": 8,
    "indicators": ["Idade avançada", "Aparência de fragilidade", "Peso possivelmente baixo para idade"],
    "summary": "Alto risco devido à idade avançada e aparência que sugere possível fragilidade",
    "confidence_level": "Alta"
}}

AGORA ANALISE:
Imagem: [Imagem fornecida]
Metadados: {metadata_str}

Baseado nos exemplos acima, analise a imagem fornecida seguindo o mesmo padrão de avaliação. Considere indicadores visuais observáveis e os metadados fornecidos.

Responda APENAS em formato JSON válido:
{{
    "risk_score": [número de 0 a 10],
    "indicators": ["indicador1", "indicador2", "indicador3"],
    "summary": "resumo técnico da análise",
    "confidence_level": "[Alta/Média/Baixa]"
}}"""

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
                
                # Valida se os campos obrigatórios estão presentes
                required_fields = ["risk_score", "indicators", "summary"]
                for field in required_fields:
                    if field not in parsed_result:
                        parsed_result[field] = "Não disponível"
                
                # Garante que risk_score seja um número válido
                if not isinstance(parsed_result.get("risk_score"), (int, float)):
                    parsed_result["risk_score"] = 5  # valor padrão
                
                # Garante que indicators seja uma lista
                if not isinstance(parsed_result.get("indicators"), list):
                    parsed_result["indicators"] = ["Análise inconclusiva"]
                
                return {
                    "success": True,
                    "strategy": self.strategy_name,
                    "result": parsed_result,
                    "raw_response": result["response"],
                    "approach": "few-shot"
                }
                
            except json.JSONDecodeError:
                # Se não conseguir fazer parse, retorna estrutura padrão
                return {
                    "success": True,
                    "strategy": self.strategy_name,
                    "result": {
                        "risk_score": 5,
                        "indicators": ["Erro ao processar análise Few-Shot"],
                        "summary": "Não foi possível processar a resposta do modelo adequadamente (Few-Shot)",
                        "confidence_level": "Baixa"
                    },
                    "raw_response": result["response"],
                    "parse_error": True,
                    "approach": "few-shot"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na estratégia Few-Shot: {str(e)}",
                "strategy": self.strategy_name
            }

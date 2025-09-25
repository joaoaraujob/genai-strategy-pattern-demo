"""
Cliente para comunicação com Ollama API - Suporte multimodal com LLaVA
"""
import base64
import json
from typing import Optional, Dict, Any
import httpx


class OllamaClient:
    """Cliente para interagir com a API do Ollama com suporte multimodal"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def _encode_image_to_base64(self, image_bytes: bytes) -> str:
        """Converte bytes da imagem para base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    async def generate_with_image(
        self, 
        prompt: str, 
        image_bytes: bytes, 
        model: str = "llava",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gera resposta usando modelo multimodal com imagem e prompt
        
        Args:
            prompt: Texto do prompt
            image_bytes: Bytes da imagem
            model: Nome do modelo (padrão: llava)
            **kwargs: Parâmetros adicionais para o modelo
            
        Returns:
            Dict com a resposta do modelo
        """
        # Codifica a imagem em base64
        image_base64 = self._encode_image_to_base64(image_bytes)
        
        # Prepara o payload para a API
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_base64],
            "stream": False,
            "options": kwargs
        }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": result.get("model", model),
                    "created_at": result.get("created_at"),
                    "done": result.get("done", True)
                }
                
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"Erro HTTP: {str(e)}",
                "response": ""
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Erro ao decodificar JSON: {str(e)}",
                "response": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro inesperado: {str(e)}",
                "response": ""
            }
    
    async def health_check(self) -> bool:
        """Verifica se o serviço Ollama está rodando"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except:
            return False


# Instância global do cliente
ollama_client = OllamaClient()

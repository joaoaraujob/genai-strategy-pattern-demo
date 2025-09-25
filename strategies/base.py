"""
Classe base abstrata para estratégias de inferência
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class InferenceStrategy(ABC):
    """Classe abstrata base para estratégias de inferência de risco"""
    
    @abstractmethod
    async def execute(self, image_data: bytes, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa a estratégia de inferência
        
        Args:
            image_data: Bytes da imagem a ser analisada
            metadata: Metadados adicionais (ex: peso, idade, etc.)
            
        Returns:
            Dict com o resultado da análise
        """
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Nome da estratégia"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição da estratégia"""
        pass

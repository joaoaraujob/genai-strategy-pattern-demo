#!/usr/bin/env python3
"""
Script de demonstração da PoC de Análise de Risco Multimodal
"""
import asyncio
import json
from pathlib import Path

# Adiciona o diretório atual ao path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.engine import inference_engine
from core.ollama_client import ollama_client


async def demo_strategy_pattern():
    """Demonstra o uso do Strategy Pattern com dados fictícios"""
    print("🔍 PoC: Análise de Risco Multimodal com IA")
    print("=" * 50)
    
    # Verifica se Ollama está disponível
    print("🔄 Verificando disponibilidade do Ollama...")
    health = await ollama_client.health_check()
    
    if not health:
        print("❌ Ollama não está disponível!")
        print("💡 Execute: ollama pull llava")
        print("💡 Certifique-se de que o Ollama está rodando")
        return
    
    print("✅ Ollama disponível!")
    print()
    
    # Lista estratégias disponíveis
    print("📋 Estratégias Disponíveis:")
    strategies = inference_engine.get_available_strategies()
    for name, description in strategies.items():
        print(f"  • {name}: {description}")
    print()
    
    # Simula dados de exemplo
    print("🧪 Executando Demo com Dados Fictícios...")
    print("(Para demo real, use a interface Streamlit)")
    print()
    
    # Dados de exemplo
    fake_image_data = b"fake_image_bytes_for_demo"
    test_metadata = {
        "weight_kg": 75.0,
        "age": 30,
        "demo_mode": True
    }
    
    # Testa cada estratégia
    for strategy_name in strategies.keys():
        print(f"🎯 Testando estratégia: {strategy_name}")
        print(f"📊 Metadados: {test_metadata}")
        
        try:
            # Nota: Isso falhará com dados fictícios, mas demonstra o fluxo
            result = await inference_engine.run(
                image_data=fake_image_data,
                metadata=test_metadata,
                strategy_name=strategy_name
            )
            
            print(f"✅ Status: {'Sucesso' if result.success else 'Falha'}")
            if not result.success:
                print(f"❌ Erro: {result.error}")
            
        except Exception as e:
            print(f"❌ Erro na demonstração: {str(e)}")
        
        print("-" * 30)
        print()
    
    print("🎉 Demo do Strategy Pattern completo!")
    print()
    print("🚀 Para usar a aplicação completa:")
    print("  1. Terminal 1: python run_api.py")
    print("  2. Terminal 2: python run_frontend.py")
    print("  3. Abra: http://localhost:8501")


def show_project_structure():
    """Mostra a estrutura do projeto"""
    print("📦 Estrutura do Projeto:")
    print()
    
    def print_tree(directory, prefix="", max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            return
        
        items = sorted(Path(directory).iterdir())
        dirs = [item for item in items if item.is_dir() and not item.name.startswith('.')]
        files = [item for item in items if item.is_file() and not item.name.startswith('.')]
        
        for i, item in enumerate(dirs + files):
            is_last = i == len(dirs + files) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")
            
            if item.is_dir():
                extension = "    " if is_last else "│   "
                print_tree(item, prefix + extension, max_depth, current_depth + 1)
    
    try:
        print_tree(".")
    except Exception as e:
        print(f"Erro ao mostrar estrutura: {e}")


async def main():
    """Função principal da demonstração"""
    show_project_structure()
    print()
    await demo_strategy_pattern()


if __name__ == "__main__":
    asyncio.run(main())

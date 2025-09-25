import asyncio
import io
from PIL import Image

# Importe a CLASSE OllamaClient do seu arquivo de cliente
# Ajuste o caminho do import se necessário
from core.ollama_client import OllamaClient

async def main():
    """
    Função principal assíncrona para testar a conexão com o Ollama LLaVA.
    """
    print("Iniciando teste de conexão com o Ollama...")

    try:
        # 1. Crie uma instância (um objeto) do seu cliente
        client = OllamaClient()

        # Crie uma imagem de teste simples
        img = Image.new('RGB', (100, 100), color='blue')
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()
        
        # Use um prompt de teste simples
        test_prompt = "O que você vê nesta imagem?"

        print("Enviando requisição para o LLaVA...")
        
        # 2. Chame o MÉTODO .generate_with_image() do objeto client
        response = await client.generate_with_image(
            image_bytes=img_bytes, 
            prompt=test_prompt
        )
        
        print("\n--- Resposta Recebida do Ollama ---")
        print(response)
        print("\n------------------------------------")

        if response and response.get("success"):
            print("\n✅ SUCESSO! A comunicação com o Ollama está funcionando.")
            print(f"Resposta do modelo: {response.get('response')}")
        else:
            print(f"\n❌ ERRO: A comunicação falhou ou retornou um erro.")
            print(f"Detalhes: {response.get('error')}")

    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: Ocorreu uma falha inesperada no script de teste.")
        print(f"Detalhes do erro: {e}")

if __name__ == "__main__":
    # O asyncio.run() executa a função assíncrona 'main'
    asyncio.run(main())
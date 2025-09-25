"""
Interface Streamlit para a PoC de Análise de Risco Multimodal
"""
import streamlit as st
import requests
import json
from PIL import Image
import io
from typing import Dict, Any

# Configuração da página
st.set_page_config(
    page_title="PoC: Análise de Risco Multimodal",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurações da API
API_BASE_URL = "http://localhost:8000"
API_ANALYZE_URL = f"{API_BASE_URL}/analyze"
API_HEALTH_URL = f"{API_BASE_URL}/health"
API_STRATEGIES_URL = f"{API_BASE_URL}/strategies"


def check_api_health() -> bool:
    """Verifica se a API está funcionando"""
    try:
        response = requests.get(API_HEALTH_URL, timeout=5)
        return response.status_code == 200
    except:
        return False


def get_available_strategies() -> Dict[str, Any]:
    """Obtém as estratégias disponíveis da API"""
    try:
        response = requests.get(API_STRATEGIES_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        return {}
    except:
        return {}


def analyze_image(image_file, strategy: str, weight_kg: float, additional_metadata: str = "{}") -> Dict[str, Any]:
    """Chama a API para analisar a imagem"""
    try:
        # Prepara os dados para envio
        files = {"image": (image_file.name, image_file.getvalue(), image_file.type)}
        data = {
            "strategy": strategy,
            "weight_kg": weight_kg,
            "additional_metadata": additional_metadata
        }
        
        # Faz a requisição
        response = requests.post(
            API_ANALYZE_URL,
            files=files,
            data=data,
            timeout=60
        )
        
        return {
            "success": response.status_code == 200,
            "data": response.json(),
            "status_code": response.status_code
        }
        
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout: A análise demorou muito para completar",
            "status_code": 408
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Erro de conexão: Verifique se a API está rodando",
            "status_code": 503
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erro inesperado: {str(e)}",
            "status_code": 500
        }


def display_analysis_result(result: Dict[str, Any], strategy_type: str):
    """Exibe o resultado da análise de forma formatada"""
    if not result.get("success", False):
        st.error(f"❌ Erro na análise: {result.get('error', 'Erro desconhecido')}")
        return
    
    data = result.get("data", {})
    analysis_result = data.get("result", {})
    
    if not data.get("success", False):
        st.error(f"❌ Erro na análise: {data.get('error', 'Erro desconhecido')}")
        return
    
    # Exibe resultados baseado no tipo de estratégia
    if strategy_type == "zero_shot_risk_assessment":
        st.success("✅ Análise Zero-Shot Completada!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            risk_level = analysis_result.get("risk_level", "Indeterminado")
            if risk_level == "Baixo":
                st.success(f"🟢 **Nível de Risco:** {risk_level}")
            elif risk_level == "Médio":
                st.warning(f"🟡 **Nível de Risco:** {risk_level}")
            elif risk_level == "Alto":
                st.error(f"🔴 **Nível de Risco:** {risk_level}")
            else:
                st.info(f"⚪ **Nível de Risco:** {risk_level}")
        
        with col2:
            st.info(f"⏱️ **Tempo:** {data.get('processing_time', 0):.2f}s")
        
        with col3:
            st.info("🎯 **Abordagem:** Zero-Shot")
        
        reason = analysis_result.get("reason", "Não disponível")
        st.write("**💡 Justificativa (sem exemplos prévios):**")
        st.write(reason)
    
    elif strategy_type == "few_shot_indicator_analysis":
        st.success("✅ Análise Few-Shot Completada!")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            risk_score = analysis_result.get("risk_score", 0)
            st.metric("📊 Score de Risco", f"{risk_score}/10")
        
        with col2:
            confidence = analysis_result.get("confidence_level", "Média")
            st.metric("🎯 Confiança", confidence)
        
        with col3:
            st.metric("⏱️ Tempo", f"{data.get('processing_time', 0):.2f}s")
        
        with col4:
            st.info("📚 **Abordagem:** Few-Shot")
        
        # Indicadores
        indicators = analysis_result.get("indicators", [])
        if indicators:
            st.write("**🔍 Indicadores Identificados (baseado em exemplos):**")
            for i, indicator in enumerate(indicators, 1):
                st.write(f"{i}. {indicator}")
        
        # Resumo
        summary = analysis_result.get("summary", "Não disponível")
        st.write("**📋 Resumo da Análise Few-Shot:**")
        st.write(summary)
    
    # Seção de detalhes técnicos (expansível)
    with st.expander("🔧 Detalhes Técnicos"):
        st.json(data)


def main():
    """Função principal da aplicação Streamlit"""
    
    # Título principal
    st.title("🔍 PoC: Análise de Risco Multimodal com IA")
    st.markdown("**Análise preliminar de risco baseada em dados multimodais usando Ollama + LLaVA**")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Verifica status da API
        if check_api_health():
            st.success("✅ API Online")
        else:
            st.error("❌ API Offline")
            st.warning("Certifique-se de que a API está rodando em http://localhost:8000")
            st.stop()
        
        # Informações sobre o projeto
        st.markdown("---")
        st.markdown("### 📚 Sobre o Projeto")
        st.markdown("""
        Esta PoC demonstra:
        - **🎯 Zero-Shot vs 📚 Few-Shot** prompting
        - **Strategy Pattern** para diferentes abordagens
        - **Análise multimodal** com imagem + metadados
        - **Integração com Ollama** (modelo LLaVA)
        - **API REST** com FastAPI
        - **Interface interativa** com Streamlit
        """)
        
        st.markdown("### 🔍 Diferenças das Estratégias")
        st.markdown("""
        **🎯 Zero-Shot:**
        - Análise sem exemplos prévios
        - Baseada apenas em instruções diretas
        - Mais rápida, mas pode ser menos precisa
        
        **📚 Few-Shot:**
        - Análise com exemplos de referência
        - Aprende com casos anteriores
        - Mais lenta, mas potencialmente mais precisa
        """)
    
    # Interface principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📤 Upload da Imagem")
        
        # Upload de imagem
        uploaded_file = st.file_uploader(
            "Escolha uma foto do rosto para análise:",
            type=['png', 'jpg', 'jpeg'],
            help="Formatos aceitos: PNG, JPG, JPEG (máximo 10MB)"
        )
        
        if uploaded_file is not None:
            # Exibe a imagem
            image = Image.open(uploaded_file)
            st.image(image, caption="Imagem carregada", use_column_width=True)
    
    with col2:
        st.header("📊 Parâmetros de Análise")
        
        # Input de peso
        weight_kg = st.number_input(
            "Peso (kg):",
            min_value=1.0,
            max_value=500.0,
            value=70.0,
            step=0.1,
            help="Peso da pessoa em quilogramas"
        )
        
        # Seleção de estratégia
        strategy_options = {
            "zero_shot_risk_assessment": "🎯 Zero-Shot (Sem Exemplos)",
            "few_shot_indicator_analysis": "📚 Few-Shot (Com Exemplos)"
        }
        
        selected_strategy = st.selectbox(
            "Estratégia de Prompting:",
            options=list(strategy_options.keys()),
            format_func=lambda x: strategy_options[x],
            help="Zero-Shot: sem exemplos | Few-Shot: com exemplos prévios"
        )
        
        # Metadados adicionais (opcional)
        with st.expander("➕ Metadados Adicionais (Opcional)"):
            additional_metadata = st.text_area(
                "JSON com metadados extras:",
                value="{}",
                help="Exemplo: {\"idade\": 30, \"genero\": \"M\"}"
            )
        
        # Botão de análise
        analyze_button = st.button(
            "🚀 Iniciar Análise",
            type="primary",
            disabled=uploaded_file is None,
            use_container_width=True
        )
    
    # Processamento da análise
    if analyze_button and uploaded_file is not None:
        st.header("📈 Resultado da Análise")
        
        with st.spinner("🔄 Processando análise... Isso pode levar alguns segundos."):
            result = analyze_image(
                uploaded_file, 
                selected_strategy, 
                weight_kg, 
                additional_metadata
            )
        
        display_analysis_result(result, selected_strategy)
    
    # Informações de uso
    if uploaded_file is None:
        st.info("👆 Faça upload de uma imagem para começar a análise")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🤖 Powered by Ollama + LLaVA | "
        "📊 Strategy Pattern Demo | "
        "🔬 PoC para Análise de Risco"
        "</div>", 
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

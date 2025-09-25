# 🔍 PoC: Análise de Risco Multimodal com IA

Uma **Prova de Conceito (PoC)** completa demonstrando análise de risco preliminar baseada em dados multimodais, utilizando **Ollama**, **LLaVA**, **Strategy Pattern** e interfaces modernas.

## 🎯 Objetivo

Esta aplicação simula um sistema de análise de risco para seguradoras, processando:
- **Imagem:** Foto do rosto da pessoa
- **Metadados:** Informações como peso em kg
- **IA Multimodal:** Inferências usando modelo LLaVA via Ollama

## 🏗️ Arquitetura

```
📦 genai-strategy-pattern-demo/
├── 🔧 api/                    # API REST (FastAPI)
│   ├── __init__.py
│   └── main.py
├── 🧠 core/                   # Funcionalidades centrais
│   ├── __init__.py
│   ├── engine.py              # Motor de inferência
│   ├── ollama_client.py       # Cliente Ollama
│   └── schemas.py             # Schemas Pydantic
├── 🎯 strategies/             # Strategy Pattern
│   ├── __init__.py
│   ├── base.py                # Classe abstrata
│   ├── basic_risk_assessment.py
│   └── detailed_indicator_analysis.py
├── 🖥️ frontend/              # Interface Streamlit
│   ├── __init__.py
│   └── app.py
├── 📁 data/                   # Dados de teste
├── 📋 requirements.txt        # Dependências
├── 🚀 run_api.py             # Script para iniciar API
└── 🚀 run_frontend.py        # Script para iniciar frontend
```

## 🚀 Instalação e Configuração

### 1. Instalar Ollama e LLaVA

```bash
# Instalar Ollama (Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar modelo LLaVA
ollama pull llava
```

### 2. Instalar Dependências Python

```bash
# Criar ambiente virtual (opcional, mas recomendado)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## 🎮 Como Usar

### 1. Iniciar a API (Terminal 1)

```bash
python run_api.py
```

A API estará disponível em: http://localhost:8000
- **Documentação:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### 2. Iniciar o Frontend (Terminal 2)

```bash
python run_frontend.py
```

A interface estará disponível em: http://localhost:8501

### 3. Usar a Aplicação

1. **Upload de Imagem:** Carregue uma foto do rosto
2. **Configurar Parâmetros:** Defina peso e tipo de análise
3. **Executar Análise:** Clique em "Iniciar Análise"
4. **Ver Resultados:** Análise formatada com scores e indicadores

## 🎯 Estratégias de Prompting Disponíveis

### 🎯 Zero-Shot (`zero_shot_risk_assessment`)
- **Abordagem:** Análise sem exemplos prévios, apenas instruções diretas
- **Output:** Nível de risco (Baixo/Médio/Alto) + justificativa
- **Vantagens:** Mais rápida, menor uso de tokens
- **Uso:** Triagem rápida e análises diretas

### 📚 Few-Shot (`few_shot_indicator_analysis`)
- **Abordagem:** Análise com exemplos de referência incluídos no prompt
- **Output:** Score 0-10, indicadores específicos, resumo técnico
- **Vantagens:** Maior precisão e consistência baseada em exemplos
- **Uso:** Análises mais detalhadas e padronizadas

## 🔌 API Endpoints

### `POST /analyze`
Endpoint principal para análise multimodal:

```bash
# Exemplo Zero-Shot
curl -X POST "http://localhost:8000/analyze" \
  -F "image=@foto.jpg" \
  -F "strategy=zero_shot_risk_assessment" \
  -F "weight_kg=70.5" \
  -F "additional_metadata={}"

# Exemplo Few-Shot
curl -X POST "http://localhost:8000/analyze" \
  -F "image=@foto.jpg" \
  -F "strategy=few_shot_indicator_analysis" \
  -F "weight_kg=70.5" \
  -F "additional_metadata={}"
```

### `GET /health`
Verifica status da aplicação e dependências.

### `GET /strategies`
Lista estratégias disponíveis.

## 🧪 Exemplo de Uso via API

```python
import requests

# Analisar imagem
with open("foto.jpg", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"image": f},
        data={
            "strategy": "few_shot_indicator_analysis",
            "weight_kg": 75.0,
            "additional_metadata": '{"idade": 30}'
        }
    )

result = response.json()
print(f"Risk Score: {result['result']['risk_score']}/10")
```

## 💡 Conceitos Demonstrados

- **🎯 Zero-Shot vs 📚 Few-Shot:** Diferentes abordagens de prompting com IA
- **🎯 Strategy Pattern:** Algoritmos intercambiáveis para diferentes estratégias
- **🤖 IA Multimodal:** Processamento conjunto de imagem + dados estruturados
- **📊 Schemas Pydantic:** Validação robusta de dados
- **🔄 Arquitetura Assíncrona:** FastAPI + async/await
- **🖥️ Interface Moderna:** Streamlit com UX intuitiva
- **🧪 PoC Completa:** Do backend à interface, pronto para demonstração

## 🔧 Configurações Avançadas

### Personalizar Prompts
Edite os arquivos em `strategies/` para ajustar prompts de análise.

### Adicionar Nova Estratégia
1. Criar classe herdando de `InferenceStrategy`
2. Implementar método `execute()`
3. Registrar no `InferenceEngine`

### Configurar Modelo
Modifique `ollama_client.py` para usar diferentes modelos multimodais.

## 🚀 Próximos Passos

- [ ] Autenticação e autorização
- [ ] Logging estruturado
- [ ] Cache de resultados
- [ ] Métricas e monitoramento
- [ ] Deploy com Docker
- [ ] Testes automatizados

## 📝 Notas Técnicas

- **Modelo:** LLaVA via Ollama (local)
- **Framework:** FastAPI + Streamlit
- **Validação:** Pydantic schemas
- **Padrão:** Strategy para flexibilidade
- **Prompting:** Zero-Shot vs Few-Shot
- **Dados:** Multimodal (imagem + metadados)

---

**🎯 Esta PoC demonstra uma arquitetura completa e funcional para análise de risco baseada em IA, seguindo melhores práticas de desenvolvimento e design patterns estabelecidos.**

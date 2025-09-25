# 📁 Dados de Teste

Este diretório é destinado para armazenar imagens de teste para a aplicação.

## 🖼️ Formatos Suportados

- **PNG** (.png)
- **JPEG** (.jpg, .jpeg)
- **Tamanho máximo:** 10MB

## 📋 Exemplos de Teste

Para testar a aplicação, você pode usar:

1. **Fotos de rosto** (frontais, boa iluminação)
2. **Imagens de teste** disponíveis online
3. **Dados fictícios** para metadados

## ⚠️ Considerações Éticas

- Use apenas imagens com permissão apropriada
- Esta é uma PoC educacional - não use para análises reais
- Resultados são demonstrativos e não devem ser usados para decisões reais

## 🧪 Dados de Exemplo

Estrutura sugerida para testes:

```
data/
├── test_images/
│   ├── pessoa1.jpg
│   ├── pessoa2.png
│   └── ...
└── test_metadata.json
```

### Exemplo de metadados de teste:

```json
{
  "pessoa1": {
    "weight_kg": 70.5,
    "age": 30,
    "gender": "M"
  },
  "pessoa2": {
    "weight_kg": 65.0,
    "age": 25,
    "gender": "F"
  }
}
```

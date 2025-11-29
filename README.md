# Photo Indexer

Sistema de indexação e busca de fotos usando IA generativa do Google Gemini. Este projeto permite catalogar suas fotos automaticamente com legendas descritivas e buscar por descrições textuais usando embeddings semânticos.

## Migração do Google Colab para VSCode Windows

Este projeto foi originalmente desenvolvido no Google Colab e foi adaptado para funcionar no VSCode no Windows.

## Pré-requisitos

- Python 3.11 ou superior
- VSCode com a extensão Jupyter
- Conta Google com acesso à API do Gemini

## Instalação

### 1. Habilitar Suporte a Caminhos Longos no Windows (Recomendado)

Para evitar erros durante a instalação de pacotes, habilite o suporte a caminhos longos:

1. Abra o Editor de Registro (Win + R, digite `regedit`)
2. Navegue até: `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`
3. Crie ou edite o valor DWORD `LongPathsEnabled` e defina como `1`
4. Reinicie o computador

Ou execute como Administrador no PowerShell:
```powershell
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### 2. Instalar Dependências

```bash
# Instale as dependências com suporte a proxy corporativo (se necessário)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

Ou se você não tiver problemas de proxy:
```bash
pip install -r requirements.txt
```

### 3. Configurar a API Key do Gemini

1. Obtenha sua API Key em: https://aistudio.google.com/apikey
2. Copie o arquivo `.env.example` para `.env`:
   ```bash
   copy .env.example .env
   ```
3. Edite o arquivo `.env` e adicione sua API Key:
   ```
   GEMINI_API_KEY=sua_api_key_aqui
   ```

## Como Usar

O notebook está dividido em duas seções principais:

### Parte 1: INDEXAÇÃO (Executar uma vez por pasta de fotos)

Esta parte gera legendas e embeddings para todas as suas fotos:

1. **Execute a célula 1**: Importa as bibliotecas necessárias
2. **Execute a célula 2**: Configura a API Key do Gemini
3. **Execute a célula 3**: Digite o caminho da pasta com suas fotos quando solicitado
   - Exemplo Windows: `C:/Users/SeuNome/Pictures/Minhas_Fotos`
   - Exemplo Linux/Mac: `/home/usuario/fotos`
4. **Execute a célula 4**: Processa todas as fotos

O processo vai:
- Ler todas as fotos da pasta especificada (formatos: jpg, jpeg, png)
- Gerar legendas descritivas usando IA
- Extrair palavras-chave, categoria e contexto
- Criar embeddings para busca semântica
- Salvar tudo automaticamente em `index.csv` na mesma pasta das fotos

### Parte 2: BUSCA (Executar quantas vezes quiser)

Esta parte permite buscar fotos por descrições textuais:

1. **Execute a célula 3**: Digite a pasta onde está o arquivo `index.csv` quando solicitado
2. **Execute a célula 4**: Digite a frase de busca quando solicitado
3. O sistema mostrará as 5 fotos mais relevantes com suas pontuações de similaridade

Exemplos de frases de busca:
- "Momentos de alegria e diversão"
- "Paisagens naturais e tranquilas"
- "Pessoas sorrindo"
- "Atividades esportivas"
- "Animais e natureza"

## Estrutura de Arquivos

```
photoIndexer/
├── PhotoIndexer.ipynb      # Notebook principal
├── requirements.txt        # Dependências Python
├── .env.example           # Exemplo de configuração
├── .env                   # Sua configuração (não versionar!)
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Este arquivo
└── sample_files/         # Pasta de exemplo para fotos
    ├── foto1.jpg
    ├── foto2.png
    ├── index.csv         # Gerado automaticamente após indexação
    └── session.json      # Opcional: contexto adicional
```

**Nota**: O arquivo `index.csv` é criado automaticamente na pasta das fotos após executar a indexação.

## Diferenças do Google Colab

### O que foi removido:
- `from google.colab import drive` - Não é necessário montar o Drive
- `from google.colab import userdata` - Substituído por `python-dotenv`
- Comandos `!pip install` dentro das células (movido para requirements.txt)

### O que foi adicionado:
- `python-dotenv` - Para gerenciar variáveis de ambiente
- `requirements.txt` - Para instalação de dependências
- `.env` - Para configuração local segura
- Suporte a caminhos do Windows
- **Inputs interativos**: As pastas e frases de busca são solicitadas durante a execução
- **Arquivo de saída automático**: O `index.csv` é sempre salvo na mesma pasta das fotos

### Caminhos de Arquivo

No Windows, use barras normais `/` nos caminhos (Python converte automaticamente):

```
C:/Users/SeuNome/Pictures/Minhas_Fotos
```

Ou use barras invertidas duplas `\\`:

```
C:\\Users\\SeuNome\\Pictures\\Minhas_Fotos
```

**Dica**: Você pode copiar o caminho diretamente do Windows Explorer e colar no input do notebook.

## Contexto de Sessão para Melhor Identificação (RECOMENDADO)

Para obter identificações consistentes e precisas de pessoas nas fotos, crie um arquivo `session.json` **aprimorado** na pasta das fotos. Este contexto ajuda a IA a identificar pessoas específicas ao invés de usar termos genéricos.

### Formato Aprimorado (session.json)

Use o arquivo [session.json.template](session.json.template) como base:

```json
{
  "session_details": {
    "type": "Família | Evento | Produto | Corporativo",
    "location": "Local da sessão",
    "date": "2024-01-15",
    "client": {
      "name": "Nome do Cliente Principal",
      "industry": "Pessoal | Comercial"
    }
  },
  "contextual_description": "Descrição geral da sessão",
  "people": [
    {
      "name": "Nome da Pessoa Principal",
      "role": "Cliente/Mãe/Função",
      "visual_cues": "Mulher adulta, morena, 30-40 anos",
      "priority": "PRIMARY",
      "note": "Sempre use o nome desta pessoa"
    },
    {
      "name": "Familiar ou Amigo",
      "role": "Pai/Filho/etc",
      "visual_cues": "Homem adulto, criança, etc",
      "priority": "SECONDARY"
    }
  ],
  "identification_priority": "CRÍTICO: Sempre identifique a pessoa PRIMARY pelo nome quando ela aparecer nas fotos.",
  "photo_reference": {
    "primary_subject": "foto_referencia.jpg",
    "description": "Retrato solo para referência visual"
  }
}
```

### Benefícios do Formato Aprimorado

- **Consistência de 70-80%** (vs. 57% sem o contexto aprimorado)
- Identificação por nome específico ao invés de termos genéricos ("Juliana" vs. "mulher")
- Hierarquia clara de pessoas (PRIMARY, SECONDARY, TERTIARY)
- Pistas visuais para auxiliar a IA na identificação
- Melhor resultado em buscas por nome de pessoas

### Exemplo Real (Sessão Família)

Veja [.test/session.json](.test/session.json) para um exemplo completo de sessão familiar.

## Testes de Consistência

O projeto inclui scripts para medir a consistência das identificações da IA:

### Analisar Baseline (Dados Existentes)

```bash
python analyze_baseline.py
```

Este script analisa o arquivo `index.csv` existente e calcula:
- Taxa de consistência por foto
- Fotos com identificação consistente vs. inconsistente
- Taxa de consistência geral

**Resultado do Baseline** (.test sem melhorias): 57.1% de consistência

### Testar Melhorias (Reprocessar Fotos)

```bash
python test_consistency.py
```

Este script:
- Processa as mesmas fotos múltiplas vezes (3 runs por padrão)
- Usa o prompt e session.json aprimorados
- Calcula a taxa de consistência
- Salva resultados detalhados em `test_results.json`

**Meta com melhorias**: 70-80% de consistência

## Troubleshooting

### Erro de SSL Certificate
Se você estiver em uma rede corporativa com proxy:
```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org [pacote]
```

### Erro de Caminho Longo
Habilite o suporte a caminhos longos no Windows (veja seção de instalação)

### Kernel não encontrado
1. Certifique-se de ter instalado o `ipykernel`
2. Reinicie o VSCode
3. Selecione o kernel Python 3.11 no notebook

## Limitações da API

- A API Gemini tem limites de taxa (rate limits)
- O código espera 1 segundo entre cada foto processada
- Para muitas fotos, considere fazer em lotes

## Licença

Este projeto está sob licença MIT.

## Suporte

Para problemas ou dúvidas, abra uma issue no GitHub. 

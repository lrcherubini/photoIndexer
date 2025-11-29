# Instruções para Completar Fase 2a - Enriquecimento Visual

## Status da Implementação

✅ **Concluído:**
- session.json.template atualizado com campo `reference_photo`
- .test/session.json atualizado com referência de Juliana
- Célula 4A criada (Enriquecimento de Contexto Visual)

⏳ **Pendente - Modificação Manual Necessária:**

### 1. Atualizar Célula 11 (Script de Indexação)

**Localização:** PhotoIndexer.ipynb, célula após "Bloco 4: O Script Principal"

**Substituir esta seção:**
```python
# --- OTIMIZAÇÃO: Ler o session.json UMA VEZ, fora do loop ---
session_json_content = "Nenhum contexto de sessão fornecido." # Padrão
caminho_sessao = pasta / "session.json" # Procura o JSON na pasta principal

if caminho_sessao.exists():
    try:
        with open(caminho_sessao, 'r', encoding='utf-8') as f:
            session_json_content = f.read()
        print(f"Contexto 'session.json' carregado com sucesso.")
    except Exception as e:
        print(f"--- Aviso: Falha ao ler o session.json. Erro: {e}")
else:
    print("--- Aviso: 'session.json' não encontrado na pasta. Usando prompt padrão.")
```

**Por este código:**
```python
# --- OTIMIZAÇÃO: Ler o session.json (ou enriquecido) UMA VEZ, fora do loop ---
session_json_content = "Nenhum contexto de sessão fornecido." # Padrão
caminho_enriquecido = pasta / "session_enriched.json"
caminho_sessao = pasta / "session.json"

# Priorizar contexto enriquecido se existir
if caminho_enriquecido.exists():
    try:
        with open(caminho_enriquecido, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        # Usar visual_cues_enriched quando disponível
        for person in session_data.get('people', []):
            if 'visual_cues_enriched' in person:
                person['visual_cues'] = person['visual_cues_enriched']

        session_json_content = json.dumps(session_data, ensure_ascii=False, indent=2)
        print(f"✓ Contexto ENRIQUECIDO carregado (session_enriched.json)")
    except Exception as e:
        print(f"--- Aviso: Falha ao ler session_enriched.json. Erro: {e}")
        print("--- Tentando usar session.json normal...")
        caminho_enriquecido = None

# Fallback para session.json normal
if not caminho_enriquecido or not caminho_enriquecido.exists():
    if caminho_sessao.exists():
        try:
            with open(caminho_sessao, 'r', encoding='utf-8') as f:
                session_json_content = f.read()
            print(f"Contexto 'session.json' carregado com sucesso.")
        except Exception as e:
            print(f"--- Aviso: Falha ao ler o session.json. Erro: {e}")
    else:
        print("--- Aviso: 'session.json' não encontrado na pasta. Usando prompt padrão.")
```

**O que mudou:**
- Verifica primeiro se existe `session_enriched.json`
- Se existir, usa `visual_cues_enriched` no lugar de `visual_cues`
- Fallback automático para `session.json` se enriquecido não existir
- Mensagem clara indicando qual contexto foi carregado

---

## 2. Atualizar .gitignore

Adicionar ao final do arquivo `.gitignore`:
```
# Arquivos gerados automaticamente
session_enriched.json
```

---

## 3. Como Testar

### Passo 1: Executar Enriquecimento
1. Abrir PhotoIndexer.ipynb
2. Executar células 1, 2, 3 normalmente
3. **Executar célula 4A** (nova) - Enriquece o contexto
4. Verificar que `session_enriched.json` foi criado na pasta .test

### Passo 2: Processar Fotos
1. Executar célula 11 (Script de Indexação)
2. Verificar mensagem: "✓ Contexto ENRIQUECIDO carregado"
3. Comparar resultados com baseline

### Passo 3: Medir Consistência
```bash
python test_consistency.py
```

**Meta esperada:** 80-85% de consistência (vs. 70-80% Fase 1)

---

## 4. Verificação do Enriquecimento

Após executar célula 4A, verificar o arquivo gerado:

```python
import json
with open('.test/session_enriched.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for person in data['people']:
    if 'visual_cues_enriched' in person:
        print(f"\n{person['name']}:")
        print(f"Original: {person['visual_cues_original']}")
        print(f"Enriquecido: {person['visual_cues_enriched'][:200]}...")
```

Você deve ver descrições muito mais detalhadas!

---

## 5. Troubleshooting

**Problema:** "ERRO: session.json não encontrado"
- **Solução:** Execute célula 3 primeiro para configurar PASTA_DAS_FOTOS

**Problema:** "INFO: Nenhuma pessoa com 'reference_photo' encontrada"
- **Solução:** Adicione `"reference_photo": "nome_arquivo.jpg"` em pelo menos uma pessoa no session.json

**Problema:** "⚠ AVISO: Foto não encontrada"
- **Solução:** Verifique que o arquivo especificado em `reference_photo` existe na pasta

**Problema:** Contexto enriquecido não está sendo usado
- **Solução:** Verifique se a célula 11 foi atualizada com o código acima

---

## Arquivos Modificados

- ✅ `session.json.template` - Adicionado `reference_photo` e documentação
- ✅ `.test/session.json` - Adicionado `reference_photo: "Juliana.jpg"`
- ✅ `PhotoIndexer.ipynb` - Adicionada célula 4A
- ⏳ `PhotoIndexer.ipynb` - Atualizar célula 11 (MANUAL)
- ⏳ `.gitignore` - Adicionar `session_enriched.json`

---

## Próximos Passos (Opcional - Fase 2b)

Após validar que Fase 2a funciona:
1. Implementar histórico conversacional
2. Adicionar scores de confiança
3. Meta: 85-90% de consistência

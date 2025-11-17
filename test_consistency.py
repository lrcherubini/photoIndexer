"""
Script para testar a consistência das identificações da IA
Processa as mesmas fotos múltiplas vezes e mede a taxa de consistência
"""

import google.generativeai as genai
import pandas as pd
import pathlib
import json
import time
import os
from dotenv import load_dotenv
from collections import defaultdict

# Carrega as variáveis de ambiente
load_dotenv()

# Configuração
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("ERRO: GEMINI_API_KEY não encontrada no arquivo .env")
    exit(1)

genai.configure(api_key=api_key)

# Configurações de teste
PASTA_TESTE = r"c:\Users\Leandro.Cherubini\GitHub\photoIndexer\.test"
NUM_RUNS = 3  # Número de vezes para processar cada foto
MODELO_VISAO = 'models/gemini-2.0-flash'

# Prompt aprimorado
PROMPT_LEGENDA = """
Sua única tarefa é analisar a imagem e retornar um objeto JSON.

VOCÊ É UM FOTÓGRAFO PROFISSIONAL E ESPECIALISTA EM CATALOGAÇÃO DE PORTFÓLIO.
Seu objetivo é catalogar esta imagem para um portfólio de fotografia profissional,
identificando pessoas específicas quando possível para facilitar buscas futuras.

---
INFORMAÇÕES DE CONTEXTO DA SESSÃO:
{session_context}
---

INSTRUÇÕES CRÍTICAS PARA IDENTIFICAÇÃO DE PESSOAS:

1. PRIORIDADE MÁXIMA: Se a pessoa na foto corresponde às características da CLIENTE PRINCIPAL
   (marcada como "PRIMARY" no contexto), USE O NOME DELA na legenda, contexto e keywords.

2. Para pessoas marcadas como "SECONDARY" ou "TERTIARY", use seus nomes quando tiver
   confiança razoável na identificação baseada nas pistas visuais fornecidas.

3. Use termos genéricos (mãe, filho, mulher, homem, criança) APENAS quando não puder
   identificar com certeza quem é a pessoa.

4. CONSISTÊNCIA: Mantenha o mesmo padrão de identificação em fotos similares. Se identificou
   alguém pelo nome, continue usando esse nome em outras fotos onde a pessoa apareça.

5. Para acessibilidade, combine descrição visual + nome específico quando possível.
   Exemplo: "Juliana Lombardi sorrindo com sua filha" ao invés de apenas "mãe e filha".

EXEMPLOS DE BOA CATALOGAÇÃO:
- ✓ "Juliana Lombardi e sua filha brincando no sofá"
- ✓ "Retrato de Juliana Lombardi sorrindo, luz natural"
- ✓ "Família reunida: Juliana, marido e filha no apartamento"
- ✗ "Mãe e filha brincando" (muito genérico quando se sabe quem é)
- ✗ "Mulher sorrindo" (muito genérico quando se sabe quem é)

ESTRUTURA DO JSON (OBRIGATÓRIA):
{{
  "caption": "Legenda descritiva incluindo NOMES das pessoas identificadas. Foque no sujeito, ação e cenário.",
  "keywords": {{
    "subjects": ["Nome Pessoa 1", "Nome Pessoa 2", "objeto1", "local"],
    "techniques": ["técnica_fotográfica", "tipo_de_luz"],
    "mood": ["emoção", "atmosfera"]
  }},
  "category": "retrato | familia | grupo | produto | evento | paisagem",
  "context": "Descrição detalhada do contexto da cena incluindo NOMES das pessoas identificadas. Use as informações de contexto da sessão para enriquecer esta descrição."
}}

IMPORTANTE:
- Sempre use nomes próprios quando disponíveis no contexto
- Keywords de "subjects" devem priorizar nomes de pessoas sobre termos genéricos
- Responda APENAS com o JSON, sem texto adicional
- Sempre responda em português BR
"""

def load_session_context(pasta):
    """Carrega o contexto da sessão"""
    caminho_sessao = pathlib.Path(pasta) / "session.json"
    if caminho_sessao.exists():
        with open(caminho_sessao, 'r', encoding='utf-8') as f:
            return f.read()
    return "Nenhum contexto de sessão fornecido."

def process_photo(caminho_foto, prompt, model):
    """Processa uma foto e retorna os dados estruturados"""
    arquivo_upload = None
    try:
        arquivo_upload = genai.upload_file(path=caminho_foto)
        response = model.generate_content([prompt, arquivo_upload])

        # Parse do JSON
        texto_limpo = response.text.strip().replace("```json", "").replace("```", "")
        dados = json.loads(texto_limpo)

        # Extrair informações relevantes para análise
        caption = dados.get('caption', '')
        context = dados.get('context', '')
        keywords_dict = dados.get('keywords', {})
        keywords_subjects = ", ".join(keywords_dict.get('subjects', []))

        # Verificar menções de "Juliana"
        all_text = f"{caption} {context} {keywords_subjects}"
        juliana_mentioned = 'juliana' in all_text.lower()

        return {
            'caption': caption,
            'context': context,
            'keywords_subjects': keywords_subjects,
            'juliana_mentioned': juliana_mentioned,
            'raw_json': dados
        }

    except Exception as e:
        print(f"  ERRO ao processar: {e}")
        return None

    finally:
        if arquivo_upload:
            try:
                genai.delete_file(arquivo_upload.name)
            except:
                pass

def measure_consistency(results_by_photo):
    """Calcula métricas de consistência"""
    total_photos = len(results_by_photo)
    juliana_consistency_count = 0

    print("\n" + "="*80)
    print("ANÁLISE DE CONSISTÊNCIA POR FOTO")
    print("="*80)

    for filename, runs in results_by_photo.items():
        juliana_mentions = [r['juliana_mentioned'] for r in runs if r]
        consistency_rate = sum(juliana_mentions) / len(juliana_mentions) if juliana_mentions else 0

        print(f"\n{filename}:")
        print(f"  Juliana mencionada em {sum(juliana_mentions)}/{len(juliana_mentions)} runs")
        print(f"  Taxa de consistência: {consistency_rate*100:.0f}%")

        # Mostrar as legendas de cada run
        for i, run in enumerate(runs, 1):
            if run:
                mark = "✓" if run['juliana_mentioned'] else "✗"
                print(f"  [{mark}] Run {i}: {run['caption'][:100]}...")

        # Considerar consistente se for 100% sim ou 100% não
        if consistency_rate == 1.0 or consistency_rate == 0.0:
            juliana_consistency_count += 1

    overall_consistency = (juliana_consistency_count / total_photos * 100) if total_photos > 0 else 0

    print("\n" + "="*80)
    print("RESULTADO GERAL")
    print("="*80)
    print(f"Total de fotos testadas: {total_photos}")
    print(f"Fotos com identificação consistente: {juliana_consistency_count}")
    print(f"Taxa de consistência geral: {overall_consistency:.1f}%")
    print("="*80)

    return overall_consistency

def main():
    print("="*80)
    print("TESTE DE CONSISTÊNCIA - PhotoIndexer")
    print("="*80)
    print(f"Pasta de teste: {PASTA_TESTE}")
    print(f"Número de runs por foto: {NUM_RUNS}")
    print(f"Modelo: {MODELO_VISAO}")
    print("="*80)

    # Carregar contexto da sessão
    session_context = load_session_context(PASTA_TESTE)
    final_prompt = PROMPT_LEGENDA.format(session_context=session_context)

    # Carregar modelo
    model = genai.GenerativeModel(MODELO_VISAO)

    # Encontrar fotos (com deduplicação)
    pasta = pathlib.Path(PASTA_TESTE)
    extensoes = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
    arquivos_encontrados = []
    for ext in extensoes:
        arquivos_encontrados.extend(pasta.glob(ext))

    # Deduplica usando lowercase (Windows = case-insensitive)
    arquivos_unicos = {}
    for arquivo in arquivos_encontrados:
        chave = str(arquivo.absolute()).lower()
        if chave not in arquivos_unicos:
            arquivos_unicos[chave] = arquivo

    fotos = list(arquivos_unicos.values())
    print(f"\nEncontradas {len(fotos)} fotos únicas para testar\n")

    # Processar cada foto múltiplas vezes
    results_by_photo = defaultdict(list)

    for foto in fotos:
        print(f"\nProcessando {foto.name}...")
        for run in range(NUM_RUNS):
            print(f"  Run {run + 1}/{NUM_RUNS}...", end=" ")
            result = process_photo(foto, final_prompt, model)
            results_by_photo[foto.name].append(result)

            if result and result['juliana_mentioned']:
                print("✓ Juliana mencionada")
            elif result:
                print("✗ Juliana não mencionada")
            else:
                print("⚠ Erro no processamento")

            # Pausa para evitar limite de API
            if run < NUM_RUNS - 1:
                time.sleep(2)

        # Pausa maior entre fotos
        time.sleep(3)

    # Medir consistência
    consistency_rate = measure_consistency(results_by_photo)

    # Salvar resultados detalhados
    output_file = pasta / "test_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dict(results_by_photo), f, ensure_ascii=False, indent=2)

    print(f"\nResultados detalhados salvos em: {output_file}")
    print(f"\n{'='*80}")
    print(f"TAXA DE CONSISTÊNCIA FINAL: {consistency_rate:.1f}%")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()

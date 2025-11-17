"""
Analisa a consistência do baseline (dados existentes no index.csv)
"""

import pandas as pd
from collections import defaultdict

# Carregar o CSV
csv_path = r"c:\Users\Leandro.Cherubini\GitHub\photoIndexer\.test\index.csv"
df = pd.read_csv(csv_path)

print("="*80)
print("ANÁLISE DE CONSISTÊNCIA - BASELINE (Dados Existentes)")
print("="*80)
print(f"Total de registros: {len(df)}")
print(f"Arquivos únicos: {df['arquivo'].nunique()}")
print("="*80)

# Agrupar por arquivo
results_by_photo = defaultdict(list)

for arquivo in df['arquivo'].unique():
    rows = df[df['arquivo'] == arquivo]

    for idx, row in rows.iterrows():
        # Combinar todos os campos de texto
        all_text = f"{row['legenda']} {row['contexto']} {row['keywords_assuntos']}"
        juliana_mentioned = 'juliana' in all_text.lower()

        results_by_photo[arquivo].append({
            'legenda': row['legenda'],
            'contexto': row['contexto'],
            'keywords': row['keywords_assuntos'],
            'juliana_mentioned': juliana_mentioned
        })

# Análise de consistência
print("\nANÁLISE POR FOTO:\n")

total_photos = len(results_by_photo)
consistent_photos = 0

for arquivo, runs in sorted(results_by_photo.items()):
    juliana_mentions = [r['juliana_mentioned'] for r in runs]
    num_mentions = sum(juliana_mentions)
    num_runs = len(juliana_mentions)
    consistency_rate = num_mentions / num_runs if num_runs > 0 else 0

    # Considera consistente se for 100% sim ou 100% não
    is_consistent = (consistency_rate == 1.0 or consistency_rate == 0.0)
    if is_consistent:
        consistent_photos += 1

    status = "[OK] CONSISTENTE" if is_consistent else "[!!] INCONSISTENTE"

    print(f"{arquivo}:")
    print(f"  Status: {status}")
    print(f"  Juliana mencionada: {num_mentions}/{num_runs} runs ({consistency_rate*100:.0f}%)")

    # Mostrar cada run
    for i, run in enumerate(runs, 1):
        mark = "[+]" if run['juliana_mentioned'] else "[-]"
        print(f"  [{mark}] Run {i}:")
        print(f"      Legenda: {run['legenda'][:120]}...")
    print()

# Resultado geral
overall_consistency = (consistent_photos / total_photos * 100) if total_photos > 0 else 0

print("="*80)
print("RESULTADO GERAL - BASELINE")
print("="*80)
print(f"Total de fotos analisadas: {total_photos}")
print(f"Fotos com identificação consistente: {consistent_photos}")
print(f"Fotos com identificação inconsistente: {total_photos - consistent_photos}")
print(f"TAXA DE CONSISTÊNCIA GERAL: {overall_consistency:.1f}%")
print("="*80)

# Estatísticas adicionais
print("\nESTATÍSTICAS ADICIONAIS:")
print("="*80)

total_runs = len(df)
juliana_total_mentions = sum(1 for _, row in df.iterrows()
                              if 'juliana' in f"{row['legenda']} {row['contexto']} {row['keywords_assuntos']}".lower())

print(f"Total de processamentos: {total_runs}")
print(f"Vezes que Juliana foi mencionada: {juliana_total_mentions}")
print(f"Taxa de menção geral: {juliana_total_mentions/total_runs*100:.1f}%")
print("="*80)

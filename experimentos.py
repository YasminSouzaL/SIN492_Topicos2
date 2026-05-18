"""
experimentos.py
---------------
Executa os experimentos computacionais para o GQAP comparando:
  1. Heurística construtiva gulosa (TP01)
  2. Construtiva + Busca Local VND   (TP02)

Saída
-----
  • Tabela LaTeX com resultados agregados por tamanho e capacidade
  • Arquivo CSV com todos os resultados individuais (experimentos.csv)
  • Resumo no terminal

Uso
---
  python experimentos.py
"""

import time
import csv
import os
import sys

from instancias   import gerar_conjunto_instancias
from heuristica   import heuristica_gulosa
from busca_local  import busca_local_vnd


# ---------------------------------------------------------------------------
# Execução de um único experimento
# ---------------------------------------------------------------------------

def executar_instancia(instancia):
    """
    Roda a heurística construtiva e depois a busca local sobre a mesma instância.

    Retorna dict com todos os resultados.
    """
    # --- Heurística construtiva ---
    t0 = time.perf_counter()
    sol_g, custo_g, nao_aloc_g = heuristica_gulosa(instancia)
    t_gulosa = time.perf_counter() - t0

    # --- Busca local (VND) ---
    t0 = time.perf_counter()
    sol_bl, custo_bl, historico = busca_local_vnd(sol_g, instancia)
    t_bl = time.perf_counter() - t0

    # Melhora percentual
    if custo_g > 0:
        melhora_pct = 100.0 * (custo_g - custo_bl) / custo_g
    else:
        melhora_pct = 0.0

    # Movimentos totais na busca local
    total_movimentos = sum(h['movimentos'] for h in historico)

    return {
        'label_tamanho'    : instancia['label_tamanho'],
        'label_capacidade' : instancia['label_capacidade'],
        'n_produtos'       : instancia['n_produtos'],
        'n_maquinas'       : instancia['n_maquinas'],
        'alpha'            : instancia['alpha'],
        'semente'          : instancia['semente'],
        'custo_gulosa'     : custo_g,
        'nao_alocados'     : len(nao_aloc_g),
        'tempo_gulosa_ms'  : t_gulosa * 1000,
        'custo_bl'         : custo_bl,
        'tempo_bl_ms'      : t_bl * 1000,
        'melhora_pct'      : melhora_pct,
        'movimentos_bl'    : total_movimentos,
    }


# ---------------------------------------------------------------------------
# Rodada de todos os experimentos
# ---------------------------------------------------------------------------

def rodar_experimentos():
    instancias = gerar_conjunto_instancias()
    resultados = []

    print(f"{'Instância':<30} {'C.Gulosa':>12} {'C.BL':>12} {'Melhora':>9} {'T.BL(ms)':>10}")
    print("-" * 80)

    for idx, inst in enumerate(instancias):
        r = executar_instancia(inst)
        resultados.append(r)

        label = f"{r['label_tamanho']}-{r['label_capacidade']}-s{r['semente']}"
        print(f"{label:<30} {r['custo_gulosa']:>12.1f} {r['custo_bl']:>12.1f} "
              f"{r['melhora_pct']:>8.2f}% {r['tempo_bl_ms']:>10.2f}")

    return resultados


# ---------------------------------------------------------------------------
# Persistência em CSV
# ---------------------------------------------------------------------------

def salvar_csv(resultados, caminho='experimentos.csv'):
    if not resultados:
        return
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
        writer.writeheader()
        writer.writerows(resultados)
    print(f"\nResultados salvos em: {caminho}")


# ---------------------------------------------------------------------------
# Tabela LaTeX
# ---------------------------------------------------------------------------

def gerar_tabela_latex(resultados):
    """
    Gera uma tabela LaTeX com médias agregadas por (tamanho, capacidade).
    """
    from collections import defaultdict

    grupos = defaultdict(list)
    for r in resultados:
        chave = (r['label_tamanho'], r['n_produtos'], r['n_maquinas'],
                 r['label_capacidade'], r['alpha'])
        grupos[chave].append(r)

    ordem_tam = {'Pequena': 0, 'Media': 1, 'Grande': 2}
    ordem_cap = {'Apertada': 0, 'Media': 1, 'Folgada': 2}

    linhas = []
    for chave, grupo in sorted(grupos.items(),
                                key=lambda x: (ordem_tam[x[0][0]], ordem_cap[x[0][3]])):
        label_tam, n, m, label_cap, alpha = chave
        med_g   = sum(r['custo_gulosa']    for r in grupo) / len(grupo)
        med_bl  = sum(r['custo_bl']        for r in grupo) / len(grupo)
        med_imp = sum(r['melhora_pct']     for r in grupo) / len(grupo)
        med_tg  = sum(r['tempo_gulosa_ms'] for r in grupo) / len(grupo)
        med_tb  = sum(r['tempo_bl_ms']     for r in grupo) / len(grupo)
        linhas.append((label_tam, n, m, label_cap, alpha,
                       med_g, med_bl, med_imp, med_tg, med_tb))

    latex = []
    latex.append(r'\begin{table}[ht]')
    latex.append(r'\centering')
    latex.append(r'\caption{Resultados médios por grupo de instâncias '
                 r'(5 sementes por grupo)}')
    latex.append(r'\label{tab:resultados}')
    latex.append(r'\begin{tabular}{|l|c|c|l|r|r|r|r|r|}')
    latex.append(r'\hline')
    latex.append(r'\textbf{Tam.} & \textbf{n} & \textbf{m} & '
                 r'\textbf{Cap.} & \textbf{C.Gul.} & \textbf{C.BL} & '
                 r'\textbf{Mel.\%} & \textbf{T.Gul.(ms)} & \textbf{T.BL(ms)} \\')
    latex.append(r'\hline')

    ultimo_tam = None
    for (lt, n, m, lc, alpha, cg, cb, imp, tg, tb) in linhas:
        if lt != ultimo_tam and ultimo_tam is not None:
            latex.append(r'\hline')
        ultimo_tam = lt
        latex.append(
            f'{lt} & {n} & {m} & {lc} & '
            f'{cg:.0f} & {cb:.0f} & {imp:.1f} & '
            f'{tg:.2f} & {tb:.2f} \\\\'
        )

    latex.append(r'\hline')
    latex.append(r'\end{tabular}')
    latex.append(r'\end{table}')

    return '\n'.join(latex)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("=" * 80)
    print("GQAP — Experimentos Computacionais")
    print("Heurística Construtiva Gulosa  vs.  Construtiva + Busca Local VND")
    print("=" * 80)
    print()

    resultados = rodar_experimentos()

    salvar_csv(resultados)

    print()
    print("=" * 80)
    print("TABELA LATEX")
    print("=" * 80)
    print()
    print(gerar_tabela_latex(resultados))

    # Resumo geral
    print()
    print("=" * 80)
    print("RESUMO GERAL")
    print("=" * 80)
    total = len(resultados)
    med_melhora = sum(r['melhora_pct'] for r in resultados) / total
    max_melhora = max(r['melhora_pct'] for r in resultados)
    med_t_bl    = sum(r['tempo_bl_ms'] for r in resultados) / total
    sem_alocar  = sum(1 for r in resultados if r['nao_alocados'] > 0)

    print(f"Total de instâncias        : {total}")
    print(f"Instâncias com não-alocados: {sem_alocar}")
    print(f"Melhora média (BL vs Gul.) : {med_melhora:.2f}%")
    print(f"Melhora máxima             : {max_melhora:.2f}%")
    print(f"Tempo médio BL (ms)        : {med_t_bl:.2f}")

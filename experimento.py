import time
import csv
import os
import sys
from collections import defaultdict

# matplotlib é opcional — se não estiver instalado, pula os gráficos
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False
    print("AVISO: matplotlib/numpy não encontrado.")
    print("       Instale com:  pip install matplotlib numpy")
    print("       Os gráficos serão pulados.\n")

from instancias  import gerar_conjunto_instancias
from heuristica  import heuristica_gulosa
from busca_local import busca_local_vnd

# Pasta onde o script está sendo executado
PASTA = os.path.dirname(os.path.abspath(__file__))



# Execução de uma instância

def executar_instancia(instancia):
    t0 = time.perf_counter()
    sol_g, custo_g, nao_aloc_g = heuristica_gulosa(instancia)
    t_gulosa = time.perf_counter() - t0

    t0 = time.perf_counter()
    sol_bl, custo_bl, historico = busca_local_vnd(sol_g, instancia)
    t_bl = time.perf_counter() - t0

    melhora_pct = 100.0 * (custo_g - custo_bl) / custo_g if custo_g > 0 else 0.0

    return {
        'label_tamanho'   : instancia['label_tamanho'],
        'label_capacidade': instancia['label_capacidade'],
        'n_produtos'      : instancia['n_produtos'],
        'n_maquinas'      : instancia['n_maquinas'],
        'alpha'           : instancia['alpha'],
        'semente'         : instancia['semente'],
        'custo_gulosa'    : custo_g,
        'nao_alocados'    : len(nao_aloc_g),
        'tempo_gulosa_ms' : round(t_gulosa * 1000, 4),
        'custo_bl'        : custo_bl,
        'tempo_bl_ms'     : round(t_bl * 1000, 4),
        'melhora_pct'     : round(melhora_pct, 4),
        'movimentos_bl'   : sum(h['movimentos'] for h in historico),
    }



# Rodada completa


def rodar_experimentos():
    instancias = gerar_conjunto_instancias()
    resultados = []

    print(f"{'Instância':<30} {'C.Gulosa':>12} {'C.BL':>12} {'Melhora':>9} {'T.BL(ms)':>10}")
    print("-" * 80)

    for inst in instancias:
        r = executar_instancia(inst)
        resultados.append(r)
        label = f"{r['label_tamanho']}-{r['label_capacidade']}-s{r['semente']}"
        print(f"{label:<30} {r['custo_gulosa']:>12.1f} {r['custo_bl']:>12.1f} "
              f"{r['melhora_pct']:>8.2f}% {r['tempo_bl_ms']:>10.2f}")

    return resultados



# Agregação por grupo
def agregar_grupos(resultados):
    ordem_tam = {'Pequena': 0, 'Media': 1, 'Grande': 2}
    ordem_cap = {'Apertada': 0, 'Media': 1, 'Folgada': 2}

    grupos = defaultdict(list)
    for r in resultados:
        chave = (r['label_tamanho'], r['n_produtos'], r['n_maquinas'],
                 r['label_capacidade'], r['alpha'])
        grupos[chave].append(r)

    linhas = []
    for chave, grupo in sorted(grupos.items(),
                               key=lambda x: (ordem_tam[x[0][0]], ordem_cap[x[0][3]])):
        lt, n, m, lc, alpha = chave
        linhas.append({
            'tamanho'        : lt,
            'n_produtos'     : n,
            'n_maquinas'     : m,
            'capacidade'     : lc,
            'alpha'          : alpha,
            'label_eixo'     : f"{lt[:3]}/{lc[:2]}",
            'med_custo_gul'  : round(sum(r['custo_gulosa']    for r in grupo) / len(grupo), 1),
            'med_custo_bl'   : round(sum(r['custo_bl']        for r in grupo) / len(grupo), 1),
            'med_melhora_pct': round(sum(r['melhora_pct']     for r in grupo) / len(grupo), 2),
            'med_tempo_gul'  : round(sum(r['tempo_gulosa_ms'] for r in grupo) / len(grupo), 4),
            'med_tempo_bl'   : round(sum(r['tempo_bl_ms']     for r in grupo) / len(grupo), 4),
            'n_instancias'   : len(grupo),
        })
    return linhas



# CSV — individual e agregado


def salvar_csvs(resultados, linhas_agr):
    # CSV individual (todas as 45 instâncias)
    caminho_ind = os.path.join(PASTA, 'result2', 'experimentos_individual.csv')
    with open(caminho_ind, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=resultados[0].keys())
        writer.writeheader()
        writer.writerows(resultados)
    print(f"  • {caminho_ind}")

    # CSV agregado (9 grupos com médias)
    caminho_agr = os.path.join(PASTA, 'result2', 'experimentos_agregado.csv')
    campos = ['tamanho', 'n_produtos', 'n_maquinas', 'capacidade', 'alpha',
              'med_custo_gul', 'med_custo_bl', 'med_melhora_pct',
              'med_tempo_gul', 'med_tempo_bl', 'n_instancias']
    with open(caminho_agr, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(linhas_agr)
    print(f"  • {caminho_agr}")



# Tabela LaTeX

'''
def gerar_tabela_latex(linhas):
    latex = [
        r'\begin{table}[ht]',
        r'\centering',
        r'\caption{Resultados médios por grupo de instâncias (5 sementes por grupo)}',
        r'\label{tab:resultados}',
        r'\begin{tabular}{|l|c|c|l|r|r|r|r|r|}',
        r'\hline',
        r'\textbf{Tam.} & \textbf{n} & \textbf{m} & \textbf{Cap.} & '
        r'\textbf{C.Gul.} & \textbf{C.BL} & \textbf{Mel.\%} & '
        r'\textbf{T.Gul.(ms)} & \textbf{T.BL(ms)} \\',
        r'\hline',
    ]
    ultimo = None
    for l in linhas:
        if ultimo and l['tamanho'] != ultimo:
            latex.append(r'\hline')
        ultimo = l['tamanho']
        latex.append(
            f"{l['tamanho']} & {l['n_produtos']} & {l['n_maquinas']} & "
            f"{l['capacidade']} & {l['med_custo_gul']:.0f} & "
            f"{l['med_custo_bl']:.0f} & {l['med_melhora_pct']:.1f} & "
            f"{l['med_tempo_gul']:.2f} & {l['med_tempo_bl']:.2f} \\\\"
        )
    latex += [r'\hline', r'\end{tabular}', r'\end{table}']
    return '\n'.join(latex)
'''


# Gráficos


def gerar_graficos(linhas):
    if not MATPLOTLIB_OK:
        print("  Gráficos pulados (matplotlib não instalado).")
        return

    plt.rcParams.update({
        'font.family'     : 'DejaVu Sans',
        'axes.spines.top' : False,
        'axes.spines.right': False,
        'axes.grid'       : True,
        'grid.alpha'      : 0.35,
        'grid.linestyle'  : '--',
    })

    COR_GUL = '#4C72B0'
    COR_BL  = '#DD8452'
    COR_MEL = '#55A868'

    labels  = [l['label_eixo']      for l in linhas]
    c_gul   = [l['med_custo_gul']   for l in linhas]
    c_bl    = [l['med_custo_bl']    for l in linhas]
    melhora = [l['med_melhora_pct'] for l in linhas]
    t_bl    = [l['med_tempo_bl']    for l in linhas]
    x = np.arange(len(labels))

    # ── Figura 1: Custo comparativo ──────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5.5))
    larg = 0.38
    ax.bar(x - larg/2, c_gul, larg, label='Heurística Gulosa',
           color=COR_GUL, edgecolor='white', linewidth=0.6)
    ax.bar(x + larg/2, c_bl, larg, label='Busca Local VND',
           color=COR_BL, edgecolor='white', linewidth=0.6)
    for xv in [2.5, 5.5]:
        ax.axvline(xv, color='gray', linestyle=':', linewidth=1.2, alpha=0.6)
    ymax = ax.get_ylim()[1]
    for xc, txt in zip([1, 4, 7], ['Pequenas (n=10)', 'Médias (n=20)', 'Grandes (n=40)']):
        ax.text(xc, ymax * 0.97, txt, ha='center', fontsize=9, color='gray', style='italic')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Custo médio da solução', fontsize=11)
    ax.set_title('Custo Médio: Heurística Gulosa vs. Busca Local VND',
                 fontsize=12, fontweight='bold', pad=12)
    ax.legend(fontsize=10)
    fig.tight_layout()
    p = os.path.join(PASTA, 'result2', 'fig1_comparacao_custos.png')
    fig.savefig(p, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  • {p}")

    # ── Figura 2: Melhora percentual ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5.5))
    cores = [COR_MEL]*3 + ['#8172B2']*3 + ['#C44E52']*3
    bars = ax.bar(x, melhora, color=cores, edgecolor='white', linewidth=0.6)
    for bar, val in zip(bars, melhora):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    media_geral = sum(melhora) / len(melhora)
    ax.axhline(media_geral, color='navy', linestyle='--', linewidth=1.4, alpha=0.8)
    for xv in [2.5, 5.5]:
        ax.axvline(xv, color='gray', linestyle=':', linewidth=1.2, alpha=0.6)
    leg = [
        mpatches.Patch(color=COR_MEL,   label='Pequenas'),
        mpatches.Patch(color='#8172B2', label='Médias'),
        mpatches.Patch(color='#C44E52', label='Grandes'),
        plt.Line2D([0],[0], color='navy', linestyle='--',
                   label=f'Média geral: {media_geral:.1f}%'),
    ]
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Melhora média (%)', fontsize=11)
    ax.set_ylim(0, max(melhora) * 1.18)
    ax.set_title('Melhora Percentual da Busca Local sobre a Heurística Gulosa',
                 fontsize=12, fontweight='bold', pad=12)
    ax.legend(handles=leg, fontsize=9)
    fig.tight_layout()
    #Salva na pasta result2
    final_path = os.path.join(PASTA, 'result2', 'fig2_melhora_pct.png')
    fig.savefig(final_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  • {final_path}")

    # ── Figura 3: Tempo de execução ───────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(11, 5.5))
    bars = ax.bar(x, t_bl, color='#C44E52', edgecolor='white', linewidth=0.6, alpha=0.85)
    for bar, val in zip(bars, t_bl):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{val:.0f}ms', ha='center', va='bottom', fontsize=8.5)
    for xv in [2.5, 5.5]:
        ax.axvline(xv, color='gray', linestyle=':', linewidth=1.2, alpha=0.6)
    ymax = ax.get_ylim()[1]
    for xc, txt in zip([1, 4, 7], ['Pequenas', 'Médias', 'Grandes']):
        ax.text(xc, ymax * 0.93, txt, ha='center', fontsize=9, color='gray', style='italic')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Tempo médio (ms)', fontsize=11)
    ax.set_title('Tempo de Execução Médio da Busca Local VND por Grupo',
                 fontsize=12, fontweight='bold', pad=12)
    fig.tight_layout()
    p = os.path.join(PASTA, 'result2', 'fig3_tempo.png')
    fig.savefig(p, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  • {p}")



# Main


if __name__ == '__main__':
    
    print("GQAP — Experimentos Computacionais")
    print("Heurística Construtiva Gulosa  vs.  Construtiva + Busca Local VND")
    print()

    resultados  = rodar_experimentos()
    linhas_agr  = agregar_grupos(resultados)

    print()
    print("SALVANDO ARQUIVOS CSV")    
    salvar_csvs(resultados, linhas_agr)

    print()
    print("GERANDO GRÁFICOS")
    gerar_graficos(linhas_agr)
    print()
    
    print("RESUMO GERAL")
    total       = len(resultados)
    med_melhora = sum(r['melhora_pct'] for r in resultados) / total
    max_melhora = max(r['melhora_pct'] for r in resultados)
    med_t_bl    = sum(r['tempo_bl_ms'] for r in resultados) / total
    sem_alocar  = sum(1 for r in resultados if r['nao_alocados'] > 0)
    print(f"Total de instâncias        : {total}")
    print(f"Instâncias com não-alocados: {sem_alocar}")
    print(f"Melhora média (BL vs Gul.) : {med_melhora:.2f}%")
    print(f"Melhora máxima             : {max_melhora:.2f}%")
    print(f"Tempo médio BL (ms)        : {med_t_bl:.2f}")
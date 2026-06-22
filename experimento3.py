import time
import csv
import os
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    MPL_OK = True
except ImportError:
    MPL_OK = False
    print("AVISO: matplotlib/numpy não encontrado. Instale com: pip install matplotlib numpy\n")

from instancias        import gerar_conjunto_instancias
from instancias_orlib  import gerar_instancias_orlib
from heuristica        import heuristica_gulosa
from busca_local       import busca_local_vnd
from grasp             import grasp
from tabu_search       import tabu_search

PASTA     = os.path.dirname(os.path.abspath(__file__))
PASTA_OUT = os.path.join(PASTA, 'result3')
os.makedirs(PASTA_OUT, exist_ok=True)

GRASP_ITER      = 100
GRASP_ALPHA     = 0.3
TABU_ITER       = 200
TABU_TENURE     = 10

# GRASP+Tabu — cenário 1 (Tabu como intensificador rápido, muitas reconstruções)
GT1_MAX_ITER     = 100
GT1_TABU_ITER    = 20
GT1_TABU_TENURE  = 7
# GRASP+Tabu — cenário 2 (Tabu como intensificador forte, poucas reconstruções)
GT2_MAX_ITER     = 20
GT2_TABU_ITER    = 100
GT2_TABU_TENURE  = 20




def executar_instancia(inst):
    semente = inst.get('semente', 42)

    # --- Etapa 1: Gulosa ---
    t0 = time.perf_counter()
    sol_g, custo_g, nao_aloc = heuristica_gulosa(inst)
    t_g = (time.perf_counter() - t0) * 1000

    # --- Etapa 2: VND ---
    t0 = time.perf_counter()
    sol_bl, custo_bl, hist_bl = busca_local_vnd(sol_g, inst)
    t_bl = (time.perf_counter() - t0) * 1000

    # --- Etapa 3a: GRASP + VND ---
    t0 = time.perf_counter()
    sol_gv, custo_gv, hist_gv = grasp(inst, max_iter=GRASP_ITER,
                                       alpha=GRASP_ALPHA, semente=semente,
                                       busca_local='vnd')
    t_gv = (time.perf_counter() - t0) * 1000

    # --- Etapa 3b: Busca Tabu pura (parte da solução gulosa) ---
    t0 = time.perf_counter()
    sol_ts, custo_ts, hist_ts = tabu_search(inst, sol_g, max_iter=TABU_ITER,
                                             tenure=TABU_TENURE, semente=semente)
    t_ts = (time.perf_counter() - t0) * 1000

    # --- Etapa 3c: GRASP + Tabu — Cenário 1 (intensificador rápido) ---
    t0 = time.perf_counter()
    sol_gt1, custo_gt1, hist_gt1 = grasp(inst, max_iter=GT1_MAX_ITER,
                                          alpha=GRASP_ALPHA, semente=semente,
                                          busca_local='tabu',
                                          tabu_iter_internas=GT1_TABU_ITER,
                                          tabu_tenure=GT1_TABU_TENURE)
    t_gt1 = (time.perf_counter() - t0) * 1000

    # --- Etapa 3d: GRASP + Tabu — Cenário 2 (intensificador forte) ---
    t0 = time.perf_counter()
    sol_gt2, custo_gt2, hist_gt2 = grasp(inst, max_iter=GT2_MAX_ITER,
                                          alpha=GRASP_ALPHA, semente=semente,
                                          busca_local='tabu',
                                          tabu_iter_internas=GT2_TABU_ITER,
                                          tabu_tenure=GT2_TABU_TENURE)
    t_gt2 = (time.perf_counter() - t0) * 1000

    def mel(base, novo):
        return 100.0 * (base - novo) / base if base > 0 else 0.0

    return {
        'nome'            : inst.get('nome', inst.get('label_tamanho', '?')),
        'label_tamanho'   : inst.get('label_tamanho', inst.get('nome_base', '?')),
        'label_capacidade': inst.get('label_capacidade', '?'),
        'n_produtos'      : inst['n_produtos'],
        'n_maquinas'      : inst['n_maquinas'],
        'alpha'           : inst.get('alpha', '?'),
        'semente'         : semente,
        # custos
        'custo_gulosa'       : round(custo_g,  2),
        'custo_bl'           : round(custo_bl, 2),
        'custo_grasp_vnd'    : round(custo_gv, 2)  if custo_gv  != float('inf') else 'inf',
        'custo_tabu'         : round(custo_ts, 2)  if custo_ts  != float('inf') else 'inf',
        'custo_grasp_tabu1'  : round(custo_gt1, 2) if custo_gt1 != float('inf') else 'inf',
        'custo_grasp_tabu2'  : round(custo_gt2, 2) if custo_gt2 != float('inf') else 'inf',
        # melhoras (% sobre a gulosa)
        'mel_bl_vs_g'         : round(mel(custo_g, custo_bl),  2),
        'mel_graspvnd_vs_g'   : round(mel(custo_g, custo_gv),  2),
        'mel_tabu_vs_g'       : round(mel(custo_g, custo_ts),  2),
        'mel_grasptabu1_vs_g' : round(mel(custo_g, custo_gt1), 2),
        'mel_grasptabu2_vs_g' : round(mel(custo_g, custo_gt2), 2),
        # comparações diretas entre metaheurísticas
        'mel_graspvnd_vs_bl'        : round(mel(custo_bl, custo_gv), 2),
        'mel_graspvnd_vs_tabu'      : round(mel(custo_ts, custo_gv), 2),
        'mel_grasptabu1_vs_graspvnd': round(mel(custo_gv, custo_gt1), 2),
        'mel_grasptabu2_vs_graspvnd': round(mel(custo_gv, custo_gt2), 2),
        'mel_grasptabu2_vs_grasptabu1': round(mel(custo_gt1, custo_gt2), 2),
        # tempos
        't_gulosa_ms'        : round(t_g,   3),
        't_bl_ms'            : round(t_bl,  3),
        't_grasp_vnd_ms'     : round(t_gv,  3),
        't_tabu_ms'          : round(t_ts,  3),
        't_grasp_tabu1_ms'   : round(t_gt1, 3),
        't_grasp_tabu2_ms'   : round(t_gt2, 3),
        # historico convergência
        'historico_grasp_vnd'   : hist_gv,
        'historico_tabu'        : hist_ts,
        'historico_grasp_tabu1' : hist_gt1,
        'historico_grasp_tabu2' : hist_gt2,
        'nao_alocados_g'   : len(nao_aloc),
    }


# ---------------------------------------------------------------------------
# Rodada completa
# ---------------------------------------------------------------------------

def rodar_experimentos(instancias, label_conjunto):
    print(f"\n{'='*100}")
    print(f"  {label_conjunto}  ({len(instancias)} instâncias)")
    print(f"{'='*100}")
    cabecalho = (f"{'Instância':<24} {'C.Gul':>8} {'C.BL':>8} {'GR+VND':>8} {'Tabu':>8} "
                 f"{'GRT1':>8} {'GRT2':>8} {'Mel.GRV%':>8} {'Mel.GT2%':>8}")
    print(cabecalho)
    print('-' * len(cabecalho))

    resultados = []
    for inst in instancias:
        r = executar_instancia(inst)
        resultados.append(r)

        def fmt(v):
            return f"{v:>8.1f}" if v != 'inf' else f"{'inf':>8}"

        print(f"{r['nome']:<24} {r['custo_gulosa']:>8.1f} {r['custo_bl']:>8.1f} "
              f"{fmt(r['custo_grasp_vnd'])} {fmt(r['custo_tabu'])} "
              f"{fmt(r['custo_grasp_tabu1'])} {fmt(r['custo_grasp_tabu2'])} "
              f"{r['mel_graspvnd_vs_g']:>7.1f}% {r['mel_grasptabu2_vs_g']:>7.1f}%")
    return resultados


# ---------------------------------------------------------------------------
# Aggregação por grupo
# ---------------------------------------------------------------------------

def agregar(resultados, chave_fn):
    grupos = defaultdict(list)
    for r in resultados:
        grupos[chave_fn(r)].append(r)
    return grupos


# ---------------------------------------------------------------------------
# CSV
# ---------------------------------------------------------------------------

def salvar_csv(resultados, nome_arquivo):
    campos = [k for k in resultados[0].keys()
              if k not in ('historico_grasp_vnd', 'historico_tabu',
                           'historico_grasp_tabu1', 'historico_grasp_tabu2')]
    caminho = os.path.join(PASTA_OUT, nome_arquivo)
    with open(caminho, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=campos, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(resultados)
    print(f"  • CSV salvo: {caminho}")
    return caminho


# ---------------------------------------------------------------------------
# Gráficos — paleta e tipografia pensadas para apresentação (slide/projetor)
# ---------------------------------------------------------------------------

PLT_STYLE = {
    'font.family'       : 'DejaVu Sans',
    'font.size'         : 13,
    'axes.titlesize'    : 16,
    'axes.labelsize'    : 13,
    'xtick.labelsize'   : 12,
    'ytick.labelsize'   : 12,
    'legend.fontsize'   : 12,
    'axes.spines.top'   : False,
    'axes.spines.right' : False,
    'axes.grid'         : True,
    'grid.alpha'        : 0.30,
    'grid.linestyle'    : '--',
    'axes.edgecolor'    : '#444444',
    'axes.titleweight'  : 'bold',
    'figure.facecolor'  : 'white',
    'savefig.facecolor' : 'white',
}

# Paleta única e consistente em todas as figuras do projeto
COR_GUL         = '#4C72B0'   # azul    — Gulosa (Etapa 1)
COR_BL          = '#DD8452'   # laranja — BL VND (Etapa 2)
COR_GRASP_VND   = '#2CA02C'   # verde   — GRASP + VND
COR_TABU        = '#C44E52'   # vermelho — Tabu pura
COR_GRASP_TABU1 = '#8172B2'   # roxo    — GRASP + Tabu (cenário 1: intensif. rápido)
COR_GRASP_TABU2 = '#CCB974'   # dourado — GRASP + Tabu (cenário 2: intensif. forte)

ABORD_CORES = {
    'Gulosa'         : COR_GUL,
    'BL VND'         : COR_BL,
    'GRASP+VND'      : COR_GRASP_VND,
    'Tabu'           : COR_TABU,
    'GRASP+Tabu (C1)': COR_GRASP_TABU1,
    'GRASP+Tabu (C2)': COR_GRASP_TABU2,
}


def _aplicar_estilo():
    plt.rcParams.update(PLT_STYLE)


def _salvar(fig, nome_fig):
    caminho = os.path.join(PASTA_OUT, nome_fig)
    fig.savefig(caminho, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  • {caminho}")


# ---------------------------------------------------------------------------
# Figura 1/2 — Comparação das 5 abordagens (custo médio por grupo)
# ---------------------------------------------------------------------------

def _fig_comparacao_6(resultados, nome_fig, titulo, chave_label):
    if not MPL_OK:
        return
    _aplicar_estilo()

    grupos = defaultdict(list)
    for r in resultados:
        grupos[chave_label(r)].append(r)
    labels = list(grupos.keys())

    def media(campo):
        out = []
        for l in labels:
            vals = [r[campo] for r in grupos[l] if r[campo] != 'inf']
            out.append(sum(vals) / len(vals) if vals else 0)
        return out

    series = [
        ('Gulosa',          media('custo_gulosa'),      COR_GUL),
        ('BL VND',          media('custo_bl'),          COR_BL),
        ('GRASP+VND',       media('custo_grasp_vnd'),   COR_GRASP_VND),
        ('Tabu',            media('custo_tabu'),        COR_TABU),
        ('GRASP+Tabu (C1)', media('custo_grasp_tabu1'), COR_GRASP_TABU1),
        ('GRASP+Tabu (C2)', media('custo_grasp_tabu2'), COR_GRASP_TABU2),
    ]

    n_series = len(series)
    larg = 0.84 / n_series
    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(max(14, len(labels) * 1.7), 6.5))
    for idx, (nome, vals, cor) in enumerate(series):
        offset = (idx - (n_series - 1) / 2) * larg
        ax.bar(x + offset, vals, larg, label=nome, color=cor,
               edgecolor='white', linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha='right')
    ax.set_ylabel('Custo médio da solução')
    ax.set_title(titulo, pad=14)
    ax.legend(ncol=3, loc='upper center', bbox_to_anchor=(0.5, -0.22), frameon=False)
    fig.tight_layout()
    _salvar(fig, nome_fig)


# ---------------------------------------------------------------------------
# Figura 3/4 — Convergência (GRASP+VND vs GRASP+Tabu vs Tabu pura)
# ---------------------------------------------------------------------------

def _fig_convergencia_comparativa(resultados, nome_fig, titulo, n_amostras=4):
    """
    Para cada instância amostrada, plota a curva de convergência das três
    variantes do GRASP: GRASP+VND, GRASP+Tabu (cenário 1 — intensificador
    rápido) e GRASP+Tabu (cenário 2 — intensificador forte). Como o cenário
    2 usa menos iterações externas (GT2_MAX_ITER), seu eixo X é mais curto.

    Prioriza instâncias de tamanho médio/grande, que mostram curvas de
    convergência mais informativas que as pequenas (que tendem a saturar
    em poucas iterações).
    """
    if not MPL_OK:
        return
    _aplicar_estilo()

    candidatas = [r for r in resultados if r.get('label_tamanho') in ('Media', 'Grande')]
    if len(candidatas) < n_amostras:
        candidatas = resultados
    amostras = candidatas[:n_amostras]

    n = len(amostras)
    fig, axes = plt.subplots(1, n, figsize=(5.4 * n, 4.8), sharey=True)
    if n == 1:
        axes = [axes]

    for ax, r in zip(axes, amostras):
        def serie(hist):
            iters  = [h['iteracao']     for h in hist]
            melhor = [h['melhor_custo'] for h in hist]
            base = melhor[0] if melhor and melhor[0] != float('inf') else 1
            norm = [v / base * 100 if v != float('inf') else 100 for v in melhor]
            return iters, norm

        it_v, norm_v   = serie(r['historico_grasp_vnd'])
        it_t1, norm_t1 = serie(r['historico_grasp_tabu1'])
        it_t2, norm_t2 = serie(r['historico_grasp_tabu2'])

        ax.plot(it_v,  norm_v,  color=COR_GRASP_VND,   linewidth=2.2, label='GRASP+VND')
        ax.plot(it_t1, norm_t1, color=COR_GRASP_TABU1, linewidth=2.2, label='GRASP+Tabu (C1)')
        ax.plot(it_t2, norm_t2, color=COR_GRASP_TABU2, linewidth=2.4, label='GRASP+Tabu (C2)')
        ax.set_title(r['nome'][:22], fontsize=13)
        ax.set_xlabel('Iteração GRASP (externa)')

    axes[0].set_ylabel('Custo relativo ao inicial (%)')
    handles, lbls = axes[0].get_legend_handles_labels()
    fig.legend(handles, lbls, ncol=3, loc='upper center',
               bbox_to_anchor=(0.5, 1.1), frameon=False, fontsize=13)
    fig.suptitle(titulo, y=1.2, fontsize=16, fontweight='bold')
    fig.tight_layout()
    _salvar(fig, nome_fig)


def _fig_convergencia_tabu(resultados, nome_fig):
    """Curva de convergência da Busca Tabu pura (melhor custo por iteração)."""
    if not MPL_OK:
        return
    _aplicar_estilo()
    fig, ax = plt.subplots(figsize=(10, 5.5))

    candidatas = [r for r in resultados if r.get('label_tamanho') in ('Media', 'Grande')]
    if len(candidatas) < 5:
        candidatas = resultados
    amostras = candidatas[:5]

    cores_linha = plt.cm.Reds(np.linspace(0.4, 0.9, len(amostras)))
    for r, cor in zip(amostras, cores_linha):
        hist = r['historico_tabu']
        iters  = [h['iteracao']     for h in hist]
        melhor = [h['melhor_custo'] for h in hist]
        base = melhor[0] if melhor and melhor[0] != float('inf') else 1
        norm = [v / base * 100 if v != float('inf') else 100 for v in melhor]
        ax.plot(iters, norm, linewidth=2, alpha=0.85, color=cor, label=r['nome'][:20])

    ax.set_xlabel('Iteração Tabu')
    ax.set_ylabel('Custo relativo ao inicial (%)')
    ax.set_title('Convergência da Busca Tabu (pura)', pad=14)
    ax.legend(fontsize=10, loc='upper right', frameon=False)
    fig.tight_layout()
    _salvar(fig, nome_fig)


# ---------------------------------------------------------------------------
# Figura 5 — Comparação direta GRASP+VND vs Tabu pura
# ---------------------------------------------------------------------------

def _fig_comparacao_direta(res_sint, res_orlib, nome_fig, campo, titulo,
                            cor_pos, cor_neg, label_pos, label_neg, xlabel):
    """
    Gráfico de barras horizontais genérico para comparar duas abordagens.
    `campo` é o nome do campo de melhora percentual já calculado no dict
    de resultados (positivo favorece a primeira abordagem do par).
    """
    if not MPL_OK:
        return
    _aplicar_estilo()

    def med_grupo(resultados, chave_fn):
        grupos = defaultdict(list)
        for r in resultados:
            grupos[chave_fn(r)].append(r)
        return {k: sum(r[campo] for r in v) / len(v) for k, v in grupos.items()}

    med_s = med_grupo(res_sint,  lambda r: f"Sint {r['label_tamanho'][:3]}/{r['label_capacidade'][:2]}")
    med_o = med_grupo(res_orlib, lambda r: f"OR-Lib {r['label_tamanho']}/{r['label_capacidade'][:2]}")

    labels = list(med_s.keys()) + list(med_o.keys())
    vals   = list(med_s.values()) + list(med_o.values())
    cores  = [cor_pos if v >= 0 else cor_neg for v in vals]

    fig, ax = plt.subplots(figsize=(9.5, max(5, len(labels) * 0.5)))
    bars = ax.barh(labels, vals, color=cores, edgecolor='white', alpha=0.9)
    for bar, val in zip(bars, vals):
        desloc = 0.25 if val >= 0 else -0.25
        ha = 'left' if val >= 0 else 'right'
        ax.text(bar.get_width() + desloc, bar.get_y() + bar.get_height() / 2,
                f'{val:.1f}%', va='center', ha=ha, fontsize=10)
    ax.axvline(0, color='#444444', linewidth=1)
    ax.set_xlabel(xlabel)
    ax.set_title(titulo, pad=14)
    leg = [mpatches.Patch(color=cor_pos, label=label_pos),
           mpatches.Patch(color=cor_neg, label=label_neg)]
    ax.legend(handles=leg, frameon=False, loc='lower right')
    fig.tight_layout()
    _salvar(fig, nome_fig)


# ---------------------------------------------------------------------------
# Resumo no terminal
# ---------------------------------------------------------------------------

def resumo(resultados, label):
    total = len(resultados)

    v_gv  = [r['mel_graspvnd_vs_g']   for r in resultados if r['custo_grasp_vnd']   != 'inf']
    v_ts  = [r['mel_tabu_vs_g']       for r in resultados if r['custo_tabu']        != 'inf']
    v_gt1 = [r['mel_grasptabu1_vs_g'] for r in resultados if r['custo_grasp_tabu1'] != 'inf']
    v_gt2 = [r['mel_grasptabu2_vs_g'] for r in resultados if r['custo_grasp_tabu2'] != 'inf']

    v_gv_bl  = [r['mel_graspvnd_vs_bl']         for r in resultados if r['custo_grasp_vnd']   != 'inf']
    v_gv_ts  = [r['mel_graspvnd_vs_tabu']       for r in resultados if r['custo_grasp_vnd']   != 'inf']
    v_gt1_gv = [r['mel_grasptabu1_vs_graspvnd'] for r in resultados if r['custo_grasp_tabu1'] != 'inf']
    v_gt2_gv = [r['mel_grasptabu2_vs_graspvnd'] for r in resultados if r['custo_grasp_tabu2'] != 'inf']
    v_gt2_gt1 = [r['mel_grasptabu2_vs_grasptabu1'] for r in resultados if r['custo_grasp_tabu2'] != 'inf']

    t_gv  = [r['t_grasp_vnd_ms']   for r in resultados]
    t_ts  = [r['t_tabu_ms']        for r in resultados]
    t_gt1 = [r['t_grasp_tabu1_ms'] for r in resultados]
    t_gt2 = [r['t_grasp_tabu2_ms'] for r in resultados]

    print(f"\n  [{label}]  {total} instâncias")
    print(f"  Melhora GRASP+VND        vs Gulosa  — média: {sum(v_gv)/len(v_gv):.2f}%   máx: {max(v_gv):.2f}%")
    print(f"  Melhora Tabu pura        vs Gulosa  — média: {sum(v_ts)/len(v_ts):.2f}%   máx: {max(v_ts):.2f}%")
    print(f"  Melhora GRASP+Tabu (C1)  vs Gulosa  — média: {sum(v_gt1)/len(v_gt1):.2f}%   máx: {max(v_gt1):.2f}%")
    print(f"  Melhora GRASP+Tabu (C2)  vs Gulosa  — média: {sum(v_gt2)/len(v_gt2):.2f}%   máx: {max(v_gt2):.2f}%")
    print(f"  GRASP+VND  vs BL VND                — média: {sum(v_gv_bl)/len(v_gv_bl):.2f}%")
    print(f"  GRASP+VND  vs Tabu pura             — média: {sum(v_gv_ts)/len(v_gv_ts):.2f}%  (>0 favorece GRASP+VND)")
    print(f"  GRASP+Tabu (C1) vs GRASP+VND        — média: {sum(v_gt1_gv)/len(v_gt1_gv):.2f}%  (>0 favorece C1)")
    print(f"  GRASP+Tabu (C2) vs GRASP+VND        — média: {sum(v_gt2_gv)/len(v_gt2_gv):.2f}%  (>0 favorece C2)")
    print(f"  GRASP+Tabu (C2) vs GRASP+Tabu (C1)  — média: {sum(v_gt2_gt1)/len(v_gt2_gt1):.2f}%  (>0 favorece C2)")
    print(f"  Tempo médio (ms) — GRASP+VND: {sum(t_gv)/len(t_gv):.1f}  Tabu: {sum(t_ts)/len(t_ts):.1f}  "
          f"GRASP+Tabu(C1): {sum(t_gt1)/len(t_gt1):.1f}  GRASP+Tabu(C2): {sum(t_gt2)/len(t_gt2):.1f}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    print("GQAP — Etapa 3: GRASP, Busca Tabu e GRASP+Tabu (dois cenários)")
    print(f"GRASP+VND      : {GRASP_ITER} iter. externas, alpha={GRASP_ALPHA}")
    print(f"Tabu pura      : {TABU_ITER} iterações, tenure={TABU_TENURE}")
    print(f"GRASP+Tabu (C1): {GT1_MAX_ITER} iter. externas x {GT1_TABU_ITER} iter. "
          f"internas (tenure={GT1_TABU_TENURE}) — intensificador rápido, muitas reconstruções")
    print(f"GRASP+Tabu (C2): {GT2_MAX_ITER} iter. externas x {GT2_TABU_ITER} iter. "
          f"internas (tenure={GT2_TABU_TENURE}) — intensificador forte, poucas reconstruções")

    # ── Instâncias sintéticas ────────────────────────────────────────────────
    inst_sint   = gerar_conjunto_instancias()
    res_sint    = rodar_experimentos(inst_sint,  "INSTÂNCIAS SINTÉTICAS")

    # ── Instâncias OR-Library ────────────────────────────────────────────────
    inst_orlib  = gerar_instancias_orlib()
    res_orlib   = rodar_experimentos(inst_orlib, "INSTÂNCIAS OR-LIBRARY (QAPLIB adaptadas)")

    # ── Salva CSVs ───────────────────────────────────────────────────────────
    print("\nSALVANDO CSVs")
    salvar_csv(res_sint,   'experimento3_sinteticas.csv')
    salvar_csv(res_orlib,  'experimento3_orlib.csv')

    # ── Gráficos ─────────────────────────────────────────────────────────────
    print("\nGERANDO GRÁFICOS")
    _fig_comparacao_6(
        res_sint,
        'fig1_comparacao_6abordagens_sinteticas.png',
        'Gulosa → BL VND → GRASP+VND → Tabu → GRASP+Tabu (C1/C2) — Sintéticas',
        lambda r: f"{r['label_tamanho'][:3]}/{r['label_capacidade'][:2]}",
    )
    _fig_comparacao_6(
        res_orlib,
        'fig2_comparacao_6abordagens_orlib.png',
        'Gulosa → BL VND → GRASP+VND → Tabu → GRASP+Tabu (C1/C2) — OR-Library',
        lambda r: f"{r['label_tamanho']}/{r['label_capacidade'][:2]}",
    )
    _fig_convergencia_comparativa(
        res_sint, 'fig3_convergencia_grasp_sinteticas.png',
        'Convergência: GRASP+VND vs GRASP+Tabu (C1 e C2) — Sintéticas',
    )
    _fig_convergencia_tabu(res_sint, 'fig4_convergencia_tabu_sinteticas.png')

    _fig_comparacao_direta(
        res_sint, res_orlib, 'fig5_grasp_vnd_vs_tabu.png',
        campo='mel_graspvnd_vs_tabu',
        titulo='Comparação direta: GRASP+VND vs Busca Tabu (pura)',
        cor_pos=COR_GRASP_VND, cor_neg=COR_TABU,
        label_pos='GRASP+VND melhor', label_neg='Tabu melhor',
        xlabel='GRASP+VND melhor que Tabu (%)  →  positivo favorece GRASP+VND',
    )
    _fig_comparacao_direta(
        res_sint, res_orlib, 'fig6_grasp_vnd_vs_grasp_tabu_c1.png',
        campo='mel_grasptabu1_vs_graspvnd',
        titulo='GRASP+Tabu (C1: intensif. rápido) vs GRASP+VND',
        cor_pos=COR_GRASP_TABU1, cor_neg=COR_GRASP_VND,
        label_pos='GRASP+Tabu (C1) melhor', label_neg='GRASP+VND melhor',
        xlabel='GRASP+Tabu(C1) melhor que GRASP+VND (%)  →  positivo favorece C1',
    )
    _fig_comparacao_direta(
        res_sint, res_orlib, 'fig7_grasp_vnd_vs_grasp_tabu_c2.png',
        campo='mel_grasptabu2_vs_graspvnd',
        titulo='GRASP+Tabu (C2: intensif. forte) vs GRASP+VND',
        cor_pos=COR_GRASP_TABU2, cor_neg=COR_GRASP_VND,
        label_pos='GRASP+Tabu (C2) melhor', label_neg='GRASP+VND melhor',
        xlabel='GRASP+Tabu(C2) melhor que GRASP+VND (%)  →  positivo favorece C2',
    )
    _fig_comparacao_direta(
        res_sint, res_orlib, 'fig8_grasp_tabu_c1_vs_c2.png',
        campo='mel_grasptabu2_vs_grasptabu1',
        titulo='GRASP+Tabu: Cenário 2 (forte) vs Cenário 1 (rápido)',
        cor_pos=COR_GRASP_TABU2, cor_neg=COR_GRASP_TABU1,
        label_pos='Cenário 2 melhor', label_neg='Cenário 1 melhor',
        xlabel='C2 melhor que C1 (%)  →  positivo favorece intensificador forte (C2)',
    )

    # ── Resumo ───────────────────────────────────────────────────────────────
    print("\nRESUMO GERAL")
    resumo(res_sint,  "Sintéticas")
    resumo(res_orlib, "OR-Library")
    print("\nConcluído. Arquivos salvos em result3/")
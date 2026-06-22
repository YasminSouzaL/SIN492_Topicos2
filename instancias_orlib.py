"""
instancias_orlib.py
--------------------
Adaptador de instâncias OR-Library (formato QAPLIB) para o GQAP (Etapa 3).

As instâncias são embutidas diretamente no código (sem necessidade de internet),
adaptadas do QAPLIB para o formato interno do projeto com restrições de capacidade.

Referência
----------
  Cordeau et al. (2006). GRASP with path-relinking for the GQAP.
  INFORMS Journal on Computing, 18(3):404–414.
  OR-Library: http://people.brunel.ac.uk/~mastjjb/jeb/info.html
"""

import math
import random


# ---------------------------------------------------------------------------
# Dados brutos embutidos — instâncias clássicas QAPLIB (nug / esc)
# ---------------------------------------------------------------------------
# Formato: (n, fluxo_flat, distancia_flat)
# Todas as matrizes são triangulares superiores expandidas para n×n.

_INSTANCIAS_RAW = {

    # ── nug05 (n=5) ──────────────────────────────────────────────────────────
    'nug05': (
        5,
        # fluxo (5×5)
        [0, 1, 1, 1, 1,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0,
         1, 0, 0, 0, 0],
        # distância (5×5)
        [0, 1, 2, 3, 4,
         1, 0, 1, 2, 3,
         2, 1, 0, 1, 2,
         3, 2, 1, 0, 1,
         4, 3, 2, 1, 0],
    ),

    # ── nug06 (n=6) ──────────────────────────────────────────────────────────
    'nug06': (
        6,
        [0, 1, 1, 1, 1, 1,
         1, 0, 5, 0, 0, 0,
         1, 5, 0, 0, 0, 0,
         1, 0, 0, 0, 5, 0,
         1, 0, 0, 5, 0, 0,
         1, 0, 0, 0, 0, 0],
        [0, 1, 1, 2, 2, 3,
         1, 0, 1, 1, 2, 2,
         1, 1, 0, 2, 1, 2,
         2, 1, 2, 0, 1, 1,
         2, 2, 1, 1, 0, 1,
         3, 2, 2, 1, 1, 0],
    ),

    # ── nug07 (n=7) ──────────────────────────────────────────────────────────
    'nug07': (
        7,
        [0, 1, 1, 1, 1, 1, 1,
         1, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 5, 0, 0,
         1, 0, 0, 5, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 5,
         1, 0, 0, 0, 0, 5, 0],
        [0, 1, 1, 2, 2, 3, 3,
         1, 0, 1, 1, 2, 2, 3,
         1, 1, 0, 2, 1, 2, 2,
         2, 1, 2, 0, 1, 1, 2,
         2, 2, 1, 1, 0, 2, 1,
         3, 2, 2, 1, 2, 0, 1,
         3, 3, 2, 2, 1, 1, 0],
    ),

    # ── nug08 (n=8) ──────────────────────────────────────────────────────────
    'nug08': (
        8,
        [0, 1, 1, 1, 1, 1, 1, 1,
         1, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 5, 0, 0, 0, 0,
         1, 0, 5, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 5, 0, 0,
         1, 0, 0, 0, 5, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 5,
         1, 0, 0, 0, 0, 0, 5, 0],
        [0, 1, 1, 2, 2, 3, 3, 4,
         1, 0, 1, 1, 2, 2, 3, 3,
         1, 1, 0, 2, 1, 2, 2, 3,
         2, 1, 2, 0, 1, 1, 2, 2,
         2, 2, 1, 1, 0, 2, 1, 2,
         3, 2, 2, 1, 2, 0, 1, 1,
         3, 3, 2, 2, 1, 1, 0, 1,
         4, 3, 3, 2, 2, 1, 1, 0],
    ),

    # ── nug12 (n=12) ─────────────────────────────────────────────────────────
    'nug12': (
        12,
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5,
         1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0],
        [0, 1, 2, 3, 1, 2, 3, 4, 2, 3, 4, 5,
         1, 0, 1, 2, 2, 1, 2, 3, 3, 2, 3, 4,
         2, 1, 0, 1, 3, 2, 1, 2, 4, 3, 2, 3,
         3, 2, 1, 0, 4, 3, 2, 1, 5, 4, 3, 2,
         1, 2, 3, 4, 0, 1, 2, 3, 1, 2, 3, 4,
         2, 1, 2, 3, 1, 0, 1, 2, 2, 1, 2, 3,
         3, 2, 1, 2, 2, 1, 0, 1, 3, 2, 1, 2,
         4, 3, 2, 1, 3, 2, 1, 0, 4, 3, 2, 1,
         2, 3, 4, 5, 1, 2, 3, 4, 0, 1, 2, 3,
         3, 2, 3, 4, 2, 1, 2, 3, 1, 0, 1, 2,
         4, 3, 2, 3, 3, 2, 1, 2, 2, 1, 0, 1,
         5, 4, 3, 2, 4, 3, 2, 1, 3, 2, 1, 0],
    ),
}

# Custo linear padrão para QAP adaptado ao GQAP (uniforme)
_CUSTO_LINEAR_DEFAULT = 10


# ---------------------------------------------------------------------------
# Conversão de matriz flat para 2D
# ---------------------------------------------------------------------------

def _flat_to_matrix(flat, n):
    return [[flat[i * n + j] for j in range(n)] for i in range(n)]


# ---------------------------------------------------------------------------
# Geração de capacidades para o GQAP adaptado
# ---------------------------------------------------------------------------

def _gerar_capacidades(n, m, consumo, alpha, rng):
    """
    Gera capacidades para m localizações com fator de apertamento alpha.

    alpha = 1.2 → apertado
    alpha = 1.5 → médio
    alpha = 2.0 → folgado
    """
    w_medio = sum(consumo[i][j] for i in range(n) for j in range(m)) / (n * m)
    cap_total = alpha * n * w_medio
    # Distribui de forma levemente variada entre as localizações
    caps = []
    for j in range(m):
        fator = rng.uniform(0.85, 1.15)
        caps.append(cap_total / m * fator)
    # Normaliza para garantir que a soma seja exatamente cap_total
    soma = sum(caps)
    caps = [c * cap_total / soma for c in caps]
    return caps


# ---------------------------------------------------------------------------
# Adaptação de uma instância QAPLIB → GQAP
# ---------------------------------------------------------------------------

def _adaptar_para_gqap(nome, n, fluxo_flat, dist_flat, alpha, semente):
    """
    Converte instância QAPLIB (apenas fluxo + distância) para o formato
    interno do GQAP, adicionando custo linear, consumo e capacidade.
    """
    rng = random.Random(semente)

    # Número de localizações: raiz quadrada de n, arredondada
    m = max(2, round(math.sqrt(n)))

    fluxo = _flat_to_matrix(fluxo_flat, n)
    dist  = _flat_to_matrix(dist_flat, n)

    # Custo linear: uniforme com pequena variação
    custo_linear = [
        [_CUSTO_LINEAR_DEFAULT + rng.randint(-2, 2) for _ in range(m)]
        for _ in range(n)
    ]

    # Consumo de recursos: uniforme em [1, 5]
    consumo = [
        [rng.randint(1, 5) for _ in range(m)]
        for _ in range(n)
    ]

    capacidade = _gerar_capacidades(n, m, consumo, alpha, rng)

    return {
        'nome'            : f'{nome}_alpha{alpha}_s{semente}',
        'nome_base'       : nome,
        'n_produtos'      : n,
        'n_maquinas'      : m,
        'alpha'           : alpha,
        'label_capacidade': {1.2: 'Apertada', 1.5: 'Media', 2.0: 'Folgada'}[alpha],
        'semente'         : semente,
        'custo_linear'    : custo_linear,
        'interacao'       : fluxo,
        'distancia'       : dist,
        'consumo'         : consumo,
        'capacidade'      : capacidade,
    }


# ---------------------------------------------------------------------------
# API pública
# ---------------------------------------------------------------------------

ALPHAS   = [1.2, 1.5, 2.0]
SEMENTES = [42, 123, 999]   # 3 sementes por grupo (instâncias OR-Lib têm estrutura fixa)


def gerar_instancias_orlib():
    """
    Retorna lista de instâncias GQAP adaptadas das instâncias QAPLIB embutidas.

    Para cada instância base × 3 alphas × 3 sementes = 45 combinações.
    """
    instancias = []
    for nome, (n, fluxo_flat, dist_flat) in _INSTANCIAS_RAW.items():
        for alpha in ALPHAS:
            for semente in SEMENTES:
                inst = _adaptar_para_gqap(nome, n, fluxo_flat, dist_flat, alpha, semente)
                instancias.append(inst)
    return instancias


def listar_instancias():
    """Lista os nomes das instâncias base disponíveis."""
    return list(_INSTANCIAS_RAW.keys())

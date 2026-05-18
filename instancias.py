"""
instancias.py
-------------
Gerador de instâncias sintéticas reproducíveis para o GQAP simplificado.

Estrutura da instância (dict)
-----------------------------
  n_produtos  : int          – número de produtos
  n_maquinas  : int          – número de máquinas
  custo_linear: list[n][m]   – f[i][j]: custo de alocar produto i em máquina j
  interacao   : list[n][n]   – inter[i][k]: peso de interação entre produtos i e k
  distancia   : list[m][m]   – dist[j][l]: distância entre máquinas j e l
  consumo     : list[n][m]   – b[i][j]: recurso consumido por produto i em máquina j
  capacidade  : list[m]      – c[j]: capacidade total da máquina j

Parâmetro alpha (aperto de capacidade)
---------------------------------------
  alpha perto de 1  → capacidade apertada (difícil alocar tudo)
  alpha perto de 2  → capacidade folgada  (fácil alocar tudo)
"""

import random


def gerar_instancia(n_produtos, n_maquinas, alpha=1.5, semente=42):
    """
    Gera uma instância sintética reproducível do GQAP.

    Parâmetros
    ----------
    n_produtos : int   – número de produtos
    n_maquinas : int   – número de máquinas
    alpha      : float – fator de capacidade (1.0 = muito apertado, 2.0 = folgado)
    semente    : int   – semente do gerador para reproducibilidade

    Retorna
    -------
    dict com todos os dados da instância
    """
    rng = random.Random(semente)
    n, m = n_produtos, n_maquinas

    # Custo linear f[i][j] ∈ [1, 100]
    custo_linear = [[rng.randint(1, 100) for _ in range(m)] for _ in range(n)]

    # Interação inter[i][k] = inter[k][i] ∈ [0, 50], diagonal = 0
    interacao = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for k in range(i + 1, n):
            v = rng.randint(0, 50)
            interacao[i][k] = v
            interacao[k][i] = v

    # Distância dist[j][l] = dist[l][j] ∈ [1, 20], diagonal = 0
    distancia = [[0.0] * m for _ in range(m)]
    for j in range(m):
        for l in range(j + 1, m):
            v = rng.randint(1, 20)
            distancia[j][l] = v
            distancia[l][j] = v

    # Consumo b[i][j] ∈ [1, 10]
    consumo = [[rng.randint(1, 10) for _ in range(m)] for _ in range(n)]

    # Capacidade: alpha × (consumo médio por máquina se produtos distribuídos uniformemente)
    # Usa a média de consumo de cada produto (não o mínimo) para uma estimativa mais realista.
    consumo_medio_produto = sum(
        sum(consumo[i]) / m for i in range(n)
    )
    # Demanda média por máquina se distribuição for uniforme
    demanda_por_maquina = consumo_medio_produto / m
    cap_base = alpha * demanda_por_maquina
    variacao = cap_base * 0.1
    capacidade = [
        max(1, int(cap_base + rng.uniform(-variacao, variacao)))
        for _ in range(m)
    ]

    return {
        'n_produtos' : n,
        'n_maquinas' : m,
        'custo_linear': custo_linear,
        'interacao'  : interacao,
        'distancia'  : distancia,
        'consumo'    : consumo,
        'capacidade' : capacidade,
        'alpha'      : alpha,
        'semente'    : semente,
    }


def gerar_conjunto_instancias():
    """
    Gera 45 instâncias cobrindo 3 tamanhos × 3 alphas × 5 sementes.

    Retorna lista de dicts, cada um com os dados da instância e metadados.
    """
    configuracoes = [
        # (n_produtos, n_maquinas, label_tamanho)
        (10,  5,  'Pequena'),
        (20,  8,  'Media'  ),
        (40, 12,  'Grande' ),
    ]
    alphas = [
        (1.2, 'Apertada'),
        (1.5, 'Media'   ),
        (2.0, 'Folgada' ),
    ]
    sementes = [42, 123, 256, 512, 999]

    instancias = []
    for n, m, label_tam in configuracoes:
        for alpha, label_cap in alphas:
            for s in sementes:
                inst = gerar_instancia(n, m, alpha=alpha, semente=s)
                inst['label_tamanho']   = label_tam
                inst['label_capacidade'] = label_cap
                instancias.append(inst)

    return instancias

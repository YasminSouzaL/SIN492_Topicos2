# ---------------------------------------------------------------------------
# Avaliação da função objetivo
# ---------------------------------------------------------------------------

def calcular_custo(solucao, instancia):
    """
    Calcula o custo total (linear + quadrático) de uma solução.

    Parâmetros
    ----------
    solucao  : list[int]  – s[i] = índice da máquina do produto i (-1 = não alocado)
    instancia: dict       – dicionário com os dados do problema

    Retorna
    -------
    float : custo total da solução
    """
    n     = instancia['n_produtos']
    f     = instancia['custo_linear']
    inter = instancia['interacao']
    dist  = instancia['distancia']

    custo = 0.0

    # Custo linear
    for i in range(n):
        if solucao[i] >= 0:
            custo += f[i][solucao[i]]

    # Custo quadrático (pares ordenados i < k, contados uma vez cada)
    for i in range(n):
        for k in range(i + 1, n):
            if solucao[i] >= 0 and solucao[k] >= 0:
                custo += inter[i][k] * dist[solucao[i]][solucao[k]]

    return custo


def eh_viavel(solucao, instancia):
    """Verifica se a solução respeita todas as restrições de capacidade."""
    m        = instancia['n_maquinas']
    consumo  = instancia['consumo']
    cap      = instancia['capacidade']

    uso = [0.0] * m
    for i, j in enumerate(solucao):
        if j >= 0:
            uso[j] += consumo[i][j]

    return all(uso[j] <= cap[j] for j in range(m))


# ---------------------------------------------------------------------------
# Heurística construtiva gulosa
# ---------------------------------------------------------------------------

def heuristica_gulosa(instancia):
    """
    Constrói uma solução gulosa para o GQAP.

    Estratégia
    ----------
    A cada passo seleciona-se o produto ainda não alocado cujo custo
    mínimo de atribuição (mín sobre j) é o mais alto — ou seja, o produto
    mais "caro" de alocar tem prioridade.  Para cada candidato de máquina
    avalia-se o custo incremental total:

        Δ(i, j) = f[i][j] + Σₖ∈alocados inter[i][k] · dist[j][s[k]]

    e escolhe-se a máquina que minimiza Δ, desde que a capacidade permita.

    Complexidade
    ------------
    O(n² · m)  —  n iterações × m máquinas × n produtos já alocados.

    Parâmetros
    ----------
    instancia : dict  – gerado por instancias.py

    Retorna
    -------
    solucao    : list[int]  – s[i] = máquina do produto i
    custo_total: float      – valor da função objetivo
    nao_alocados: list[int] – produtos que não couberam em nenhuma máquina
    """
    n       = instancia['n_produtos']
    m       = instancia['n_maquinas']
    f       = instancia['custo_linear']
    inter   = instancia['interacao']
    dist    = instancia['distancia']
    consumo = instancia['consumo']
    cap     = instancia['capacidade']

    solucao      = [-1] * n
    cap_restante = cap[:]
    nao_alocados = []

    # Ordena produtos do mais caro para o mais barato (custo linear mínimo)
    # Produtos mais difíceis de alocar têm prioridade
    ordem = sorted(range(n), key=lambda i: -min(f[i]))

    for i in ordem:
        melhor_maquina = -1
        melhor_delta   = float('inf')

        for j in range(m):
            # Verifica viabilidade de capacidade
            if consumo[i][j] > cap_restante[j]:
                continue

            # Custo linear
            delta = f[i][j]

            # Custo quadrático incremental com produtos já alocados
            for k in range(n):
                if solucao[k] >= 0:
                    delta += inter[i][k] * dist[j][solucao[k]]

            if delta < melhor_delta:
                melhor_delta   = delta
                melhor_maquina = j

        if melhor_maquina >= 0:
            solucao[i] = melhor_maquina
            cap_restante[melhor_maquina] -= consumo[i][melhor_maquina]
        else:
            nao_alocados.append(i)

    custo_total = calcular_custo(solucao, instancia)
    return solucao, custo_total, nao_alocados

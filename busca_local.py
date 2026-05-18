
from heuristica import calcular_custo

# Utilitários internos
def _capacidade_usada(solucao, instancia):
    """Retorna vetor com capacidade consumida por máquina."""
    m       = instancia['n_maquinas']
    consumo = instancia['consumo']
    uso = [0.0] * m
    for i, j in enumerate(solucao):
        if j >= 0:
            uso[j] += consumo[i][j]
    return uso


def _delta_relocate(i, j_novo, solucao, instancia):
    """
    Calcula a variação de custo ao mover o produto i para a máquina j_novo.
    Retorna (delta, viavel).

    delta < 0  →  movimento melhora a solução
    """
    n       = instancia['n_produtos']
    f       = instancia['custo_linear']
    inter   = instancia['interacao']
    dist    = instancia['distancia']
    consumo = instancia['consumo']
    cap     = instancia['capacidade']

    j_atual = solucao[i]
    if j_novo == j_atual:
        return 0.0, False

    # --- Verifica viabilidade ---
    # Capacidade restante em j_novo após mover i
    uso = _capacidade_usada(solucao, instancia)
    cap_j_novo_restante = cap[j_novo] - uso[j_novo]
    if consumo[i][j_novo] > cap_j_novo_restante:
        return float('inf'), False

    # --- Variação no custo linear ---
    delta = f[i][j_novo] - f[i][j_atual]

    # --- Variação no custo quadrático ---
    for k in range(n):
        if k == i or solucao[k] < 0:
            continue
        jk = solucao[k]
        # Perde interação antiga (i em j_atual com k em jk)
        delta -= inter[i][k] * dist[j_atual][jk]
        # Ganha interação nova (i em j_novo com k em jk)
        delta += inter[i][k] * dist[j_novo][jk]

    return delta, True


def _delta_swap(i, k, solucao, instancia):
    """
    Calcula a variação de custo ao trocar as máquinas dos produtos i e k.
    Retorna (delta, viavel).
    """
    n       = instancia['n_produtos']
    f       = instancia['custo_linear']
    inter   = instancia['interacao']
    dist    = instancia['distancia']
    consumo = instancia['consumo']
    cap     = instancia['capacidade']

    ji = solucao[i]
    jk = solucao[k]

    if ji == jk:
        return 0.0, False

    # --- Verifica viabilidade (capacidade) ---
    uso = _capacidade_usada(solucao, instancia)

    # i vai para jk: libera consumo[i][ji] em ji, consome consumo[i][jk] em jk
    cap_jk_apos = cap[jk] - uso[jk] + consumo[k][jk] - consumo[i][jk]
    cap_ji_apos = cap[ji] - uso[ji] + consumo[i][ji] - consumo[k][ji]

    if cap_jk_apos < 0 or cap_ji_apos < 0:
        return float('inf'), False

    # --- Variação no custo linear ---
    delta  = f[i][jk] - f[i][ji]
    delta += f[k][ji] - f[k][jk]

    # --- Variação no custo quadrático ---
    for p in range(n):
        if p == i or p == k or solucao[p] < 0:
            continue
        jp = solucao[p]
        # Produto p com produto i
        delta -= inter[i][p] * dist[ji][jp]
        delta += inter[i][p] * dist[jk][jp]
        # Produto p com produto k
        delta -= inter[k][p] * dist[jk][jp]
        delta += inter[k][p] * dist[ji][jp]

    # Interação entre i e k si mesmos
    delta -= inter[i][k] * dist[ji][jk]
    delta += inter[i][k] * dist[jk][ji]

    return delta, True



# Vizinhanças
def vizinhanca_relocate(solucao, instancia, eps=1e-9):
    solucao      = solucao[:]
    n            = instancia['n_produtos']
    m            = instancia['n_maquinas']
    custo_atual  = calcular_custo(solucao, instancia)
    n_iteracoes  = 0
    melhorou     = True

    while melhorou:
        melhorou        = False
        melhor_delta    = -eps
        melhor_i        = -1
        melhor_j        = -1

        for i in range(n):
            if solucao[i] < 0:
                continue
            for j in range(m):
                if j == solucao[i]:
                    continue
                delta, viavel = _delta_relocate(i, j, solucao, instancia)
                if viavel and delta < melhor_delta:
                    melhor_delta = delta
                    melhor_i     = i
                    melhor_j     = j

        if melhor_i >= 0:
            solucao[melhor_i] = melhor_j
            custo_atual      += melhor_delta
            n_iteracoes      += 1
            melhorou          = True

    return solucao, custo_atual, n_iteracoes


def vizinhanca_swap(solucao, instancia, eps=1e-9):
    ''' Vizinhança Swap: troca as máquinas de dois produtos. '''
    solucao      = solucao[:]
    n            = instancia['n_produtos']
    custo_atual  = calcular_custo(solucao, instancia)
    n_iteracoes  = 0
    melhorou     = True

    while melhorou:
        melhorou     = False
        melhor_delta = -eps
        melhor_i     = -1
        melhor_k     = -1

        for i in range(n):
            if solucao[i] < 0:
                continue
            for k in range(i + 1, n):
                if solucao[k] < 0:
                    continue
                delta, viavel = _delta_swap(i, k, solucao, instancia)
                if viavel and delta < melhor_delta:
                    melhor_delta = delta
                    melhor_i     = i
                    melhor_k     = k

        if melhor_i >= 0:
            solucao[melhor_i], solucao[melhor_k] = (
                solucao[melhor_k], solucao[melhor_i]
            )
            custo_atual += melhor_delta
            n_iteracoes += 1
            melhorou     = True

    return solucao, custo_atual, n_iteracoes



# VND (Variable Neighborhood Descent)

def busca_local_vnd(solucao_inicial, instancia):
    """
    Aplica VND com vizinhanças Relocate → Swap.

    Algoritmo
    ---------
    1. Aplica Relocate até estabilizar (ótimo local de Relocate)
    2. Aplica Swap; se houve melhora, volta ao passo 1
    3. Para quando ambas as vizinhanças não melhoram

    Parâmetros
    ----------
    solucao_inicial : list[int]  – solução de partida (ex: saída da gulosa)
    instancia       : dict

    Retorna
    -------
    solucao_final  : list[int]
    custo_final    : float
    historico      : list[dict]  – registro de cada fase para análise
    """
    solucao  = solucao_inicial[:]
    custo    = calcular_custo(solucao, instancia)
    historico = []
    fase      = 0

    while True:
        fase += 1

        # --- Fase Relocate ---
        sol_r, custo_r, it_r = vizinhanca_relocate(solucao, instancia)
        historico.append({
            'fase'       : fase,
            'vizinhanca' : 'Relocate',
            'custo_antes': custo,
            'custo_apos' : custo_r,
            'movimentos' : it_r,
        })

        # --- Fase Swap ---
        sol_s, custo_s, it_s = vizinhanca_swap(sol_r, instancia)
        historico.append({
            'fase'       : fase,
            'vizinhanca' : 'Swap',
            'custo_antes': custo_r,
            'custo_apos' : custo_s,
            'movimentos' : it_s,
        })

        if custo_s < custo - 1e-9:
            # Houve melhora nesta iteração VND: recomeça
            solucao = sol_s
            custo   = custo_s
        else:
            # Nenhuma vizinhança melhorou: ótimo local encontrado
            solucao = sol_r  # melhor entre as duas últimas fases
            custo   = custo_r if custo_r <= custo_s else custo_s
            break

    return solucao, custo, historico

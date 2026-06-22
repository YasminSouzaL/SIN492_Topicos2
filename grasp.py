import random
from heuristica   import calcular_custo
from busca_local  import busca_local_vnd
from tabu_search  import tabu_search


def _construcao_grasp(instancia, alpha, rng):
    """
    Constrói uma solução viável de forma semi-gulosa usando RCL.

    Parâmetros
    ----------
    instancia : dict
    alpha     : float em [0, 1]
        0 → completamente guloso (RCL = melhor candidato)
        1 → completamente aleatório (RCL = todos os candidatos viáveis)
    rng       : random.Random  – gerador com semente controlada

    Retorna
    -------
    solucao     : list[int]  – s[i] = máquina do produto i (-1 = não alocado)
    custo_total : float
    nao_alocados: list[int]
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

    # Mesma ordem de prioridade da gulosa (produto mais caro primeiro)
    ordem = sorted(range(n), key=lambda i: -min(f[i]))

    for i in ordem:
        # Calcula delta para cada máquina viável
        candidatos = []
        for j in range(m):
            if consumo[i][j] > cap_restante[j]:
                continue
            delta = f[i][j]
            for k in range(n):
                if solucao[k] >= 0:
                    delta += inter[i][k] * dist[j][solucao[k]]
            candidatos.append((delta, j))

        if not candidatos:
            nao_alocados.append(i)
            continue

        # Monta RCL: candidatos cujo delta <= delta_min + alpha*(delta_max - delta_min)
        delta_min = min(c[0] for c in candidatos)
        delta_max = max(c[0] for c in candidatos)
        limiar    = delta_min + alpha * (delta_max - delta_min)
        rcl       = [j for (d, j) in candidatos if d <= limiar]

        # Escolhe aleatoriamente dentro da RCL
        j_escolhido = rng.choice(rcl)
        solucao[i]  = j_escolhido
        cap_restante[j_escolhido] -= consumo[i][j_escolhido]

    custo_total = calcular_custo(solucao, instancia)
    return solucao, custo_total, nao_alocados



def grasp(instancia, max_iter=100, alpha=0.3, semente=None,
          busca_local='vnd', tabu_iter_internas=20, tabu_tenure=7):
    """
    Executa o GRASP para o GQAP.

    Parâmetros
    ----------
    instancia          : dict
    max_iter           : int    – número de iterações do GRASP (padrão: 100)
    alpha              : float  – parâmetro de aleatoriedade da RCL (padrão: 0.3)
    semente            : int    – semente para reprodutibilidade
    busca_local        : str    – 'vnd' (padrão, Etapa 2) ou 'tabu'
                                   (Tabu Search curta como intensificador)
    tabu_iter_internas : int    – nº de iterações da Tabu Search por chamada,
                                   usado apenas quando busca_local='tabu'
                                   (poucas iterações, pois é chamada 100x)
    tabu_tenure        : int    – tenure da lista tabu, usado apenas quando
                                   busca_local='tabu'

    Retorna
    -------
    melhor_solucao : list[int]
    melhor_custo   : float
    historico      : list[dict] – custo da melhor solução a cada iteração
    """
    if busca_local not in ('vnd', 'tabu'):
        raise ValueError("busca_local deve ser 'vnd' ou 'tabu'")

    rng = random.Random(semente)

    melhor_solucao = None
    melhor_custo   = float('inf')
    historico      = []

    for it in range(1, max_iter + 1):
        # 1. Construção semi-gulosa
        sol_c, custo_c, nao_aloc = _construcao_grasp(instancia, alpha, rng)

        # Pula iterações com produtos não alocados (solução inviável)
        if nao_aloc:
            historico.append({
                'iteracao'    : it,
                'custo_const' : custo_c,
                'custo_bl'    : None,
                'melhor_custo': melhor_custo,
                'nao_alocados': len(nao_aloc),
            })
            continue

        # 2. Busca local (intensificação) — VND ou Tabu Search curta
        if busca_local == 'vnd':
            sol_int, custo_int, _ = busca_local_vnd(sol_c, instancia)
        else:
            # Tabu Search com poucas iterações por chamada: explora também
            # movimentos de piora controlada antes de devolver ao GRASP.
            # Semente derivada para manter reprodutibilidade por iteração.
            sol_int, custo_int, _ = tabu_search(
                instancia, sol_c,
                max_iter=tabu_iter_internas,
                tenure=tabu_tenure,
                semente=rng.randint(0, 10**9),
            )

        # 3. Atualiza melhor global
        if custo_int < melhor_custo:
            melhor_custo   = custo_int
            melhor_solucao = sol_int[:]

        historico.append({
            'iteracao'    : it,
            'custo_const' : custo_c,
            'custo_bl'    : custo_int,
            'melhor_custo': melhor_custo,
            'nao_alocados': 0,
        })

    return melhor_solucao, melhor_custo, historico
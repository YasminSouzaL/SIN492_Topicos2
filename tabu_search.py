import random
from heuristica  import calcular_custo
from busca_local import _delta_relocate, _delta_swap


def _gerar_vizinhanca(solucao, instancia):
    """
    Gera todos os movimentos viáveis (Relocate e Swap) com seus deltas.

    Retorna lista de tuplas:
        ('R', i, j_novo, j_antigo, delta)
        ('S', i, k, None, delta)
    """
    n = instancia['n_produtos']
    m = instancia['n_maquinas']
    movimentos = []

    # Relocate
    for i in range(n):
        if solucao[i] < 0:
            continue
        j_atual = solucao[i]
        for j in range(m):
            if j == j_atual:
                continue
            delta, viavel = _delta_relocate(i, j, solucao, instancia)
            if viavel:
                movimentos.append(('R', i, j, j_atual, delta))

    # Swap
    for i in range(n):
        if solucao[i] < 0:
            continue
        for k in range(i + 1, n):
            if solucao[k] < 0:
                continue
            delta, viavel = _delta_swap(i, k, solucao, instancia)
            if viavel:
                movimentos.append(('S', i, k, None, delta))

    return movimentos


def _aplicar_movimento(solucao, mov):
    """Aplica o movimento na solução (em uma cópia) e retorna a nova solução."""
    nova = solucao[:]
    tipo = mov[0]
    if tipo == 'R':
        _, i, j_novo, _, _ = mov
        nova[i] = j_novo
    else:  # Swap
        _, i, k, _, _ = mov
        nova[i], nova[k] = nova[k], nova[i]
    return nova


def _atributo_tabu(mov):
    tipo = mov[0]
    if tipo == 'R':
        _, i, j_novo, j_antigo, _ = mov
        # Proíbe devolver i para a posição antiga (j_antigo) por um tempo
        return ('R', i, j_antigo)
    else:
        _, i, k, _, _ = mov
        # Proíbe repetir o mesmo swap (i, k) por um tempo
        return ('S', i, k)




def tabu_search(instancia, solucao_inicial, max_iter=200, tenure=10, semente=None):
    """
    Executa a Busca Tabu sobre uma solução inicial.

    Parâmetros
    ----------
    instancia       : dict
    solucao_inicial : list[int]  – normalmente a saída da heurística gulosa
    max_iter        : int        – número máximo de iterações (padrão: 200)
    tenure          : int        – duração (em iterações) que um atributo
                                    permanece proibido na lista tabu (padrão: 10)
    semente         : int        – semente para desempate aleatório

    Retorna
    -------
    melhor_solucao : list[int]
    melhor_custo   : float
    historico      : list[dict] – custo atual e melhor custo por iteração
    """
    rng = random.Random(semente)

    solucao_atual = solucao_inicial[:]
    custo_atual   = calcular_custo(solucao_atual, instancia)

    melhor_solucao = solucao_atual[:]
    melhor_custo   = custo_atual

    lista_tabu = {}   # atributo -> iteração em que deixa de ser tabu
    historico  = []

    for it in range(1, max_iter + 1):
        vizinhanca = _gerar_vizinhanca(solucao_atual, instancia)

        if not vizinhanca:
            # Nenhum movimento viável: solução isolada, encerra
            break

        # Embaralha para desempate aleatório entre movimentos de mesmo delta
        rng.shuffle(vizinhanca)

        melhor_mov        = None
        melhor_delta_mov  = float('inf')

        for mov in vizinhanca:
            delta = mov[4]
            atributo = _atributo_tabu(mov)
            eh_tabu  = lista_tabu.get(atributo, 0) > it

            custo_candidato = custo_atual + delta

            # Critério de aspiração: aceita mesmo se tabu, se for melhor que o
            # melhor global já encontrado
            aspiracao = custo_candidato < melhor_custo - 1e-9

            if eh_tabu and not aspiracao:
                continue

            if delta < melhor_delta_mov:
                melhor_delta_mov = delta
                melhor_mov       = mov

        if melhor_mov is None:
            # Todos os movimentos estavam tabu e nenhum atendeu aspiração
            historico.append({
                'iteracao'    : it,
                'custo_atual' : custo_atual,
                'melhor_custo': melhor_custo,
                'bloqueado'   : True,
            })
            continue

        # Aplica o movimento escolhido
        solucao_atual = _aplicar_movimento(solucao_atual, melhor_mov)
        custo_atual  += melhor_delta_mov

        # Atualiza lista tabu
        atributo = _atributo_tabu(melhor_mov)
        lista_tabu[atributo] = it + tenure

        # Atualiza melhor global
        if custo_atual < melhor_custo - 1e-9:
            melhor_custo   = custo_atual
            melhor_solucao = solucao_atual[:]

        historico.append({
            'iteracao'    : it,
            'custo_atual' : custo_atual,
            'melhor_custo': melhor_custo,
            'bloqueado'   : False,
        })

    return melhor_solucao, melhor_custo, historico
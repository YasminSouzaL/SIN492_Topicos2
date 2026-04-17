# import time
# import matplotlib.pyplot as plt


# # ==============================
# # LEITURA DA INSTÂNCIA
# # ==============================
# def ler_instancia(nome_arquivo):
#     with open(nome_arquivo, "r") as f:
#         linhas = f.readlines()

#     n_produtos, n_maquinas = map(int, linhas[0].split())

#     custo = [list(map(int, linhas[i+1].split())) for i in range(n_produtos)]
#     consumo = [list(map(int, linhas[i+1+n_produtos].split())) for i in range(n_produtos)]
#     capacidade = list(map(int, linhas[-1].split()))

#     return custo, consumo, capacidade


# # ==============================
# # HEURÍSTICA GULOSA
# # ==============================
# def heuristica_gulosa(custo, consumo, capacidade):
#     n_produtos = len(custo)
#     n_maquinas = len(capacidade)

#     solucao = [-1] * n_produtos
#     cap_restante = capacidade[:]

#     custo_total = 0
#     nao_alocados = 0

#     for i in range(n_produtos):
#         melhor_maquina = -1
#         melhor_custo = float('inf')

#         for j in range(n_maquinas):
#             if consumo[i][j] <= cap_restante[j]:
#                 if custo[i][j] < melhor_custo:
#                     melhor_custo = custo[i][j]
#                     melhor_maquina = j

#         if melhor_maquina != -1:
#             solucao[i] = melhor_maquina
#             cap_restante[melhor_maquina] -= consumo[i][melhor_maquina]
#             custo_total += melhor_custo
#         else:
#             nao_alocados += 1

#     return solucao, custo_total, nao_alocados


# # ==============================
# # TESTE DA INSTÂNCIA
# # ==============================
# def testar_instancia(arquivo):
#     custo, consumo, capacidade = ler_instancia(arquivo)

#     inicio = time.time()
#     _, custo_total, nao_alocados = heuristica_gulosa(custo, consumo, capacidade)
#     fim = time.time()

#     tempo_execucao = fim - inicio

#     return custo_total, tempo_execucao, nao_alocados


# # ==============================
# # MAIN
# # ==============================
# if __name__ == "__main__":
#     arquivos = [
#         "dataset/inst_5.txt",
#         "dataset/inst_10.txt",
#         "dataset/inst_20.txt",
#         "dataset/inst_50.txt"
#     ]

#     resultados = []

#     # Executa testes
#     for arquivo in arquivos:
#         custo, tempo, nao_alocados = testar_instancia(arquivo)
#         resultados.append((arquivo, custo, tempo, nao_alocados))

#     # ==============================
#     # SALVAR RESULTADOS
#     # ==============================
#     with open("resultados.txt", "w", encoding="utf-8") as out:
#         out.write("Instancia\tProdutos\tCusto\tTempo(s)\tNao_Alocados\n")

#         for arq, custo, tempo, nao_alocados in resultados:
#             n_produtos = len(ler_instancia(arq)[0])
#             out.write(f"{arq}\t{n_produtos}\t{custo}\t{tempo:.6f}\t{nao_alocados}\n")

#     print("Testes concluídos!")

#     # ==============================
#     # GRÁFICOS
#     # ==============================
#     labels = [str(len(ler_instancia(a)[0])) for a in arquivos]
#     custos = [r[1] for r in resultados]
#     tempos = [r[2] for r in resultados]

#     plt.figure(figsize=(12, 5))

#     # Gráfico de custo
#     plt.subplot(1, 2, 1)
#     plt.bar(labels, custos)
#     plt.title("Custo por Número de Produtos")
#     plt.xlabel("Produtos")
#     plt.ylabel("Custo Total")

#     # Gráfico de tempo
#     plt.subplot(1, 2, 2)
#     plt.bar(labels, tempos)
#     plt.color = 'orange'
#     plt.title("Tempo de Execução")
#     plt.xlabel("Produtos")
#     plt.ylabel("Tempo (s)")

#     plt.tight_layout()
#     plt.savefig("resultados_graficos.png")
#     plt.show()



import time


def calcular_custo_total(solucao, custo_linear, fluxo, distancia):
    """
    Calcula o custo total de uma solução já construída.

    Função objetivo do GQAP (simplificada):
        F(s) = SUM_i  custo_linear[i][s[i]]
             + SUM_{i<k}  fluxo[i][k] * distancia[s[i]][s[k]]

    Complexidade: O(n^2)
    """
    n = len(solucao)
    custo = 0

    # Termo linear
    for i in range(n):
        if solucao[i] != -1:
            custo += custo_linear[i][solucao[i]]

    # Termo quadrático (interações entre pares de entidades alocadas)
    for i in range(n):
        for k in range(i + 1, n):
            if solucao[i] != -1 and solucao[k] != -1:
                custo += fluxo[i][k] * distancia[solucao[i]][solucao[k]]

    return custo


def heuristica_gulosa(custo_linear, fluxo, distancia, consumo, capacidade):
    """
    Heurística construtiva gulosa para o GQAP.

    A cada passo, aloca a próxima entidade na localização viável
    de menor custo incremental, considerando:
      - O custo linear de alocação
      - O custo quadrático acumulado com as entidades já alocadas
      - A restrição de capacidade de cada localização

    Parâmetros
    ----------
    custo_linear : list[list[float]]
        custo_linear[i][j] = custo de alocar entidade i na localização j
    fluxo : list[list[float]]
        fluxo[i][k] = fluxo/interação entre entidades i e k
    distancia : list[list[float]]
        distancia[j][l] = distância entre localizações j e l
    consumo : list[list[float]]
        consumo[i][j] = recursos consumidos por i quando alocada em j
    capacidade : list[float]
        capacidade[j] = capacidade total da localização j

    Retorno
    -------
    solucao : list[int]
        solucao[i] = índice da localização atribuída à entidade i
        (-1 se não foi possível alocar)
    custo_total : float
        Valor da função objetivo da solução encontrada
    nao_alocadas : list[int]
        Índices das entidades que não puderam ser alocadas

    Complexidade: O(n^2 * m)
    """
    n_entidades  = len(custo_linear)
    n_locais     = len(capacidade)

    solucao      = [-1] * n_entidades
    cap_restante = capacidade[:]   # cópia para não modificar o original
    nao_alocadas = []

    for i in range(n_entidades):
        melhor_local = -1
        melhor_custo_incremental = float('inf')

        for j in range(n_locais):
            # ── Restrição de capacidade ──────────────────────────────────
            if consumo[i][j] > cap_restante[j]:
                continue

            # ── Custo incremental de alocar i em j ───────────────────────
            c = custo_linear[i][j]

            # Adiciona o custo quadrático com as entidades já alocadas
            for k in range(n_entidades):
                if solucao[k] != -1:
                    l = solucao[k]
                    c += fluxo[i][k] * distancia[j][l]

            if c < melhor_custo_incremental:
                melhor_custo_incremental = c
                melhor_local = j

        # ── Atribui ou registra falha ────────────────────────────────────
        if melhor_local != -1:
            solucao[i] = melhor_local
            cap_restante[melhor_local] -= consumo[i][melhor_local]
        else:
            nao_alocadas.append(i)
            print(f"  [AVISO] Entidade {i} não pôde ser alocada "
                  f"(capacidade insuficiente em todas as localizações).")

    custo_total = calcular_custo_total(solucao, custo_linear, fluxo, distancia)
    return solucao, custo_total, nao_alocadas


def executar(instancia, verbose=False):
    """
    Executa a heurística em uma instância e retorna métricas.

    Parâmetros
    ----------
    instancia : dict
        Dicionário com as chaves:
        'custo_linear', 'fluxo', 'distancia', 'consumo', 'capacidade', 'nome'
    verbose : bool
        Se True, imprime detalhes da execução

    Retorno
    -------
    dict com: solucao, custo, nao_alocadas, tempo_ms, viavel
    """
    nome = instancia.get('nome', 'sem_nome')
    if verbose:
        print(f"\n{'='*55}")
        print(f"  Instância: {nome}")
        print(f"  Entidades: {len(instancia['custo_linear'])}  |  "
              f"Localizações: {len(instancia['capacidade'])}")
        print(f"{'='*55}")

    inicio = time.perf_counter()

    solucao, custo, nao_alocadas = heuristica_gulosa(
        instancia['custo_linear'],
        instancia['fluxo'],
        instancia['distancia'],
        instancia['consumo'],
        instancia['capacidade'],
    )

    fim = time.perf_counter()
    tempo_ms = (fim - inicio) * 1000
    viavel   = len(nao_alocadas) == 0

    if verbose:
        status = "VIÁVEL ✓" if viavel else f"INVIÁVEL ✗ ({len(nao_alocadas)} não alocadas)"
        print(f"  Custo total  : {custo:.2f}")
        print(f"  Status       : {status}")
        print(f"  Tempo        : {tempo_ms:.3f} ms")
        print(f"  Solução      : {solucao}")

    return {
        'instancia'   : nome,
        'solucao'     : solucao,
        'custo'       : custo,
        'nao_alocadas': nao_alocadas,
        'tempo_ms'    : tempo_ms,
        'viavel'      : viavel,
    }
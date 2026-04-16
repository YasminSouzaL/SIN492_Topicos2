import time
import matplotlib.pyplot as plt


# ==============================
# LEITURA DA INSTÂNCIA
# ==============================
def ler_instancia(nome_arquivo):
    with open(nome_arquivo, "r") as f:
        linhas = f.readlines()

    n_produtos, n_maquinas = map(int, linhas[0].split())

    custo = [list(map(int, linhas[i+1].split())) for i in range(n_produtos)]
    consumo = [list(map(int, linhas[i+1+n_produtos].split())) for i in range(n_produtos)]
    capacidade = list(map(int, linhas[-1].split()))

    return custo, consumo, capacidade


# ==============================
# HEURÍSTICA GULOSA
# ==============================
def heuristica_gulosa(custo, consumo, capacidade):
    n_produtos = len(custo)
    n_maquinas = len(capacidade)

    solucao = [-1] * n_produtos
    cap_restante = capacidade[:]

    custo_total = 0
    nao_alocados = 0

    for i in range(n_produtos):
        melhor_maquina = -1
        melhor_custo = float('inf')

        for j in range(n_maquinas):
            if consumo[i][j] <= cap_restante[j]:
                if custo[i][j] < melhor_custo:
                    melhor_custo = custo[i][j]
                    melhor_maquina = j

        if melhor_maquina != -1:
            solucao[i] = melhor_maquina
            cap_restante[melhor_maquina] -= consumo[i][melhor_maquina]
            custo_total += melhor_custo
        else:
            nao_alocados += 1

    return solucao, custo_total, nao_alocados


# ==============================
# TESTE DA INSTÂNCIA
# ==============================
def testar_instancia(arquivo):
    custo, consumo, capacidade = ler_instancia(arquivo)

    inicio = time.time()
    _, custo_total, nao_alocados = heuristica_gulosa(custo, consumo, capacidade)
    fim = time.time()

    tempo_execucao = fim - inicio

    return custo_total, tempo_execucao, nao_alocados


# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    arquivos = [
        "dataset/inst_5.txt",
        "dataset/inst_10.txt",
        "dataset/inst_20.txt",
        "dataset/inst_50.txt"
    ]

    resultados = []

    # Executa testes
    for arquivo in arquivos:
        custo, tempo, nao_alocados = testar_instancia(arquivo)
        resultados.append((arquivo, custo, tempo, nao_alocados))

    # ==============================
    # SALVAR RESULTADOS
    # ==============================
    with open("resultados.txt", "w", encoding="utf-8") as out:
        out.write("Instancia\tProdutos\tCusto\tTempo(s)\tNao_Alocados\n")

        for arq, custo, tempo, nao_alocados in resultados:
            n_produtos = len(ler_instancia(arq)[0])
            out.write(f"{arq}\t{n_produtos}\t{custo}\t{tempo:.6f}\t{nao_alocados}\n")

    print("Testes concluídos!")

    # ==============================
    # GRÁFICOS
    # ==============================
    labels = [str(len(ler_instancia(a)[0])) for a in arquivos]
    custos = [r[1] for r in resultados]
    tempos = [r[2] for r in resultados]

    plt.figure(figsize=(12, 5))

    # Gráfico de custo
    plt.subplot(1, 2, 1)
    plt.bar(labels, custos)
    plt.title("Custo por Número de Produtos")
    plt.xlabel("Produtos")
    plt.ylabel("Custo Total")

    # Gráfico de tempo
    plt.subplot(1, 2, 2)
    plt.bar(labels, tempos)
    plt.color = 'orange'
    plt.title("Tempo de Execução")
    plt.xlabel("Produtos")
    plt.ylabel("Tempo (s)")

    plt.tight_layout()
    plt.savefig("resultados_graficos.png")
    plt.show()
def ler_instancia(nome_arquivo):
    with open(nome_arquivo, "r") as f:
        linhas = f.readlines()

    n_produtos, n_maquinas = map(int, linhas[0].split())

    custo = [list(map(int, linhas[i+1].split())) for i in range(n_produtos)]
    consumo = [list(map(int, linhas[i+1+n_produtos].split())) for i in range(n_produtos)]
    capacidade = list(map(int, linhas[-1].split()))

    return custo, consumo, capacidade

def heuristica_gulosa(custo, consumo, capacidade):
    n_produtos = len(custo)
    n_maquinas = len(capacidade)

    solucao = [-1] * n_produtos
    cap_restante = capacidade[:]

    custo_total = 0
    print("Iniciando heurística gulosa...")

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
            print(f"Produto {i} não pôde ser alocado!")

    return solucao, custo_total

if __name__ == "__main__":
    arquivos = ["dataset/inst_5.txt", "dataset/inst_10.txt",
                "dataset/inst_20.txt", "dataset/inst_50.txt"]

    with open("resultados.txt", "w") as out:
        out.write("Instancia | Custo\n")

        for arq in arquivos:
            custo, consumo, capacidade = ler_instancia(arq)
            solucao, custo_total = heuristica_gulosa(custo, consumo, capacidade)

            linha = f"{arq} | {custo_total}\n"
            print(linha)
            out.write(linha)
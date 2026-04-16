import random
import os

def gerar_instancia(n_produtos, n_maquinas):
    custo = []
    consumo = []

    for i in range(n_produtos):
        custo.append([random.randint(5, 20) for _ in range(n_maquinas)])
        consumo.append([random.randint(1, 5) for _ in range(n_maquinas)])

    capacidade = [random.randint(10, 20) for _ in range(n_maquinas)]

    return custo, consumo, capacidade


def salvar_instancia(nome_arquivo, custo, consumo, capacidade):
    with open(nome_arquivo, "w") as f:
        f.write(f"{len(custo)} {len(capacidade)}\n")

        for linha in custo:
            f.write(" ".join(map(str, linha)) + "\n")

        for linha in consumo:
            f.write(" ".join(map(str, linha)) + "\n")

        f.write(" ".join(map(str, capacidade)) + "\n")


# cria pasta dataset
os.makedirs("dataset", exist_ok=True)

# gera várias instâncias
for n in [5, 10, 20, 50]:
    custo, consumo, capacidade = gerar_instancia(n, 3)
    salvar_instancia(f"dataset/inst_{n}.txt", custo, consumo, capacidade)

print("Datasets gerados!")
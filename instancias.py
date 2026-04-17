"""
Gerador de Instâncias Sintéticas para o GQAP Simplificado.

Gera instâncias controladas com diferentes tamanhos e níveis de
apertamento de capacidade (capacidade folgada, média, apertada).

Disciplina: SIN-492 Tópicos Especiais 2 (2026/1)
Autores: Yasmin Souza, José Guedes
"""

import random
import json
import os


def gerar_instancia(
    n_entidades,
    n_locais,
    fator_capacidade=1.5,
    seed=None,
    nome=None
):
    """
    Gera uma instância sintética do GQAP simplificado.

    Parâmetros
    ----------
    n_entidades      : int   — número de entidades a alocar
    n_locais         : int   — número de localizações disponíveis
    fator_capacidade : float — controla folga da capacidade
                               1.0 = muito apertado, 2.0 = folgado
    seed             : int   — semente para reprodutibilidade
    nome             : str   — identificador da instância

    Retorno
    -------
    dict com todas as matrizes da instância
    """
    rng = random.Random(seed)

    n = n_entidades
    m = n_locais

    # ── Custo linear: alocar entidade i na localização j ─────────────
    custo_linear = [
        [round(rng.uniform(1, 100), 2) for j in range(m)]
        for i in range(n)
    ]

    # ── Fluxo entre entidades (matriz simétrica) ──────────────────────
    fluxo = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for k in range(i + 1, n):
            f = round(rng.uniform(0, 50), 2)
            fluxo[i][k] = f
            fluxo[k][i] = f

    # ── Distância entre localizações (matriz simétrica) ───────────────
    distancia = [[0.0] * m for _ in range(m)]
    for j in range(m):
        for l in range(j + 1, m):
            d = round(rng.uniform(1, 20), 2)
            distancia[j][l] = d
            distancia[l][j] = d

    # ── Consumo de recursos: entidade i na localização j ─────────────
    consumo = [
        [round(rng.uniform(1, 10), 2) for j in range(m)]
        for i in range(n)
    ]

    # ── Capacidade: suficiente para alocar todos com fator de folga ───
    # Para cada localização j, a demanda mínima esperada é a média de
    # consumo[i][j] multiplicada pelo número médio de entidades por local.
    entidades_por_local = n / m
    capacidade = []
    for j in range(m):
        demanda_media = sum(consumo[i][j] for i in range(n)) / n
        cap = round(demanda_media * entidades_por_local * fator_capacidade, 2)
        cap = max(cap, max(consumo[i][j] for i in range(n)))  # garante ao menos 1 por local
        capacidade.append(cap)

    return {
        'nome'        : nome or f"inst_{n}x{m}_f{fator_capacidade}",
        'n_entidades' : n,
        'n_locais'    : m,
        'fator_cap'   : fator_capacidade,
        'seed'        : seed,
        'custo_linear': custo_linear,
        'fluxo'       : fluxo,
        'distancia'   : distancia,
        'consumo'     : consumo,
        'capacidade'  : capacidade,
    }


def salvar_instancia(instancia, diretorio='instancias'):
    """Salva uma instância em arquivo JSON."""
    os.makedirs(diretorio, exist_ok=True)
    caminho = os.path.join(diretorio, f"{instancia['nome']}.json")
    with open(caminho, 'w') as f:
        json.dump(instancia, f, indent=2)
    print(f"  Salva: {caminho}")
    return caminho


def carregar_instancia(caminho):
    """Carrega uma instância de um arquivo JSON."""
    with open(caminho) as f:
        return json.load(f)


def gerar_conjunto_experimentos(diretorio='instancias'):
    """
    Gera o conjunto padrão de instâncias para os experimentos do trabalho.

    Configurações:
        Tamanhos: pequeno (5x3), médio (15x6), grande (30x10)
        Fatores de capacidade: folgado (2.0), médio (1.5), apertado (1.1)
        5 sementes por configuração → 45 instâncias no total
    """
    tamanhos = [
        (5,  3,  'pequeno'),
        (15, 6,  'medio'),
        (30, 10, 'grande'),
    ]
    fatores = [
        (2.0, 'folgado'),
        (1.5, 'medio'),
        (1.1, 'apertado'),
    ]
    seeds = [42, 123, 456, 789, 1001]

    instancias = []
    print("Gerando instâncias sintéticas...\n")

    for (n, m, tam_nome) in tamanhos:
        for (fator, fat_nome) in fatores:
            for s in seeds:
                nome = f"{tam_nome}_{fat_nome}_s{s}"
                inst = gerar_instancia(
                    n_entidades=n,
                    n_locais=m,
                    fator_capacidade=fator,
                    seed=s,
                    nome=nome
                )
                salvar_instancia(inst, diretorio)
                instancias.append(inst)

    print(f"\nTotal: {len(instancias)} instâncias geradas em '{diretorio}/'")
    return instancias


if __name__ == '__main__':
    gerar_conjunto_experimentos()
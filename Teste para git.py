#Teste para git
def heuristica_gulosa(custo, consumo, capacidade):
    n_produtos = len(custo)
    n_maquinas = len(capacidade)
    
    # solução: qual máquina cada produto vai
    solucao = [-1] * n_produtos
    
    # capacidade restante
    cap_restante = capacidade[:]
    
    custo_total = 0
    
    for i in range(n_produtos):
        melhor_maquina = -1
        melhor_custo = float('inf')
        
        for j in range(n_maquinas):
            # verifica se cabe na máquina
            if consumo[i][j] <= cap_restante[j]:
                if custo[i][j] < melhor_custo:
                    melhor_custo = custo[i][j]
                    melhor_maquina = j
        
        # se encontrou alguma máquina válida
        if melhor_maquina != -1:
            solucao[i] = melhor_maquina
            cap_restante[melhor_maquina] -= consumo[i][melhor_maquina]
            custo_total += melhor_custo
        else:
            print(f"Produto {i} não pôde ser alocado!")
    
    return solucao, custo_total
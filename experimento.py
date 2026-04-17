

import os
import statistics
from instancias   import gerar_conjunto_experimentos, carregar_instancia
from heuristica   import executar


def rodar_experimentos(diretorio='instancias'):
    """
    Executa a heurística em todas as instâncias do diretório.
    Retorna lista de resultados.
    """
    arquivos = sorted(
        f for f in os.listdir(diretorio) if f.endswith('.json')
    )

    if not arquivos:
        print("Nenhuma instância encontrada. Gerando...")
        gerar_conjunto_experimentos(diretorio)
        arquivos = sorted(
            f for f in os.listdir(diretorio) if f.endswith('.json')
        )

    resultados = []
    print(f"\nExecutando heurística em {len(arquivos)} instâncias...\n")

    for arq in arquivos:
        inst = carregar_instancia(os.path.join(diretorio, arq))
        res  = executar(inst, verbose=False)
        resultados.append(res)
        status = "OK" if res['viavel'] else "INVIAVEL"
        print(f"  {res['instancia']:<35}  custo={res['custo']:>10.2f}  "
              f"tempo={res['tempo_ms']:>7.3f}ms  [{status}]")

    return resultados


def gerar_tabela_resumo(resultados):
    """
    Agrupa resultados por (tamanho, fator_capacidade) e exibe
    médias de custo e tempo — pronta para copiar no LaTeX.
    """
    grupos = {}
    for r in resultados:
        # extrai grupo do nome: "pequeno_folgado_s42" → ("pequeno","folgado")
        partes = r['instancia'].split('_')
        chave  = (partes[0], partes[1])
        grupos.setdefault(chave, []).append(r)

    print("\n" + "=" * 72)
    print(f"{'Tamanho':<10} {'Capacidade':<12} {'Viáveis':>8} "
          f"{'Custo Médio':>14} {'Custo Min':>12} {'Custo Max':>12} "
          f"{'Tempo Médio (ms)':>17}")
    print("=" * 72)

    for (tam, fat), lista in sorted(grupos.items()):
        custos  = [r['custo']    for r in lista]
        tempos  = [r['tempo_ms'] for r in lista]
        viaveis = sum(1 for r in lista if r['viavel'])

        print(f"{tam:<10} {fat:<12} {viaveis:>6}/{len(lista):<2} "
              f"{statistics.mean(custos):>14.2f} "
              f"{min(custos):>12.2f} "
              f"{max(custos):>12.2f} "
              f"{statistics.mean(tempos):>17.4f}")

    print("=" * 72)


'''
def gerar_tabela_latex(resultados):
    """
    Gera o código LaTeX da tabela de resultados para o artigo.
    """
    grupos = {}
    for r in resultados:
        partes = r['instancia'].split('_')
        chave  = (partes[0], partes[1])
        grupos.setdefault(chave, []).append(r)

    tamanho_map = {'pequeno': '5×3',  'medio': '15×6', 'grande': '30×10'}
    fator_map   = {'folgado': 'Folgada (2.0)', 'medio': 'Média (1.5)',
                   'apertado': 'Apertada (1.1)'}

    linhas = []
    for (tam, fat), lista in sorted(grupos.items()):
        custos  = [r['custo']    for r in lista]
        tempos  = [r['tempo_ms'] for r in lista]
        viaveis = sum(1 for r in lista if r['viavel'])

        n_str  = tamanho_map.get(tam, tam)
        f_str  = fator_map.get(fat, fat)
        viavel = f"{viaveis}/{len(lista)}"

        linhas.append(
            f"  {n_str} & {f_str} & {viavel} & "
            f"{statistics.mean(custos):.2f} & "
            f"{min(custos):.2f} & "
            f"{max(custos):.2f} & "
            f"{statistics.mean(tempos):.4f} \\\\"
        )

    latex = r"""
\begin{table}[ht]
\centering
\caption{Resultados da heurística construtiva gulosa nas instâncias sintéticas}
\label{tab:resultados}
\begin{tabular}{llcrrrrr}
\hline
\textbf{Tamanho} & \textbf{Capacidade} & \textbf{Viáveis} &
\textbf{Custo Médio} & \textbf{Custo Mín.} & \textbf{Custo Máx.} &
\textbf{Tempo (ms)} \\
\hline
""" + "\n".join(linhas) + r"""
\hline
\end{tabular}
\end{table}
"""
    print("\n--- TABELA LATEX ---")
    print(latex)
    return latex

'''




import matplotlib.pyplot as plt
import statistics


def gerar_tabela_visual(resultados):
    grupos = {}

    for r in resultados:
        partes = r['instancia'].split('_')
        chave = (partes[0], partes[1])
        grupos.setdefault(chave, []).append(r)

    tamanho_map = {'pequeno': '5x3', 'medio': '15x6', 'grande': '30x10'}
    fator_map = {'folgado': 'Folgada', 'medio': 'Média', 'apertado': 'Apertada'}

    dados_tabela = []

    for (tam, fat), lista in sorted(grupos.items()):
        custos = [r['custo'] for r in lista]
        tempos = [r['tempo_ms'] for r in lista]
        viaveis = sum(1 for r in lista if r['viavel'])

        dados_tabela.append([
            tamanho_map.get(tam, tam),
            fator_map.get(fat, fat),
            f"{viaveis}/{len(lista)}",
            f"{statistics.mean(custos):.2f}",
            f"{min(custos):.2f}",
            f"{max(custos):.2f}",
            f"{statistics.mean(tempos):.4f}"
        ])

    colunas = [
        "Tamanho", "Capacidade", "Viáveis",
        "Custo Médio", "Custo Min", "Custo Max", "Tempo (ms)"
    ]

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis('off')

    tabela = ax.table(
        cellText=dados_tabela,
        colLabels=colunas,
        loc='center',
        cellLoc='center'
    )

    # Fonte
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)

    # Ajuste de largura
    tabela.auto_set_column_width(col=list(range(len(colunas))))

    # 🎨 Estilo
    for (row, col), cell in tabela.get_celld().items():
        # Cabeçalho
        if row == 0:
            cell.set_text_props(weight='bold')
            cell.set_facecolor('#cccccc')
        else:
            # Zebra
            if row % 2 == 0:
                cell.set_facecolor('#f2f2f2')

    plt.title("Resultados da Heurística Gulosa (GQAP)", fontsize=14, weight='bold')
    plt.tight_layout()

    plt.savefig("tabela_resultados_melhorada.png", dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == '__main__':
    # 1. Gera instâncias (se não existirem)
    if not os.path.exists('instancias') or not os.listdir('instancias'):
        gerar_conjunto_experimentos()

    # 2. Executa heurística
    resultados = rodar_experimentos()

    # 3. Exibe tabela resumo no terminal
    gerar_tabela_resumo(resultados)

    #4 .
    gerar_tabela_visual(resultados)

   
# SIN492_Topicos2

Repositório do projeto da disciplina **SIN 492 – Tópicos Especiais 2 (2026/1)**.

O trabalho aborda o **Problema de Atribuição Quadrática Generalizada (GQAP)**, utilizando inicialmente uma **heurística construtiva gulosa**, com evolução planejada para **meta-heurísticas (GRASP)**.

---

## Objetivo

O objetivo do projeto é estudar e implementar métodos heurísticos para resolver o GQAP, um problema clássico de otimização combinatória que envolve:

* Alocação de entidades em localizações
* Restrições de capacidade
* Minimização de custos lineares e custos de interação (fluxo × distância)

---

## Metodologia

O projeto foi estruturado de forma incremental:

### 🔹 Etapa 1 — Heurística Construtiva (Atual)

* Implementação de uma heurística gulosa
* Aloca entidades nas melhores localizações disponíveis
* Considera restrições de capacidade
* Calcula:

  * custo linear
  * custo quadrático (interações entre pares)

### 🔹Etapa 2 — Busca Local (Atual)
* Implementação do algoritmo **VND (*Variable Neighborhood Descent*)** como núcleo de intensificação.
* Integração de duas vizinhanças complementares operando em estratégia *Best Improvement*:
  * **Relocate:** Movimentação de uma única entidade para uma localização distinta.
  * **Swap:** Troca simultânea de localização entre duas entidades.
* Estruturação de dados otimizada em Python usando matrizes nativas para garantir tempo de acesso indexado $O(1)$.
* Complexidade por iteração completa do VND de $O(n^2(m+n))$.
---

## Estrutura do Projeto

```
├── heuristica.py          # Heurística construtiva gulosa + Busca Local VND
├── instancias.py          # Gerador corrigido de instâncias sintéticas (45 instâncias)
├── experimento.py         # Runner de experimentos + plotagem de gráficos (Matplotlib)
├── adaptador_qaplib.py    # Adaptador QAPLIB → GQAP (dados embutidos para bancada)
├── instancias/            # Diretório com as instâncias sintéticas geradas (JSON)
├── dataset/               # Diretório com as instâncias QAPLIB adaptadas (JSON)
└── README.md              # Documentação do repositório
```



## Como Executar

# 1. Gerar instâncias sintéticas
python instancias.py

# 2. Gerar dataset QAPLIB (sem necessidade de internet)
python adaptador_qaplib.py

# 3. Rodar todos os experimentos e gerar tabelas LaTeX
python experimento.py

python adaptador_qaplib.py


---

## Artigo Base

O trabalho é inspirado no seguinte artigo:

https://www.researchgate.net/publication/220403439_GRASP_with_path-relinking_for_the_generalized_quadratic_assignment_problem


# Artigo Nosso
Nosso artigo está disponivel : https://www.overleaf.com/read/jmrrdfqtxmhm#750067
---

##  Autores

* Yasmin Souza Lima
* José Guedes

---

## Próximos Passos

Próximos Passos (Etapa 3 - Final)
Introdução da Lista Restrita de Candidatos (RCL) para aleatorizar a fase construtiva, consolidando o algoritmo GRASP completo.

Validação experimental definitiva utilizando os datasets oficiais diretamente da OR-Library e comparação numérica com a literatura.


---

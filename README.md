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

### 🔹 Etapas Futuras

* Implementação do **GRASP**
  * Lista restrita de candidatos (RCL)
  * Construção semi-gulosa
* Inclusão de **busca local**
* Comparação entre abordagens

---

## Estrutura do Projeto

```
.
├── heuristica.py          # Heurística construtiva gulosa (O(n²·m))
├── instancias.py          # Gerador de instâncias sintéticas (45 instâncias)
├── experimento.py         # Runner de experimentos + tabelas LaTeX
├── adaptador_qaplib.py    # Adaptador QAPLIB → GQAP (dados embutidos)
├── instancias/            # Instâncias sintéticas geradas (JSON)
├── dataset/               # Instâncias QAPLIB adaptadas (JSON)
```



## Como Executar

# 1. Gerar instâncias sintéticas
python instancias.py

# 2. Gerar dataset QAPLIB (sem necessidade de internet)
python adaptador_qaplib.py

# 3. Rodar todos os experimentos e gerar tabelas LaTeX
python experimento.py



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

* Implementação do GRASP
* Inclusão de busca local


---

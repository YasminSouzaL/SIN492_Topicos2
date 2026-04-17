# SIN492_Topicos2

Repositório do projeto da disciplina **SIN 492 – Tópicos Especiais 2 (2026/1)**.

O trabalho aborda o **Problema de Atribuição Quadrática Generalizada (GQAP)**, utilizando inicialmente uma **heurística construtiva gulosa**, com evolução planejada para **meta-heurísticas (GRASP)**.

---

## 📌 Objetivo

O objetivo do projeto é estudar e implementar métodos heurísticos para resolver o GQAP, um problema clássico de otimização combinatória que envolve:

* Alocação de entidades em localizações
* Restrições de capacidade
* Minimização de custos lineares e custos de interação (fluxo × distância)

---

## 🧠 Metodologia

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

## 📂 Estrutura do Projeto

```
.
├── heuristica.py     # Implementação da heurística gulosa
├── instancias.py     # Geração de instâncias sintéticas
├── experimentos.py   # Execução dos experimentos
├── instancias/       # Conjunto de instâncias geradas (JSON)
├── resultados.txt    # Resultados dos testes
└── main.tex          # Artigo em LaTeX
```

---

## ⚙️ Instâncias

As instâncias são geradas artificialmente com:

* Diferentes tamanhos:

  * Pequeno (5×3)
  * Médio (15×6)
  * Grande (30×10)
* Diferentes níveis de capacidade:

  * Folgada (2.0)
  * Média (1.5)
  * Apertada (1.1)
* Múltiplas sementes para reprodutibilidade

---

## ▶️ Como Executar

1. Gerar instâncias (caso necessário):

```bash
python instancias.py
```

2. Rodar experimentos:

```bash
python experimentos.py
```

---

## 📊 Resultados

Os experimentos geram:

* Tabela de resultados no terminal
* Tabela formatada para LaTeX
* Visualização gráfica (matplotlib)

Os resultados mostram que:

* Instâncias maiores possuem maior custo
* Capacidades mais restritas reduzem a viabilidade
* A heurística é rápida, porém limitada na qualidade da solução

---

## 📄 Artigo Base

O trabalho é inspirado no seguinte artigo:

🔗 https://www.researchgate.net/publication/220403439_GRASP_with_path-relinking_for_the_generalized_quadratic_assignment_problem

---

## 👥 Autores

* Yasmin Souza Lima
* José Guedes

---

## 🚀 Próximos Passos

* Implementação do GRASP
* Inclusão de busca local
* Comparação de desempenho entre métodos
* Testes com instâncias maiores

---

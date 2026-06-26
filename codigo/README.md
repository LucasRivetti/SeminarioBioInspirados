# Seminário de Algoritmos Bioinspirados — Alocação de VMs (VMPACS × NSGA-II)

Implementação do problema **bioobjetivo de alocação de máquinas virtuais** em
nuvem (Gao et al., 2013), resolvido com dois algoritmos bioinspirados
multiobjetivo: **VMPACS** (colônia de formigas) e **NSGA-II** (algoritmo
genético), com comparação por 4 métricas de desempenho.

## Requisitos
- Python 3.8+
- `numpy` e `matplotlib`  → `pip install numpy matplotlib`

## Arquivos (cada um é simples e comentado em português)
| Arquivo | O que faz |
|---|---|
| `problema.py`     | Gera instâncias, avalia os 2 objetivos (energia, desperdício) e a heurística first-fit/FFD. |
| `vmpacs.py`       | Algoritmo de colônia de formigas (VMPACS), fiel ao artigo. |
| `nsga2.py`        | NSGA-II (ordenação não-dominada + crowding) para comparação. |
| `metricas.py`     | Dominância, fronteira de Pareto e métricas: Hipervolume, IGD, ONVG, Spacing. |
| `referencia.py`   | Fronteira de Pareto de referência ("melhor conhecida"): varredura do nº de servidores + busca local de balanceamento. |
| `experimentos.py` | Roda o estudo completo e gera as tabelas (CSV) e figuras (PNG). |

## Como rodar
```bash
# teste rápido de um algoritmo:
python3 vmpacs.py
python3 nsga2.py

# estudo completo (5 níveis de correlação). Roda um nível por vez:
python3 experimentos.py run 0   # correlação P=0.0
python3 experimentos.py run 1   # P=0.25
python3 experimentos.py run 2   # P=0.5
python3 experimentos.py run 3   # P=0.75
python3 experimentos.py run 4   # P=1.0
python3 experimentos.py agg     # junta tudo: gera tabelas e figuras em ../resultados/
```

## Resumo dos resultados
- Com orçamentos equiparados (~1000 avaliações), o **NSGA-II** converge, em geral,
  para soluções de **menor energia e desperdício** (maior Hipervolume, menor IGD).
- O **VMPACS** encontra **mais soluções não-dominadas** (ONVG) em correlações negativas.
- Para estas instâncias os dois objetivos são **quase alinhados** → fronteiras de
  Pareto compactas. Detalhes no relatório (`../relatorio/relatorio.pdf`).

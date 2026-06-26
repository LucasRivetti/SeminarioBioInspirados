# -*- coding: utf-8 -*-
"""
metricas.py
===========
Ferramentas de otimizacao MULTIOBJETIVO:

  - dominancia entre solucoes;
  - extracao da fronteira nao-dominada (fronteira de Pareto aproximada);
  - 4 metricas de desempenho para comparar algoritmos:
        ONVG  (numero de solucoes nao-dominadas)  -> maior e melhor
        SP    (spacing / espacamento)             -> menor e melhor
        HV    (hipervolume)                        -> maior e melhor
        IGD   (inverted generational distance)     -> menor e melhor

Todos os objetivos sao de MINIMIZACAO: (energia, desperdicio).
"""

import numpy as np


# ---------------------------------------------------------------------------
# DOMINANCIA
# ---------------------------------------------------------------------------
def domina(a, b):
    """
    Retorna True se a solucao `a` DOMINA `b` (problema de minimizacao):
    a nao e pior em nenhum objetivo E e estritamente melhor em pelo menos um.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    return np.all(a <= b) and np.any(a < b)


def frente_nao_dominada(pontos):
    """
    Recebe um array (N, 2) de objetivos e devolve os INDICES das solucoes
    nao-dominadas (a fronteira de Pareto aproximada do conjunto).
    """
    pontos = np.asarray(pontos, dtype=float)
    n = len(pontos)
    nao_dom = np.ones(n, dtype=bool)
    for i in range(n):
        if not nao_dom[i]:
            continue
        for j in range(n):
            if i != j and nao_dom[j] and domina(pontos[j], pontos[i]):
                nao_dom[i] = False
                break
    return np.where(nao_dom)[0]


def pontos_nao_dominados(pontos):
    """Mesma ideia, mas devolve diretamente os PONTOS nao-dominados (unicos)."""
    pontos = np.asarray(pontos, dtype=float)
    if len(pontos) == 0:
        return pontos
    idx = frente_nao_dominada(pontos)
    frente = pontos[idx]
    # remove duplicatas
    frente = np.unique(frente, axis=0)
    return frente


# ---------------------------------------------------------------------------
# METRICA 1 - ONVG (Overall Non-dominated Vector Generation)
# ---------------------------------------------------------------------------
def onvg(frente):
    """Numero de solucoes na fronteira (cardinalidade). Maior = melhor."""
    return len(frente)


# ---------------------------------------------------------------------------
# METRICA 2 - SPACING (SP)
# ---------------------------------------------------------------------------
def spacing(frente):
    """
    Mede o quao UNIFORMEMENTE distribuidas estao as solucoes na fronteira.
    d_i = distancia (Manhattan) da solucao i ate a solucao mais proxima.
    SP  = desvio padrao dos d_i.  Quanto MENOR, mais uniforme (melhor).
    """
    frente = np.asarray(frente, dtype=float)
    k = len(frente)
    if k < 2:
        return 0.0
    d = np.empty(k)
    for i in range(k):
        # distancia Manhattan ate as demais solucoes
        dist = np.sum(np.abs(frente - frente[i]), axis=1)
        dist[i] = np.inf
        d[i] = np.min(dist)
    d_medio = np.mean(d)
    return float(np.sqrt(np.sum((d_medio - d) ** 2) / (k - 1)))


# ---------------------------------------------------------------------------
# METRICA 3 - HIPERVOLUME (HV) em 2 objetivos
# ---------------------------------------------------------------------------
def hipervolume(frente, ref):
    """
    Area do espaco de objetivos DOMINADA pela fronteira, medida em relacao a um
    ponto de referencia `ref` (o "pior" canto). Maior = melhor.

    Para 2 objetivos de minimizacao: ordenamos por f1 e somamos faixas.
    """
    frente = np.asarray(frente, dtype=float)
    ref = np.asarray(ref, dtype=float)
    # mantem so pontos que ficam dentro da referencia (dominam o ponto ref)
    dentro = (frente[:, 0] < ref[0]) & (frente[:, 1] < ref[1])
    f = frente[dentro]
    if len(f) == 0:
        return 0.0
    f = f[np.argsort(f[:, 0])]      # ordena por f1 crescente
    hv = 0.0
    prev_y = ref[1]
    for x, y in f:
        hv += (ref[0] - x) * (prev_y - y)
        prev_y = y
    return float(hv)


# ---------------------------------------------------------------------------
# METRICA 4 - IGD (Inverted Generational Distance)
# ---------------------------------------------------------------------------
def igd(frente, referencia):
    """
    Distancia media de cada ponto da fronteira de REFERENCIA ate o ponto mais
    proximo da fronteira obtida. Mede convergencia + cobertura.
    Quanto MENOR, melhor (a fronteira chegou perto da referencia).
    """
    frente = np.asarray(frente, dtype=float)
    referencia = np.asarray(referencia, dtype=float)
    if len(frente) == 0 or len(referencia) == 0:
        return float("inf")
    soma = 0.0
    for z in referencia:
        dist = np.sqrt(np.sum((frente - z) ** 2, axis=1))
        soma += np.min(dist)
    return float(soma / len(referencia))


# ---------------------------------------------------------------------------
# Normalizacao (deixa os 2 objetivos na mesma escala antes de HV/IGD)
# ---------------------------------------------------------------------------
def normalizar(frente, minimos, maximos):
    """Leva cada objetivo para o intervalo [0, 1] usando min/max informados."""
    frente = np.asarray(frente, dtype=float)
    faixa = np.asarray(maximos, dtype=float) - np.asarray(minimos, dtype=float)
    faixa[faixa == 0] = 1.0
    return (frente - minimos) / faixa

# -*- coding: utf-8 -*-
"""
referencia.py
=============
Calcula uma fronteira de Pareto de REFERÊNCIA ("melhor conhecida") para o
problema, por varredura do número de servidores + busca local de
balanceamento. Serve para visualizar o trade-off REAL energia x desperdício
(que é raso), independentemente das metaheurísticas.

Ideia: para cada número-alvo de servidores k, distribui as VMs entre os k
servidores buscando equilibrar CPU e memória (menor desperdício), e refina com
uma busca local. Variando k, traçamos a curva de compromisso.
"""
import numpy as np
from problema import avaliar, num_servidores, first_fit_decreasing
from metricas import pontos_nao_dominados


def aloc_k_bins(perm, k, inst):
    """Distribui as VMs (na ordem `perm`) entre k servidores SEMPRE disponíveis,
    escolhendo, para cada VM, o servidor que fica mais balanceado (|CPU-mem|
    menor). Tende a espalhar as VMs pelos k servidores. Devolve None se não
    couber (k pequeno demais)."""
    cap_c = np.zeros(k); cap_m = np.zeros(k); aloc = np.full(inst.n, -1)
    for i in perm:
        cand = [j for j in range(k)
                if cap_c[j] + inst.Rp[i] <= inst.Tp + 1e-9
                and cap_m[j] + inst.Rm[i] <= inst.Tm + 1e-9]
        if not cand:
            return None
        j = min(cand, key=lambda j: abs((cap_c[j] + inst.Rp[i]) - (cap_m[j] + inst.Rm[i])))
        aloc[i] = j; cap_c[j] += inst.Rp[i]; cap_m[j] += inst.Rm[i]
    return aloc


def busca_local(aloc, inst, iters, rng):
    """Refina uma alocação movendo VMs entre os servidores já usados para
    reduzir o desperdício total (mantém a validade e o número de servidores)."""
    aloc = aloc.copy()
    _, W = avaliar(aloc, inst)
    cap_c = np.zeros(inst.m); cap_m = np.zeros(inst.m)
    np.add.at(cap_c, aloc, inst.Rp); np.add.at(cap_m, aloc, inst.Rm)
    usados = sorted(set(aloc.tolist()))
    for _ in range(iters):
        i = int(rng.integers(inst.n)); j0 = aloc[i]
        melhor, melhorW = j0, W
        for j in usados:
            if j == j0:
                continue
            if cap_c[j] + inst.Rp[i] <= inst.Tp + 1e-9 and cap_m[j] + inst.Rm[i] <= inst.Tm + 1e-9:
                aloc[i] = j
                _, Wn = avaliar(aloc, inst)
                if Wn < melhorW - 1e-9:
                    melhorW, melhor = Wn, j
                aloc[i] = j0
        if melhor != j0:
            cap_c[j0] -= inst.Rp[i]; cap_m[j0] -= inst.Rm[i]
            cap_c[melhor] += inst.Rp[i]; cap_m[melhor] += inst.Rm[i]
            aloc[i] = melhor; W = melhorW
            usados = sorted(set(aloc.tolist()))
    return aloc


def fronteira_referencia(inst, extra=7, restarts=120, iters_local=400, seed=0):
    """Varre k = k_min .. k_min+extra servidores, pega a melhor distribuição de
    cada k (várias tentativas + busca local) e devolve os pontos não-dominados."""
    rng = np.random.default_rng(seed)
    kmin = num_servidores(first_fit_decreasing(inst), inst)
    solucoes = []
    for k in range(kmin, kmin + extra + 1):
        melhor, melhorW = None, np.inf
        for _ in range(restarts):
            a = aloc_k_bins(rng.permutation(inst.n), k, inst)
            if a is None:
                continue
            _, w = avaliar(a, inst)
            if w < melhorW:
                melhorW, melhor = w, a
        if melhor is not None:
            melhor = busca_local(melhor, inst, iters_local, rng)
            solucoes.append(avaliar(melhor, inst))
    return pontos_nao_dominados(np.array(solucoes))


if __name__ == "__main__":
    from problema import gerar_instancia
    for P in [0.0, 0.5, 1.0]:
        inst = gerar_instancia(n=100, P=P, seed=100 + int(P * 100))
        fr = fronteira_referencia(inst)
        const = (inst.P_busy - inst.P_idle) * inst.total_cpu
        print(f"P={P}: {len(fr)} pontos")
        for e, w in sorted(fr.tolist()):
            print(f"   {int(round((e-const)/inst.P_idle))} serv  E={e:.0f}  W={w:.3f}")

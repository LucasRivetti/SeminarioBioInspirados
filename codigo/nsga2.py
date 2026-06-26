# -*- coding: utf-8 -*-
"""
nsga2.py
========
NSGA-II aplicado ao problema de alocacao de VMs, para COMPARAR com o VMPACS
(o artigo compara o VMPACS com um algoritmo genetico, o MGGA).

NSGA-II e um algoritmo genetico (bioinspirado) com dois ingredientes:
  (1) ordenacao por nao-dominancia (separa a populacao em "frentes" de Pareto);
  (2) distancia de multidao (crowding), que mantem as solucoes espalhadas.

Codificacao por PERMUTACAO: cada individuo e uma ordem das VMs. Para avaliar,
decodificamos com o first-fit (cada VM no primeiro servidor onde cabe). Isso
garante solucoes sempre validas e bem empacotadas. Operadores: Order
Crossover (OX) e mutacao por troca (swap).
"""
import numpy as np
from problema import avaliar, first_fit
from metricas import domina


def decodificar(perm, inst):
    aloc = first_fit(perm, inst)
    return aloc, np.array(avaliar(aloc, inst))


def ordenacao_nao_dominada(objs):
    n = len(objs); S = [[] for _ in range(n)]; cont = np.zeros(n, dtype=int)
    frentes = [[]]
    for p in range(n):
        for q in range(n):
            if p == q: continue
            if domina(objs[p], objs[q]): S[p].append(q)
            elif domina(objs[q], objs[p]): cont[p] += 1
        if cont[p] == 0: frentes[0].append(p)
    i = 0
    while frentes[i]:
        prox = []
        for p in frentes[i]:
            for q in S[p]:
                cont[q] -= 1
                if cont[q] == 0: prox.append(q)
        i += 1; frentes.append(prox)
    frentes.pop()
    return frentes


def distancia_multidao(objs, frente):
    l = len(frente); dist = {i: 0.0 for i in frente}
    if l == 0: return dist
    objs_f = objs[frente]
    for obj in range(objs.shape[1]):
        ordem = np.argsort(objs_f[:, obj]); idx_ord = [frente[k] for k in ordem]
        dist[idx_ord[0]] = float("inf"); dist[idx_ord[-1]] = float("inf")
        faixa = objs_f[ordem[-1], obj] - objs_f[ordem[0], obj]
        if faixa == 0: continue
        for k in range(1, l - 1):
            dist[idx_ord[k]] += (objs_f[ordem[k+1], obj] - objs_f[ordem[k-1], obj]) / faixa
    return dist


def torneio(rank, dist, rng):
    a, b = rng.integers(0, len(rank), size=2)
    if rank[a] < rank[b]: return a
    if rank[b] < rank[a]: return b
    return a if dist[a] >= dist[b] else b


def crossover_ox(p1, p2, rng):
    """Order Crossover: mantem uma fatia de p1 e completa na ordem de p2."""
    n = len(p1); i, j = sorted(rng.integers(0, n, size=2))
    filho = np.full(n, -1, dtype=int); filho[i:j+1] = p1[i:j+1]
    contidos = set(p1[i:j+1].tolist()); pos = (j + 1) % n
    for k in range(n):
        gene = p2[(j + 1 + k) % n]
        if gene not in contidos:
            filho[pos] = gene; pos = (pos + 1) % n
    return filho


def mutacao_swap(perm, taxa, rng):
    perm = perm.copy()
    if rng.random() < taxa:
        i, j = rng.integers(0, len(perm), size=2)
        perm[i], perm[j] = perm[j], perm[i]
    return perm


def nsga2(inst, pop=60, geracoes=40, taxa_mut=0.4, seed=None, verbose=False):
    rng = np.random.default_rng(seed); n = inst.n
    P = [rng.permutation(n) for _ in range(pop)]
    objs = np.array([decodificar(ind, inst)[1] for ind in P])
    for g in range(geracoes):
        frentes = ordenacao_nao_dominada(objs)
        rank = np.zeros(pop, dtype=int); dist = np.zeros(pop)
        for r, fr in enumerate(frentes):
            d = distancia_multidao(objs, fr)
            for i in fr: rank[i], dist[i] = r, d[i]
        filhos = []
        while len(filhos) < pop:
            pai1 = P[torneio(rank, dist, rng)]; pai2 = P[torneio(rank, dist, rng)]
            filho = mutacao_swap(crossover_ox(pai1, pai2, rng), taxa_mut, rng)
            filhos.append(filho)
        objs_f = np.array([decodificar(ind, inst)[1] for ind in filhos])
        R = P + filhos; objs_R = np.vstack([objs, objs_f])
        frentes = ordenacao_nao_dominada(objs_R); nova_P, nova_objs = [], []
        for fr in frentes:
            if len(nova_P) + len(fr) <= pop:
                for i in fr: nova_P.append(R[i]); nova_objs.append(objs_R[i])
            else:
                d = distancia_multidao(objs_R, fr)
                for i in sorted(fr, key=lambda i: d[i], reverse=True)[:pop - len(nova_P)]:
                    nova_P.append(R[i]); nova_objs.append(objs_R[i])
                break
        P, objs = nova_P, np.array(nova_objs)
        if verbose and (g % 10 == 0 or g == geracoes - 1):
            print(f"  [NSGA-II] geracao {g+1}/{geracoes}", flush=True)
    idx = ordenacao_nao_dominada(objs)[0]
    vistos, obj_u, aloc_u = set(), [], []
    for i in idx:
        chave = (round(objs[i, 0], 4), round(objs[i, 1], 6))
        if chave not in vistos:
            vistos.add(chave); obj_u.append(objs[i])
            aloc_u.append(first_fit(P[i], inst))
    return np.array(obj_u), aloc_u


if __name__ == "__main__":
    import time
    from problema import gerar_instancia
    from metricas import pontos_nao_dominados
    from vmpacs import vmpacs
    inst = gerar_instancia(n=100, P=0.5, seed=42)
    pv, pn = [], []
    t=time.time()
    for r in range(12):
        ov,_ = vmpacs(inst, NA=10, M=100, seed=r)
        on,_ = nsga2(inst, pop=60, geracoes=40, seed=r)
        pv.append(ov); pn.append(on)
    fv = pontos_nao_dominados(np.vstack(pv)); fn = pontos_nao_dominados(np.vstack(pn))
    const=(215-162)*inst.total_cpu
    print(f"tempo {time.time()-t:.1f}s")
    print("VMPACS pooled front:", len(fv), "pontos")
    for p in sorted(fv.tolist()): print(f"   E={p[0]:.0f} ({int(round((p[0]-const)/162))} serv)  W={p[1]:.3f}")
    print("NSGA pooled front:", len(fn), "pontos")
    for p in sorted(fn.tolist()): print(f"   E={p[0]:.0f} ({int(round((p[0]-const)/162))} serv)  W={p[1]:.3f}")

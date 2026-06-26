# -*- coding: utf-8 -*-
"""
problema.py
===========
Problema BIOBJETIVO de Alocacao de Maquinas Virtuais (VM Placement)
baseado em Gao et al. (2013) - "A multi-objective ant colony system
algorithm for virtual machine placement in cloud computing".

A ideia e simples:
  - Temos n maquinas virtuais (VMs), cada uma com uma demanda de CPU e de
    memoria (valores entre 0 e 1, ou seja, fracao da capacidade de 1 servidor).
  - Temos m servidores fisicos identicos. Cada servidor so pode receber VMs
    ate um limite (threshold) de CPU e de memoria.
  - Precisamos decidir EM QUAL servidor colocar cada VM.

Queremos minimizar AO MESMO TEMPO dois objetivos que estao em conflito:
  (f1) Consumo de energia  -> usar menos servidores gasta menos energia.
  (f2) Desperdicio de recursos -> deixar CPU/memoria sobrando de forma
       desbalanceada e ruim.

Uma "solucao" e representada por um vetor `aloc` de tamanho n:
    aloc[i] = indice do servidor que recebe a VM i.
"""

import numpy as np


class Instancia:
    """Guarda todos os dados de uma instancia do problema."""

    def __init__(self, Rp, Rm, m, Tp=0.9, Tm=0.9,
                 P_idle=162.0, P_busy=215.0, eps=1e-4):
        self.Rp = np.asarray(Rp, dtype=float)   # demanda de CPU de cada VM
        self.Rm = np.asarray(Rm, dtype=float)   # demanda de memoria de cada VM
        self.n = len(self.Rp)                   # numero de VMs
        self.m = m                              # numero de servidores disponiveis
        self.Tp = Tp                            # limite de uso de CPU por servidor
        self.Tm = Tm                            # limite de uso de memoria por servidor
        self.P_idle = P_idle                    # potencia do servidor ocioso (W)
        self.P_busy = P_busy                    # potencia do servidor em uso pleno (W)
        self.eps = eps                          # constante pequena (evita divisao por 0)
        self.total_cpu = float(np.sum(self.Rp)) # CPU total exigida (constante da instancia)


# ---------------------------------------------------------------------------
# 1) GERACAO DE INSTANCIAS (gerador correlacionado do artigo, Secao 5)
# ---------------------------------------------------------------------------
def gerar_instancia(n, P, Rp_ref=0.25, Rm_ref=0.25, m=None, seed=None):
    """
    Gera uma instancia com correlacao controlada entre CPU e memoria.

    Reproduz o procedimento do artigo:
        Rp_i = rand(2*Rp_ref)            # CPU em [0, 2*Rp_ref)
        Rm_i = rand(Rm_ref)              # memoria em [0, Rm_ref)
        se (r<P e Rp_i>=Rp_ref) ou (r>=P e Rp_i<Rp_ref):  Rm_i += Rm_ref

    O parametro P (entre 0 e 1) controla a correlacao:
      P proximo de 0   -> correlacao NEGATIVA forte (CPU alta combina com mem. baixa)
      P proximo de 0.5 -> sem correlacao
      P proximo de 1   -> correlacao POSITIVA forte (CPU alta combina com mem. alta)

    `m` (servidores) por padrao = n  (pior caso: 1 VM por servidor).
    """
    rng = np.random.default_rng(seed)
    Rp = np.empty(n)
    Rm = np.empty(n)
    for i in range(n):
        Rp[i] = rng.random() * (2 * Rp_ref)     # rand(2*Rp_ref)
        Rm[i] = rng.random() * Rm_ref           # rand(Rm_ref)
        r = rng.random()                        # rand(1.0)
        if (r < P and Rp[i] >= Rp_ref) or (r >= P and Rp[i] < Rp_ref):
            Rm[i] = Rm[i] + Rm_ref
    if m is None:
        m = n
    return Instancia(Rp, Rm, m)


# ---------------------------------------------------------------------------
# 2) AVALIACAO DOS DOIS OBJETIVOS
# ---------------------------------------------------------------------------
def avaliar(aloc, inst):
    """
    Recebe uma alocacao (vetor aloc) e devolve (energia, desperdicio).

    Para cada servidor EM USO j:
        Up_j = soma das CPUs das VMs nele     (utilizacao de CPU)
        Um_j = soma das memorias das VMs nele  (utilizacao de memoria)

      Energia (Eq. 1):  P_j = (P_busy - P_idle) * Up_j + P_idle
        Somando sobre os k servidores em uso e como a soma de TODAS as CPUs e
        constante (total_cpu), a energia total e exatamente:
            E = (P_busy - P_idle) * total_cpu + P_idle * k
        ou seja, depende so do NUMERO de servidores ligados (k). Calcular assim
        evita ruido numerico e deixa o vinculo energia<->servidores explicito.

      Desperdicio (Secao 3.1 / 3.3):
        Lp_j = Tp - Up_j ;  Lm_j = Tm - Um_j
        W_j = (|Lp_j - Lm_j| + eps) / (Up_j + Um_j)
    """
    aloc = np.asarray(aloc)
    usado_cpu = np.zeros(inst.m)
    usado_mem = np.zeros(inst.m)
    np.add.at(usado_cpu, aloc, inst.Rp)
    np.add.at(usado_mem, aloc, inst.Rm)
    em_uso = usado_cpu > 0                 # servidores com pelo menos 1 VM
    k = int(np.count_nonzero(em_uso))      # numero de servidores ligados

    # ---- Objetivo 1: energia (forma exata) ----
    energia = (inst.P_busy - inst.P_idle) * inst.total_cpu + inst.P_idle * k

    # ---- Objetivo 2: desperdicio ----
    Lp = inst.Tp - usado_cpu[em_uso]
    Lm = inst.Tm - usado_mem[em_uso]
    W_j = (np.abs(Lp - Lm) + inst.eps) / (usado_cpu[em_uso] + usado_mem[em_uso])
    desperdicio = float(np.sum(W_j))

    return float(energia), round(desperdicio, 9)


def num_servidores(aloc, inst):
    """Quantos servidores foram efetivamente usados pela alocacao."""
    return int(len(np.unique(np.asarray(aloc))))


def potencia_normalizada(aloc, inst):
    """
    P'(S) = soma_j (P_j / P_max_j), com P_max_j = P_busy (potencia de pico).
    Usada para calibrar o feromonio inicial do VMPACS (tau_0).
    """
    aloc = np.asarray(aloc)
    usado_cpu = np.zeros(inst.m)
    np.add.at(usado_cpu, aloc, inst.Rp)
    em_uso = usado_cpu > 0
    P_j = (inst.P_busy - inst.P_idle) * usado_cpu[em_uso] + inst.P_idle
    return float(np.sum(P_j / inst.P_busy))


# ---------------------------------------------------------------------------
# 3) HEURISTICA FIRST-FIT (usada pelo NSGA-II como decodificador e pelo FFD)
# ---------------------------------------------------------------------------
def cabe(servidor_cpu, servidor_mem, rp, rm, inst):
    """Verifica se uma VM (rp, rm) cabe em um servidor sem furar o limite."""
    return (servidor_cpu + rp <= inst.Tp + 1e-12) and \
           (servidor_mem + rm <= inst.Tm + 1e-12)


def first_fit(ordem, inst):
    """
    Coloca as VMs na ordem dada, cada uma no PRIMEIRO servidor aberto onde ela
    cabe; se nao couber em nenhum, abre um servidor novo. Sempre gera solucao
    valida (respeita os limites de CPU e memoria).
    """
    cap_cpu = []
    cap_mem = []
    aloc = np.empty(inst.n, dtype=int)
    for i in ordem:
        colocado = False
        for j in range(len(cap_cpu)):
            if cabe(cap_cpu[j], cap_mem[j], inst.Rp[i], inst.Rm[i], inst):
                cap_cpu[j] += inst.Rp[i]
                cap_mem[j] += inst.Rm[i]
                aloc[i] = j
                colocado = True
                break
        if not colocado:
            aloc[i] = len(cap_cpu)
            cap_cpu.append(inst.Rp[i])
            cap_mem.append(inst.Rm[i])
    return aloc


def first_fit_decreasing(inst):
    """
    FFD: ordena as VMs pela demanda total (CPU+memoria) decrescente e aplica o
    first-fit. Heuristica classica de empacotamento, usada no artigo para gerar
    a solucao inicial S0.
    """
    ordem = np.argsort(-(inst.Rp + inst.Rm))
    return first_fit(ordem, inst)


if __name__ == "__main__":
    inst = gerar_instancia(n=50, P=0.5, seed=1)
    aloc = first_fit_decreasing(inst)
    energia, desperdicio = avaliar(aloc, inst)
    print(f"VMs={inst.n}  servidores usados (FFD)={num_servidores(aloc, inst)}")
    print(f"Energia={energia:.2f} W   Desperdicio={desperdicio:.4f}")
    print(f"Potencia normalizada P'(S0)={potencia_normalizada(aloc, inst):.4f}")

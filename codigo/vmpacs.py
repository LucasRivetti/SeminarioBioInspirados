# -*- coding: utf-8 -*-
"""
vmpacs.py
=========
VMPACS - Virtual Machine Placement Ant Colony System
Implementacao fiel ao artigo de Gao et al. (2013).

E uma COLONIA DE FORMIGAS (bioinspirado). Cada "formiga" constroi uma alocacao
de VMs em servidores. Formigas boas deixam mais "feromonio" nos movimentos
(VM -> servidor) que usaram, e isso guia as proximas formigas.

Como o problema tem DOIS objetivos, guardamos as melhores solucoes
nao-dominadas num "arquivo externo" (a fronteira de Pareto).

Ideia geral de cada formiga (Fig. 2 do artigo):
  - abre um servidor;
  - enche esse servidor escolhendo VMs por uma regra que combina
    FEROMONIO (tau) + HEURISTICA (eta);
  - quando nao cabe mais nada, abre o proximo servidor;
  - repete ate alocar todas as VMs.
"""

import numpy as np
from problema import avaliar, potencia_normalizada, first_fit_decreasing
from metricas import domina


# ---------------------------------------------------------------------------
# CONSTRUCAO DE UMA SOLUCAO POR UMA FORMIGA
# ---------------------------------------------------------------------------
def construir_solucao(inst, tau, alpha, q0, rho_l, tau0, rng):
    """
    Uma formiga monta uma alocacao completa.

    tau[i, j] = feromonio do movimento "colocar a VM i no j-esimo servidor aberto".
    Devolve o vetor `aloc` (aloc[i] = servidor da VM i).
    """
    n, m = inst.n, inst.m
    Rp, Rm = inst.Rp, inst.Rm
    Tp, Tm = inst.Tp, inst.Tm
    Pidle, Pbusy, eps = inst.P_idle, inst.P_busy, inst.eps

    disp = np.ones(n, dtype=bool)        # VMs ainda nao alocadas
    aloc = np.full(n, -1, dtype=int)

    soma_P_ant = 0.0   # soma de P_v/Pbusy dos servidores JA fechados
    soma_W_ant = 0.0   # soma de W_v       dos servidores JA fechados

    host = 0
    while disp.any():
        # ---- abre um novo servidor (host) ----
        host_cpu = 0.0
        host_mem = 0.0
        while True:
            # candidatas: VMs disponiveis que CABEM no servidor atual
            cand = np.where(disp &
                            (host_cpu + Rp <= Tp + 1e-12) &
                            (host_mem + Rm <= Tm + 1e-12))[0]
            if len(cand) == 0:
                break

            # ---- HEURISTICA eta (Eq. 6): contribuicao parcial aos 2 objetivos ----
            novo_cpu = host_cpu + Rp[cand]
            novo_mem = host_mem + Rm[cand]
            Pj = (Pbusy - Pidle) * novo_cpu + Pidle              # energia do host com a VM
            eta1 = 1.0 / (eps + soma_P_ant + Pj / Pbusy)         # objetivo 1
            Lp = Tp - novo_cpu
            Lm = Tm - novo_mem
            Wj = (np.abs(Lp - Lm) + eps) / (novo_cpu + novo_mem)  # desperdicio do host
            eta2 = 1.0 / (eps + soma_W_ant + Wj)                 # objetivo 2
            eta = eta1 + eta2

            # ---- combinacao FEROMONIO + HEURISTICA (Eq. 7) ----
            tau_c = tau[cand, host]
            score = alpha * tau_c + (1.0 - alpha) * eta

            # ---- regra pseudo-aleatoria proporcional (Sec. 4.2) ----
            q = rng.random()
            if q <= q0:
                escolhida = cand[np.argmax(score)]       # exploitation
            else:
                prob = score / score.sum()               # exploration
                escolhida = rng.choice(cand, p=prob)

            # ---- aplica o movimento ----
            aloc[escolhida] = host
            host_cpu += Rp[escolhida]
            host_mem += Rm[escolhida]
            disp[escolhida] = False

            # ---- atualizacao LOCAL do feromonio (Eq. 8) ----
            tau[escolhida, host] = (1.0 - rho_l) * tau[escolhida, host] + rho_l * tau0

        # ---- fecha o servidor: acumula sua energia e seu desperdicio ----
        if host_cpu > 0:
            Pv = (Pbusy - Pidle) * host_cpu + Pidle
            soma_P_ant += Pv / Pbusy
            Lp = Tp - host_cpu
            Lm = Tm - host_mem
            soma_W_ant += (abs(Lp - Lm) + eps) / (host_cpu + host_mem)
        host += 1

    return aloc


# ---------------------------------------------------------------------------
# ARQUIVO EXTERNO (fronteira de Pareto)
# ---------------------------------------------------------------------------
def atualizar_arquivo(arquivo, objs, aloc, iteracao):
    """
    Tenta inserir uma solucao no arquivo de nao-dominadas.
    Cada item do arquivo = dict(objs, aloc, nis) onde nis = iteracao de entrada.
    Retorna True se a solucao foi inserida.
    """
    for item in arquivo:
        if domina(item["objs"], objs) or np.array_equal(item["objs"], objs):
            return False            # ja existe alguem igual ou melhor
    # remove os que a nova solucao domina
    arquivo[:] = [it for it in arquivo if not domina(objs, it["objs"])]
    arquivo.append({"objs": np.array(objs), "aloc": aloc.copy(), "nis": iteracao})
    return True


# ---------------------------------------------------------------------------
# ALGORITMO PRINCIPAL
# ---------------------------------------------------------------------------
def vmpacs(inst, NA=10, M=100, alpha=0.45, rho_l=0.35, rho_g=0.35, q0=0.8,
           seed=None, verbose=False):
    """
    Executa o VMPACS e devolve:
      objetivos  -> array (k, 2) com (energia, desperdicio) das solucoes de Pareto
      alocacoes  -> lista com os vetores aloc correspondentes

    Parametros padrao = os do artigo: NA=10, M=100, alpha=0.45,
    rho_l=rho_g=0.35, q0=0.8.
    """
    rng = np.random.default_rng(seed)
    n, m = inst.n, inst.m

    # ---- feromonio inicial tau0 = 1 / [n * (P'(S0) + W(S0))], S0 = solucao FFD ----
    S0 = first_fit_decreasing(inst)
    _, W_S0 = avaliar(S0, inst)
    P_S0 = potencia_normalizada(S0, inst)
    tau0 = 1.0 / (n * (P_S0 + W_S0))
    tau = np.full((n, m), tau0)

    arquivo = []   # fronteira de Pareto (arquivo externo)

    for t in range(1, M + 1):
        # ---- cada formiga constroi uma solucao ----
        soat = []
        for _ in range(NA):
            aloc = construir_solucao(inst, tau, alpha, q0, rho_l, tau0, rng)
            objs = np.array(avaliar(aloc, inst))
            soat.append((objs, aloc))
            atualizar_arquivo(arquivo, objs, aloc, t)

        # ---- atualizacao GLOBAL do feromonio (Eq. 9 e 10) ----
        # so as solucoes nao-dominadas (do arquivo) reforcam feromonio
        for item in arquivo:
            S_aloc = item["aloc"]
            P_S = potencia_normalizada(S_aloc, inst)
            _, W_S = avaliar(S_aloc, inst)
            lam = NA / (t - item["nis"] + 1)                     # Eq. (10)
            reforco = rho_g * lam / (P_S + W_S)
            # reforca os movimentos (i, host) que construiram a solucao
            for i in range(n):
                j = S_aloc[i]
                tau[i, j] = (1.0 - rho_g) * tau[i, j] + reforco

        if verbose and (t % 20 == 0 or t == M):
            print(f"  [VMPACS] iteracao {t}/{M}  |arquivo|={len(arquivo)}")

    objetivos = np.array([it["objs"] for it in arquivo])
    alocacoes = [it["aloc"] for it in arquivo]
    return objetivos, alocacoes


if __name__ == "__main__":
    from problema import gerar_instancia, num_servidores
    inst = gerar_instancia(n=60, P=0.5, seed=7)
    objs, alocs = vmpacs(inst, NA=10, M=40, seed=1, verbose=True)
    print(f"\nSolucoes de Pareto encontradas: {len(objs)}")
    ordem = np.argsort(objs[:, 0])
    for k in ordem:
        print(f"  energia={objs[k,0]:8.1f} W | desperdicio={objs[k,1]:7.3f} "
              f"| servidores={num_servidores(alocs[k], inst)}")

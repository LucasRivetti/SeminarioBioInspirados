# -*- coding: utf-8 -*-
"""
experimentos.py  -- estudo comparativo VMPACS x NSGA-II (Gao et al., 2013).
Uso:
    python3 experimentos.py run <idx>   # roda 1 nivel de correlacao e salva parcial
    python3 experimentos.py agg         # junta os parciais -> tabelas e figuras

n=100 VMs, 5 niveis de correlacao, R repeticoes. Metricas multiobjetivo:
Hipervolume, Spacing, ONVG, IGD; e indicadores: energia, desperdicio, servidores.
"""
import os, sys, pickle, time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from problema import gerar_instancia
from vmpacs import vmpacs
from nsga2 import nsga2
from metricas import pontos_nao_dominados, hipervolume, spacing, onvg, igd, normalizar

N_VMS = 100
R = 10
CORRELACOES = [0.0, 0.25, 0.5, 0.75, 1.0]
COEF_CORR = {0.0: -0.75, 0.25: -0.35, 0.5: -0.07, 0.75: 0.37, 1.0: 0.75}
PAR_VMPACS = dict(NA=10, M=100, alpha=0.45, rho_l=0.35, rho_g=0.35, q0=0.8)
PAR_NSGA = dict(pop=50, geracoes=20, taxa_mut=0.4)

PASTA = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(PASTA, "resultados")
FIG = os.path.join(RES, "figuras")
os.makedirs(FIG, exist_ok=True)


def serv_de_energia(E, inst):
    return int(round((E - (inst.P_busy - inst.P_idle) * inst.total_cpu) / inst.P_idle))


def run_one(idx):
    P = CORRELACOES[idx]
    inst = gerar_instancia(n=N_VMS, P=P, seed=100 + int(P * 100))
    fronts = {"VMPACS": [], "NSGA-II": []}
    tempos = {"VMPACS": [], "NSGA-II": []}
    t0 = time.time()
    for r in range(R):
        t = time.time(); ov, _ = vmpacs(inst, seed=r, **PAR_VMPACS)
        tempos["VMPACS"].append(time.time() - t); fronts["VMPACS"].append(ov)
        t = time.time(); on, _ = nsga2(inst, seed=r, **PAR_NSGA)
        tempos["NSGA-II"].append(time.time() - t); fronts["NSGA-II"].append(on)

    uniao = np.vstack([f for alg in fronts for f in fronts[alg]])
    ref_front = pontos_nao_dominados(uniao)
    mins, maxs = uniao.min(axis=0), uniao.max(axis=0)
    ref_norm = normalizar(ref_front, mins, maxs)
    ref_point = np.array([1.1, 1.1])

    dados_alg = {}
    for alg in fronts:
        HV, SP, NG, IG, Emin, Wmin, Serv = [], [], [], [], [], [], []
        for fr in fronts[alg]:
            frn = normalizar(fr, mins, maxs)
            HV.append(hipervolume(frn, ref_point)); SP.append(spacing(frn))
            NG.append(onvg(fr)); IG.append(igd(frn, ref_norm))
            Emin.append(fr[:, 0].min()); Wmin.append(fr[:, 1].min())
            Serv.append(serv_de_energia(fr[:, 0].min(), inst))
        dados_alg[alg] = dict(
            HV=np.array(HV), SP=np.array(SP), ONVG=np.array(NG), IGD=np.array(IG),
            Emin=np.array(Emin), Wmin=np.array(Wmin), Serv=np.array(Serv),
            tempo=np.array(tempos[alg]),
            pooled=pontos_nao_dominados(np.vstack(fronts[alg])))
    parcial = dict(P=P, total_cpu=inst.total_cpu, mins=mins, maxs=maxs,
                   ref_front=ref_front, alg=dados_alg)
    with open(os.path.join(RES, f"parcial_{idx}.pkl"), "wb") as f:
        pickle.dump(parcial, f)
    print(f"P={P} pronto em {time.time()-t0:.1f}s", flush=True)
    for alg in fronts:
        d = dados_alg[alg]
        print(f"  [{alg}] HV={d['HV'].mean():.3f} SP={d['SP'].mean():.3f} "
              f"ONVG={d['ONVG'].mean():.1f} IGD={d['IGD'].mean():.3f} "
              f"E={d['Emin'].mean():.0f} W={d['Wmin'].mean():.3f} serv={d['Serv'].mean():.1f}", flush=True)


# ------------------------------- agregacao ---------------------------------
COR = {"VMPACS": "#c0392b", "NSGA-II": "#2c3e50"}
def _ms(v): return f"{np.mean(v):.3f} ± {np.std(v):.3f}"

def agg():
    res = {}
    for idx in range(len(CORRELACOES)):
        with open(os.path.join(RES, f"parcial_{idx}.pkl"), "rb") as f:
            d = pickle.load(f); res[d["P"]] = d

    with open(os.path.join(RES, "tabela1_onvg_sp.csv"), "w") as f:
        f.write("Correlacao,Coef,Algoritmo,ONVG,Spacing\n")
        for P in CORRELACOES:
            for alg in ["VMPACS", "NSGA-II"]:
                d = res[P]["alg"][alg]
                f.write(f"{P},{COEF_CORR[P]},{alg},{_ms(d['ONVG'])},{_ms(d['SP'])}\n")
    with open(os.path.join(RES, "tabela2_energia_desperdicio.csv"), "w") as f:
        f.write("Correlacao,Coef,Algoritmo,Energia(W),Desperdicio,Servidores\n")
        for P in CORRELACOES:
            for alg in ["VMPACS", "NSGA-II"]:
                d = res[P]["alg"][alg]
                f.write(f"{P},{COEF_CORR[P]},{alg},{_ms(d['Emin'])},{_ms(d['Wmin'])},{_ms(d['Serv'])}\n")
    with open(os.path.join(RES, "tabela3_hv_igd.csv"), "w") as f:
        f.write("Correlacao,Coef,Algoritmo,Hipervolume,IGD,Tempo(s)\n")
        for P in CORRELACOES:
            for alg in ["VMPACS", "NSGA-II"]:
                d = res[P]["alg"][alg]
                f.write(f"{P},{COEF_CORR[P]},{alg},{_ms(d['HV'])},{_ms(d['IGD'])},{_ms(d['tempo'])}\n")

    xs = np.arange(len(CORRELACOES)); rot = [f"{P}\n({COEF_CORR[P]})" for P in CORRELACOES]
    def barras(metric, titulo, ylabel, arquivo, nota):
        fig, ax = plt.subplots(figsize=(7, 4)); w = 0.38
        for k, alg in enumerate(["VMPACS", "NSGA-II"]):
            m = [np.mean(res[P]["alg"][alg][metric]) for P in CORRELACOES]
            s = [np.std(res[P]["alg"][alg][metric]) for P in CORRELACOES]
            ax.bar(xs + (k - 0.5) * w, m, w, yerr=s, capsize=3, label=alg, color=COR[alg], alpha=0.9)
        ax.set_xticks(xs); ax.set_xticklabels(rot, fontsize=9)
        ax.set_xlabel("Correlacao P (coef. aprox.)"); ax.set_ylabel(ylabel); ax.set_title(titulo)
        ax.legend(); ax.grid(axis="y", alpha=0.3)
        ax.annotate(nota, xy=(0.02, 0.96), xycoords="axes fraction", fontsize=8, va="top", color="gray")
        fig.tight_layout(); fig.savefig(os.path.join(FIG, arquivo), dpi=130); plt.close(fig)
    barras("Emin", "Consumo de energia (menor = melhor)", "Energia (W)", "energia_barras.png", "menor e melhor")
    barras("Wmin", "Desperdicio de recursos (menor = melhor)", "Desperdicio", "desperdicio_barras.png", "menor e melhor")
    barras("Serv", "Numero de servidores usados", "Servidores", "servidores_barras.png", "menor e melhor")
    barras("HV", "Hipervolume (maior = melhor)", "Hipervolume (norm.)", "hipervolume_barras.png", "maior e melhor")
    barras("IGD", "IGD (menor = melhor)", "IGD (norm.)", "igd_barras.png", "menor e melhor")

    fig, axs = plt.subplots(1, 3, figsize=(13, 4))
    for ax, P in zip(axs, [0.0, 0.5, 1.0]):
        for alg in ["VMPACS", "NSGA-II"]:
            fr = res[P]["alg"][alg]["pooled"]; fr = fr[np.argsort(fr[:, 0])]
            ax.plot(fr[:, 0], fr[:, 1], "o-", color=COR[alg], label=alg, ms=7, alpha=0.85)
        ax.set_title(f"P = {P}  (coef ~ {COEF_CORR[P]})"); ax.set_xlabel("Energia (W)")
        ax.set_ylabel("Desperdicio"); ax.grid(alpha=0.3); ax.legend()
    fig.suptitle("Fronteiras de Pareto (uniao das repeticoes) — canto inferior-esquerdo e melhor")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "fronteiras_pareto.png"), dpi=130); plt.close(fig)
    print("Agregacao concluida: 3 tabelas + 6 figuras.", flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run_one(int(sys.argv[2]))
    else:
        agg()

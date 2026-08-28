# coding=UTF-8
"""
Experimento comparativo para 0/1 Knapsack.

Compara el algoritmo NUEVO LAHC contra tres algoritmos binarios ya presentes
en MHP: Genetic Algorithm (GA), Simulated Annealing (SA) y Random Walk (RW).
Todas las series usan el mismo numero de evaluaciones y corridas.

Ejemplos:
    python ExecuteKnapsack.py --quiet
    python ExecuteKnapsack.py --full --evals 10000 --runs 10 --quiet
    python ExecuteKnapsack.py --history --quiet
    python ExecuteKnapsack.py --full --stats --quiet
"""

import contextlib
import copy
import csv
import io
import os
import sys
import numpy as np

if "--headless" in sys.argv or "--quiet" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")

from agent.Agent import Agent
from examples.KnapsackProblem import KnapsackProblem
from statisticc.Reporter import getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm

INSTDIR = "./DATA/instances/KNAPSACK"
INSTANCES_FULL = ["kp60_%02d" % k for k in range(1, 11)]

SERIES = [
    ("LAHC", "LAHC100"),  # algoritmo nuevo; calibrado con --history
    ("GA",   "GAKP"),     # algoritmo existente
    ("SA",   "SAKP"),     # algoritmo existente
    ("RW",   "RWKP"),     # linea base existente
]

N_INSTANCES = 5
N_EVALS = 2000
N_RUNS = 3
QUIET = False
DO_STATS = False
OUTPUT = "./DATA/output/knapsack_comparison.csv"


def load_optima():
    optima = {}
    path = os.path.join(INSTDIR, "opt", "optimums.txt")
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) == 2:
                optima[parts[0]] = int(parts[1])
    return optima


def read_args():
    global N_INSTANCES, N_EVALS, N_RUNS, QUIET, DO_STATS, OUTPUT, SERIES

    if "--full" in sys.argv:
        N_INSTANCES = 10
    if "--quiet" in sys.argv:
        QUIET = True
    if "--stats" in sys.argv:
        DO_STATS = True

    if "--history" in sys.argv:
        SERIES = [
            ("LAHC", "LAHC20"),
            ("LAHC", "LAHC100"),
            ("LAHC", "LAHC200"),
            ("LAHC", "LAHC500"),
        ]

    for i, arg in enumerate(sys.argv):
        if arg == "--instances" and i + 1 < len(sys.argv):
            N_INSTANCES = int(sys.argv[i + 1])
        elif arg == "--evals" and i + 1 < len(sys.argv):
            N_EVALS = int(sys.argv[i + 1])
        elif arg == "--runs" and i + 1 < len(sys.argv):
            N_RUNS = int(sys.argv[i + 1])
        elif arg == "--output" and i + 1 < len(sys.argv):
            OUTPUT = sys.argv[i + 1]

    N_INSTANCES = max(1, min(N_INSTANCES, len(INSTANCES_FULL)))


def run_agent(problem, method, config, seed):
    np.random.seed(seed)
    agent = Agent(problem, [method, config, N_EVALS, N_RUNS])
    if QUIET:
        with contextlib.redirect_stdout(io.StringIO()):
            agent.init()
    else:
        agent.init()
    return agent


def main():
    read_args()
    optima = load_optima()
    instances = INSTANCES_FULL[:N_INSTANCES]

    print("============================================================")
    print(" 0/1 KNAPSACK :: comparacion de metaheuristicas")
    print(" Nuevo algoritmo       : LAHC (Late Acceptance Hill Climbing)")
    print(" Instancias             :", len(instances))
    print(" Series                 :", [m + "/" + c for m, c in SERIES])
    print(" Corridas por serie     :", N_RUNS)
    print(" Evaluaciones/corrida   :", N_EVALS)
    print(" Referencia             : optimo exacto por programacion dinamica")
    print("============================================================")

    rows = []
    stats_for_friedman = []
    names_for_friedman = []
    gaps_by_series = {m + "/" + c: [] for m, c in SERIES}
    wins = {m + "/" + c: 0 for m, c in SERIES}

    for inst_idx, name in enumerate(instances):
        optimum = optima[name]
        per_instance = []
        print("\n--", name, "optimo =", optimum)

        for method_idx, (method, config) in enumerate(SERIES):
            p = KnapsackProblem(name + ".txt")
            seed = 20260828 + inst_idx * 1000 + method_idx * 100
            agent = run_agent(p, method, config, seed)

            values = [float(s.fitness) for s in agent.stats.solutions]
            feasible = sum(1 for s in agent.stats.solutions if p.isFeasible(s))
            mean = float(np.mean(values))
            std = float(np.std(values))
            best = float(np.max(values))
            gap = 100.0 * (optimum - mean) / optimum
            label = method + "/" + config

            gaps_by_series[label].append(gap)
            per_instance.append((gap, label))
            stats_for_friedman.append(agent.stats)
            names_for_friedman.append(name)

            rows.append({
                "instance": name,
                "algorithm": method,
                "config": config,
                "evaluations": N_EVALS,
                "runs": N_RUNS,
                "optimum": optimum,
                "best": round(best, 4),
                "mean": round(mean, 4),
                "std": round(std, 4),
                "gap_percent": round(gap, 4),
                "feasible_runs": feasible,
            })
            print("  %-14s best=%7.1f mean=%7.1f gap=%6.2f%% feasible=%d/%d"
                  % (label, best, mean, gap, feasible, N_RUNS))

        winner = min(per_instance, key=lambda x: x[0])[1]
        wins[winner] += 1

    outdir = os.path.dirname(OUTPUT)
    if outdir:
        os.makedirs(outdir, exist_ok=True)
    with open(OUTPUT, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    ranking = []
    for label, gaps in gaps_by_series.items():
        ranking.append((float(np.mean(gaps)), float(np.std(gaps)), wins[label], label))
    ranking.sort(key=lambda x: x[0])

    print("\n==================== RANKING GLOBAL ====================")
    print("Ordenado por menor gap medio respecto al optimo exacto:")
    for pos, (mean_gap, std_gap, nwin, label) in enumerate(ranking, start=1):
        print(" %d. %-14s gap medio=%6.2f%%  desv=%5.2f  victorias=%d/%d"
              % (pos, label, mean_gap, std_gap, nwin, len(instances)))
    print("\nCSV guardado en:", OUTPUT)

    if DO_STATS:
        if len(instances) < 5:
            print("\n[AVISO] Friedman con muy pocas instancias es solo indicativo.")
        labels, matrix = getMatrix(names_for_friedman, stats_for_friedman)
        f = FriedmanImanHolm()
        f.fidh("MAX", copy.deepcopy(labels), matrix)

    return ranking


if __name__ == "__main__":
    main()

# coding=UTF-8
"""
Experimento comparativo: VNS vs GA vs SA vs TS sobre el
Berth Allocation Problem (BAP) con analisis estadistico de Friedman.

Ejecucion desde la raiz:
    python ExecuteBAP.py
    python ExecuteBAP.py --headless
"""

import sys
import os

if "--headless" in sys.argv:
	import matplotlib
	matplotlib.use("Agg")

import matplotlib.pyplot as plt
from agent.Agent import *
from examples.BerthAllocationProblem import *
from statisticc.Reporter import printer, getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm
import copy

INSTANCES = ["bap_10_3.txt", "bap_20_5.txt", "bap_30_7.txt"]
METHODS   = ["VNS", "TS",  "GA",  "SA"]
CONFIGS   = ["VNSc", "TSr", "GAS", "SAS"]
N_EVALS   = 3000
N_RUNS    = 5

def main():
	print("===============================================")
	print(" LOGISTICA PORTUARIA :: BAP (VNS vs TS vs GA vs SA)")
	print(" Instancias      : ", INSTANCES)
	print(" Metaheuristicas : ", METHODS)
	print(" Evaluaciones    : ", N_EVALS)
	print(" Corridas        : ", N_RUNS)
	print("===============================================")

	nameParameters = []
	nameinstances = []
	startCosts = []

	for inst in INSTANCES:
		problemv = BerthAllocationProblem(inst)
		print(f"\n-------- Instancia: {inst} (Buques={problemv.nVar}, Muelles={problemv.nBerths}) --------")

		for i in range(len(METHODS)):
			print(f"\n>>> Ejecutando {METHODS[i]} con config {CONFIGS[i]}")
			agent = Agent(problemv, [METHODS[i], CONFIGS[i], N_EVALS, N_RUNS])
			agent.init()

			nameParameters.append(agent.stats)
			nameinstances.append(inst)
			startCosts.append(list(agent.startCosts))

	# Reporte de resultados
	printer(nameinstances, nameParameters, {}, startCosts)

	# Test Estadistico de Friedman
	labels, matrix = getMatrix(nameinstances, nameParameters)
	print("\n:: Matriz de Entrada para Friedman ::")
	print(f"Dimensiones: {matrix.shape[0]} instancias x {matrix.shape[1]} algoritmos")
	print(f"Algoritmos: {labels}")

	f = FriedmanImanHolm()
	f.fidh("MIN", copy.deepcopy(labels), matrix)

	if "--headless" in sys.argv:
		outdir = "./DATA/output"
		if not os.path.isdir(outdir):
			os.makedirs(outdir)
		outfile = outdir + "/BAP_ranks_boxplot.png"
		plt.gcf().savefig(outfile, bbox_inches="tight")
		print("\n:: Boxplot guardado exitosamente en :: " + outfile)

if __name__ == "__main__":
	main()
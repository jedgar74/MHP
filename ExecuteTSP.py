# coding=UTF-8
"""
Experimento comparativo ACO vs GA vs SA sobre instancias TSPLIB, con analisis
estadistico no parametrico (Friedman / Iman-Davenport / Holm).

IMPORTANTE: ejecutar desde la raiz del repositorio; las rutas ./DATA/... son
relativas al directorio de trabajo.

	python ExecuteTSP.py                 # banco rapido por defecto (4 x 3 x 5), < 3 min
	python ExecuteTSP.py --full          # experimento completo (12 x 3 x 30), ~20 h
	python ExecuteTSP.py --headless      # no abre ventanas; guarda el boxplot
	python ExecuteTSP.py --instances 6 --runs 5 --evals 3000
	python ExecuteTSP.py --headless --log DATA/output/run.log

Con --log se escribe un fichero de progreso, una linea por celda
(instancia x algoritmo), con tiempo transcurrido y ETA. Esta pensado para
seguir una corrida larga desde fuera:

	tail -f DATA/output/run.log
"""

import sys
import os

if "--headless" in sys.argv:
	import matplotlib
	matplotlib.use("Agg")

import matplotlib.pyplot as plt

from agent.Agent import *
from examples.TravelingSalesmanProblem import *
from statisticc.Reporter import printer, getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm

import copy

# agent.Agent hace 'from datetime import ... time ...', asi que el nombre time
# queda sombreado por datetime.time. Se importan con alias tras el star-import.
import time as _time
import traceback as _traceback


LOGFILE = None


def elapsedStr(seconds):
	"""Segundos -> H:MM:SS."""

	seconds = int(seconds)
	return "%d:%02d:%02d" % (seconds // 3600, (seconds % 3600) // 60, seconds % 60)


def progress(msg):
	"""Emite una linea de progreso con prefijo fijo, para que un monitor
	externo pueda filtrarla. Se vuelca de inmediato: con la salida redirigida
	a un fichero el buffer es de bloque y las lineas no apareceran a tiempo."""

	line = "[TSP] " + msg
	print(line, flush=True)
	if LOGFILE is not None:
		try:
			f = open(LOGFILE, "a", encoding="utf-8")
			f.write(line + chr(10))
			f.close()
		except Exception:
			pass   # el log es observabilidad: nunca debe tumbar la corrida


# --------------------------------------------------------------------------
# Instancias TSPLIB (EUC_2D) y sus optimos conocidos.
# Se usan como BLOQUES del test de Friedman: por eso son >= 10 y no 3.
# --------------------------------------------------------------------------
OPTIMA = {
	"eil51.tsp":     426,
	"berlin52.tsp":  7542,
	"st70.tsp":      675,
	"eil76.tsp":     538,
	"pr76.tsp":      108159,
	"rat99.tsp":     1211,
	"kroA100.tsp":   21282,
	"kroB100.tsp":   22141,
	"eil101.tsp":    629,
	"lin105.tsp":    14379,
	"ch130.tsp":     6110,
	"ch150.tsp":     6528,
}

# Conjunto por defecto: 4 instancias de escala creciente (51 a 100 ciudades).
# Es un banco representativo y agil, pensado para demostrar el sistema en
# menos de 3 minutos. El conjunto completo de 12, que sirve como bloques del
# test de Friedman con la potencia estadistica que pide la literatura, esta
# disponible con --full.
INSTANCES = ["eil51.tsp", "berlin52.tsp", "st70.tsp", "kroA100.tsp"]

INSTANCES_FULL = ["eil51.tsp", "berlin52.tsp", "st70.tsp", "eil76.tsp",
			"pr76.tsp", "rat99.tsp", "kroA100.tsp", "kroB100.tsp",
			"eil101.tsp", "lin105.tsp", "ch130.tsp", "ch150.tsp"]

# Configuraciones OBLIGATORIAMENTE permutacionales.
# OperatorsPerm solo implementa la mutacion SWAPPING y los cruces
# APX/PMX/OX/CX/POS. No usar SAR: no declara mutationoper, cae al default
# BASIC2 y lanza ValueError en espacio permutacional.
METHODS = ["ACO", "GA",  "SA"]
CONFIGS = ["ACOS", "GAS", "SAS"]

# 1500 y no 2000: con 2000 el banco tarda 3:24 en la maquina de referencia y
# el objetivo es bajar de 3 min. Se recorta el presupuesto antes que el numero
# de instancias o de repeticiones, que son los que sostienen la comparacion.
N_EVALS = 1500
N_EXPERIMENTS = 5


def readArgs():
	"""Aplica los modificadores de linea de comandos."""
	global INSTANCES, N_EVALS, N_EXPERIMENTS, LOGFILE

	# --full restaura el experimento completo descrito en el commit
	#   feat(tsp-aco): incorporar metaheuristica ACO, soporte TSPLIB para TSP
	#   y suite de pruebas
	# es decir 12 instancias x 3 algoritmos x 30 corridas x 25000 evaluaciones,
	# con las 12 instancias como bloques del test de Friedman.
	# Advertencia: son unas 20 h. El coste esta dominado por ACO, cuyo
	# buildTour es O(N^2) por tour y no se beneficia del parche de OX.
	if "--full" in sys.argv:
		INSTANCES = INSTANCES_FULL
		N_EVALS = 25000
		N_EXPERIMENTS = 30

	for i in range(len(sys.argv)):
		if (sys.argv[i] == "--instances") and (i+1 < len(sys.argv)):
			INSTANCES = INSTANCES[0:int(sys.argv[i+1])]
		elif (sys.argv[i] == "--evals") and (i+1 < len(sys.argv)):
			N_EVALS = int(sys.argv[i+1])
		elif (sys.argv[i] == "--runs") and (i+1 < len(sys.argv)):
			N_EXPERIMENTS = int(sys.argv[i+1])
		elif (sys.argv[i] == "--log") and (i+1 < len(sys.argv)):
			LOGFILE = sys.argv[i+1]
			d = os.path.dirname(LOGFILE)
			if d and (not os.path.isdir(d)):
				os.makedirs(d)
			open(LOGFILE, "w", encoding="utf-8").close()


def main():
	readArgs()

	print("===============================================")
	print(" TSP :: ACO vs GA vs SA")
	print(" Instancias (bloques) : " + str(len(INSTANCES)))
	print(" Algoritmos           : " + str(METHODS))
	print(" Configuraciones      : " + str(CONFIGS))
	print(" Evaluaciones/corrida : " + str(N_EVALS))
	print(" Corridas             : " + str(N_EXPERIMENTS))
	print("===============================================")

	nameParameters = []
	nameinstances = []
	startCosts = []

	nCells = len(INSTANCES) * len(METHODS)
	cell = 0
	t0 = _time.perf_counter()
	progress("START %d celdas (%d instancias x %d algoritmos), %d corridas x %d evals"
			% (nCells, len(INSTANCES), len(METHODS), N_EXPERIMENTS, N_EVALS))

	for j in range(len(INSTANCES)):
		problemv = TravelingSalesmanProblem(INSTANCES[j])
		print("\n-------- instance ------ " + INSTANCES[j]
				+ "  (n=" + str(problemv.nVar) + ")")

		for i in range(len(METHODS)):
			print("\n---------------------- " + METHODS[i] + " --- " + CONFIGS[i])
			agent = Agent(problemv, [METHODS[i], CONFIGS[i], N_EVALS, N_EXPERIMENTS])
			agent.init()

			# Nota: Agent.init() reinicia problemv.counter al cerrar cada
			# corrida, por lo que aqui siempre valdria 0. La verificacion del
			# presupuesto esta en tests/test_aco.py.

			nameParameters.append(agent.stats)
			nameinstances.append(INSTANCES[j])
			# Costo del tour de arranque por corrida. Solo ACO lo reporta;
			# para GA y SA queda vacio y las columnas salen como '-'.
			startCosts.append(list(agent.startCosts))

			# Una linea por celda: es lo que consume el monitor externo.
			cell = cell + 1
			el = _time.perf_counter() - t0
			eta = (el / cell) * (nCells - cell)
			ave = agent.stats.average()
			progress("CELL %d/%d %s %s best=%.2f mean=%.2f | elapsed %s | ETA %s"
					% (cell, nCells, INSTANCES[j], METHODS[i],
						agent.stats.getBetter(), ave,
						elapsedStr(el), elapsedStr(eta)))

	progress("STATS todas las celdas completas en %s; analisis estadistico"
			% elapsedStr(_time.perf_counter() - t0))

	# ---------------- Tablas descriptivas ---------------------------------
	printer(nameinstances, nameParameters, OPTIMA, startCosts)

	# ---------------- Test no parametrico ---------------------------------
	# matrix es N x K : N = instancias (bloques), K = algoritmos (columnas)
	labels, matrix = getMatrix(nameinstances, nameParameters)

	print("\n\n:: Friedman input matrix :: "
			+ str(matrix.shape[0]) + " instancias x "
			+ str(matrix.shape[1]) + " algoritmos")
	print(":: labels :: " + str(labels))

	if matrix.shape[0] < 10:
		print("\n[AVISO] Con menos de 10 instancias el test de Friedman carece")
		print("        de potencia estadistica. Resultado solo indicativo.")

	f = FriedmanImanHolm()
	f.fidh("MIN", copy.deepcopy(labels), matrix)

	if "--headless" in sys.argv:
		outdir = "./DATA/output"
		if not os.path.isdir(outdir):
			os.makedirs(outdir)
		outfile = outdir + "/TSP_ranks_boxplot.png"
		plt.gcf().savefig(outfile, bbox_inches="tight")
		print("\n:: boxplot guardado en :: " + outfile)

	progress("DONE total %s" % elapsedStr(_time.perf_counter() - t0))


if __name__ == "__main__":
	# El fallo debe llegar al log: un monitor que solo vigile lineas de exito
	# se queda mudo ante un crash, y el silencio es indistinguible de "sigue".
	try:
		main()
	except BaseException as ex:
		progress("FAIL %s: %s" % (type(ex).__name__, ex))
		progress("FAIL traceback:" + chr(10) + _traceback.format_exc())
		raise

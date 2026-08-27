# coding=UTF-8
"""
Experimento comparativo GRASP vs GA vs SA vs RW sobre instancias de Max-Cut,
con analisis estadistico no parametrico (Friedman / Iman-Davenport / Holm).

Espejo de ExecuteFlowShop.py, adaptado a un problema binario de maximizacion.

IMPORTANTE: ejecutar desde la raiz del repositorio; las rutas ./DATA/... son
relativas al directorio de trabajo.

	python ExecuteMaxCut.py                  # banco rapido (5 inst. x 4 series), ~3 min
	python ExecuteMaxCut.py --full           # 20 instancias, corridas completas, ~30 min
	python ExecuteMaxCut.py --headless       # no abre ventanas; guarda el boxplot
	python ExecuteMaxCut.py --instances 8 --runs 5 --evals 20000
	python ExecuteMaxCut.py --alpha --full --headless   # calibra el parametro alpha
	python ExecuteMaxCut.py --full --headless --log DATA/output/maxcut.log

Con --log se escribe un fichero de progreso, una linea por celda
(instancia x algoritmo), con tiempo transcurrido y ETA:

	tail -f DATA/output/maxcut.log
"""

import sys
import os

if "--headless" in sys.argv:
	import matplotlib
	matplotlib.use("Agg")

import matplotlib.pyplot as plt

from agent.Agent import *
from examples.MaxCutProblem import *
from statisticc.Reporter import printer, getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm

import copy

# agent.Agent hace 'from datetime import ... time ...', asi que el nombre time
# queda sombreado por datetime.time. Se importan con alias tras el star-import.
import time as _time
import traceback as _traceback


LOGFILE = None

INSTDIR = "./DATA/instances/MAXCUT"

# Las 20 instancias de 20 vertices generadas con semilla fija. El optimo de
# cada una es EXACTO: se obtuvo por enumeracion 2^(n-1) en generate.py, no es
# un "mejor valor conocido".
# El nombre va SIN extension, para que coincida con las claves de optimums.txt;
# el fichero se abre anadiendo ".txt".
INSTANCES_FULL = ["mc20_%d" % k for k in range(1, 21)]

# La lista completa; en main() se toma el prefijo segun --instances / --full.
INSTANCES = INSTANCES_FULL


def elapsedStr(seconds):
	"""Segundos -> H:MM:SS."""

	seconds = int(seconds)
	return "%d:%02d:%02d" % (seconds // 3600, (seconds % 3600) // 60, seconds % 60)


def progress(msg):
	"""Emite una linea de progreso con prefijo fijo, para que un monitor
	externo pueda filtrarla. Se vuelca de inmediato: con la salida redirigida
	a un fichero el buffer es de bloque y las lineas no apareceran a tiempo."""

	line = "[MAXCUT] " + msg
	print(line, flush=True)
	if LOGFILE is not None:
		try:
			f = open(LOGFILE, "a", encoding="utf-8")
			f.write(line + chr(10))
			f.close()
		except Exception:
			pass   # el log es observabilidad: nunca debe tumbar la corrida


def loadOptima():
	"""
	Lee los optimos exactos desde opt/optimums.txt.

	@return dict : "mc20_1" -> corte maximo exacto
	@author
	"""

	optima = {}
	with open(INSTDIR + "/opt/optimums.txt", "r") as fh:
		for line in fh.readlines():
			parts = line.split()
			if len(parts) == 2:
				optima[parts[0].lower()] = int(parts[1])
	return optima


# --------------------------------------------------------------------------
# Series a comparar: (metaheuristica, configuracion, corridas).
#
# Las cuatro son estocasticas, asi que todas corren 10 veces (o lo que indique
# --runs). GRASP es constructivo de multi-arranque; GA poblacional; SA y RW
# trayectoriales. RW es la linea base (caminata aleatoria con memoria del
# mejor).
#
# La potencia del test de Friedman la aportan las INSTANCIAS, que son sus
# bloques; las repeticiones se colapsan en una media dentro de cada celda
# (ver getMatrix en statisticc/Reporter.py).
# --------------------------------------------------------------------------
SERIES = [
	("GRASP", "GRASPc", 10),   # construccion RCL (alpha=0.3) + busqueda local
	("GA",    "GAB",    10),   # generacional... ver config; STEADY + ONEPOINT
	("SA",    "SAB",    10),   # recocido simulado, mutacion FLIPPING
	("RW",    "RWB",    10),   # caminata aleatoria, mutacion FLIPPING
]

N_EVALS = 20000
N_INSTANCES = 5
RUNS_OVERRIDE = None


def readArgs():
	"""Aplica los modificadores de linea de comandos."""
	global N_INSTANCES, N_EVALS, RUNS_OVERRIDE, LOGFILE

	if "--full" in sys.argv:
		N_INSTANCES = 20

	# Calibracion del parametro alpha: cuatro valores de la misma metaheuristica,
	# con todo lo demas identico.
	if "--alpha" in sys.argv:
		global SERIES
		SERIES = [
			("GRASP", "GRASPg",   10),   # alpha = 0.0 (voraz)
			("GRASP", "GRASPc",   10),   # alpha = 0.3
			("GRASP", "GRASPa05", 10),   # alpha = 0.5
			("GRASP", "GRASPr",   10),   # alpha = 1.0 (aleatorio)
		]

	for i in range(len(sys.argv)):
		if (sys.argv[i] == "--instances") and (i+1 < len(sys.argv)):
			N_INSTANCES = int(sys.argv[i+1])
		elif (sys.argv[i] == "--evals") and (i+1 < len(sys.argv)):
			N_EVALS = int(sys.argv[i+1])
		elif (sys.argv[i] == "--runs") and (i+1 < len(sys.argv)):
			RUNS_OVERRIDE = int(sys.argv[i+1])
		elif (sys.argv[i] == "--log") and (i+1 < len(sys.argv)):
			LOGFILE = sys.argv[i+1]
			d = os.path.dirname(LOGFILE)
			if d and (not os.path.isdir(d)):
				os.makedirs(d)
			open(LOGFILE, "w", encoding="utf-8").close()


def main():
	readArgs()

	optima = loadOptima()
	instances = INSTANCES[0:N_INSTANCES]

	series = []
	for method, config, runs in SERIES:
		if RUNS_OVERRIDE is not None:
			runs = RUNS_OVERRIDE
		series.append((method, config, runs))

	print("===============================================")
	print(" Max-Cut :: GRASP vs GA vs SA vs RW")
	print(" Instancias (bloques) : " + str(len(instances)))
	print(" Series               : " + str([s[0]+"/"+s[1] for s in series]))
	print(" Corridas por serie   : " + str([s[2] for s in series]))
	print(" Evaluaciones/corrida : " + str(N_EVALS))
	print(" Referencia de calidad: opt/optimums.txt (optimo exacto)")
	print("===============================================")

	nameParameters = []
	nameinstances = []
	startCosts = []

	nCells = len(instances) * len(series)
	cell = 0
	t0 = _time.perf_counter()
	progress("START %d celdas (%d instancias x %d series), %d evals"
			% (nCells, len(instances), len(series), N_EVALS))

	for label in instances:
		problemv = MaxCutProblem(label + ".txt")
		print("\n-------- instance ------ " + label
				+ "  (n=" + str(problemv.nVar) + ", totalWeight="
				+ str(problemv.totalWeight) + ")")

		for method, config, runs in series:
			print("\n---------------------- " + method + " --- " + config)
			agent = Agent(problemv, [method, config, N_EVALS, runs])
			agent.init()

			nameParameters.append(agent.stats)
			nameinstances.append(label)
			# Costo del arranque constructivo por corrida. GRASP lo reporta via
			# graspStartCost; GA, SA y RW no, y sus columnas salen como '-'.
			startCosts.append(list(agent.startCosts))

			cell = cell + 1
			el = _time.perf_counter() - t0
			eta = (el / cell) * (nCells - cell)
			ave = agent.stats.average()
			bks = optima.get(label, 0)
			# Problema de MAX: el gap es positivo cuando se queda por debajo.
			gap = 100.0 * (bks - ave) / bks if bks else 0.0
			progress("CELL %d/%d %s %s/%s best=%.0f mean=%.1f gap=%.2f%% | elapsed %s | ETA %s"
					% (cell, nCells, label, method, config,
						agent.stats.getBetter(), ave, gap,
						elapsedStr(el), elapsedStr(eta)))

	progress("STATS todas las celdas completas en %s; analisis estadistico"
			% elapsedStr(_time.perf_counter() - t0))

	# ---------------- Tablas descriptivas ---------------------------------
	# La columna Delta separa el merito de la busqueda del de la construccion:
	# Start% es el gap del arranque constructivo y Gap% el final tras buscar.
	printer(nameinstances, nameParameters, optima, startCosts)

	# ---------------- Test no parametrico ---------------------------------
	# matrix es N x K : N = instancias (bloques), K = series (columnas)
	labels, matrix = getMatrix(nameinstances, nameParameters)

	print("\n\n:: Friedman input matrix :: "
			+ str(matrix.shape[0]) + " instancias x "
			+ str(matrix.shape[1]) + " series")
	print(":: labels :: " + str(labels))

	if matrix.shape[0] < 10:
		print("\n[AVISO] Con menos de 10 instancias el test de Friedman carece")
		print("        de potencia estadistica. Resultado solo indicativo.")

	f = FriedmanImanHolm()
	f.fidh("MAX", copy.deepcopy(labels), matrix)

	if "--headless" in sys.argv:
		outdir = "./DATA/output"
		if not os.path.isdir(outdir):
			os.makedirs(outdir)
		# El nombre depende del modo: si no, una corrida --alpha sobrescribe
		# el diagrama del experimento principal.
		suffix = "alpha" if ("--alpha" in sys.argv) else "main"
		outfile = outdir + "/MAXCUT_ranks_boxplot_" + suffix + ".png"
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

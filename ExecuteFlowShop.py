# coding=UTF-8
"""
Experimento comparativo TS vs GA vs SA sobre instancias de Taillard del
Permutation Flow Shop Scheduling Problem, con analisis estadistico no
parametrico (Friedman / Iman-Davenport / Holm).

Espejo de ExecuteTSP.py, adaptado a las particularidades del PFSP.

IMPORTANTE: ejecutar desde la raiz del repositorio; las rutas ./DATA/... son
relativas al directorio de trabajo.

	python ExecuteFlowShop.py                  # banco rapido (5 inst. x 5 series), ~6 min
	python ExecuteFlowShop.py --full           # 30 instancias, corridas completas, ~3 h
	python ExecuteFlowShop.py --headless       # no abre ventanas; guarda el boxplot
	python ExecuteFlowShop.py --instances 10 --runs 5 --evals 20000
	python ExecuteFlowShop.py --tenure --full --headless   # calibra la tenencia
	python ExecuteFlowShop.py --full --headless --log DATA/output/pfsp.log

Con --log se escribe un fichero de progreso, una linea por celda
(instancia x algoritmo), con tiempo transcurrido y ETA:

	tail -f DATA/output/pfsp.log
"""

import sys
import os

if "--headless" in sys.argv:
	import matplotlib
	matplotlib.use("Agg")

import matplotlib.pyplot as plt

from agent.Agent import *
from examples.PermutationFlowShopProblem import *
from statisticc.Reporter import printer, getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm

import copy

# agent.Agent hace 'from datetime import ... time ...', asi que el nombre time
# queda sombreado por datetime.time. Se importan con alias tras el star-import.
import time as _time
import traceback as _traceback


LOGFILE = None

INSTDIR = "./DATA/instances/PFSP"

# Los tres ficheros de 20 trabajos. Se usan estos y no los de 50 porque en
# n=20 la referencia de calidad es solida: 26 de 30 cabeceras coinciden con el
# mejor valor conocido, frente a 11 de 30 en n=50 (ver seccion 2.4 del
# documento de diseno).
FILES_20 = [("tai20_5.txt", 5), ("tai20_10.txt", 10), ("tai20_20.txt", 20)]


def elapsedStr(seconds):
	"""Segundos -> H:MM:SS."""

	seconds = int(seconds)
	return "%d:%02d:%02d" % (seconds // 3600, (seconds % 3600) // 60, seconds % 60)


def progress(msg):
	"""Emite una linea de progreso con prefijo fijo, para que un monitor
	externo pueda filtrarla. Se vuelca de inmediato: con la salida redirigida
	a un fichero el buffer es de bloque y las lineas no apareceran a tiempo."""

	line = "[PFSP] " + msg
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
	Lee los MEJORES VALORES CONOCIDOS desde opt/optimums.txt.

	No se usan las cotas de la cabecera de cada instancia: son las de Taillard
	(1993) y la investigacion posterior las ha mejorado. Medirse contra ellas
	daria desviaciones negativas espurias de hasta el 1 % (ver seccion 2.4c
	del documento de diseno).

	@return dict : "ta001" -> mejor valor conocido
	@author
	"""

	optima = {}
	with open(INSTDIR + "/opt/optimums.txt", "r") as fh:
		for line in fh.readlines():
			parts = line.split()
			if len(parts) == 2:
				optima[parts[0].lower()] = int(parts[1])
	return optima


def buildInstances(files):
	"""
	Construye la lista de instancias como pares (etiqueta, [fichero, indice]).

	Cada fichero de Taillard concatena 10 instancias, asi que la etiqueta
	"ta001" no basta para abrirla: hace falta el par fichero + indice.

	@param list files : lista de (fichero, numero de maquinas)
	@return list : lista de (etiqueta, [fichero, indice])
	@author
	"""

	out = []
	for fname, m in files:
		for idx in range(1, 11):
			problem = PermutationFlowShopProblem([fname, idx])
			out.append((problem.instanceName, [fname, idx]))
	return out


# --------------------------------------------------------------------------
# Series a comparar: (metaheuristica, configuracion, corridas).
#
# El numero de corridas NO es uniforme a proposito:
#
#   TSc y TSattr arrancan con NEH y eligen siempre el mejor candidato, sin
#   ningun componente aleatorio. Son DETERMINISTAS: 30 corridas devolverian
#   30 veces el mismo numero y una desviacion estandar de 0. Se ejecuta una
#   sola y su valor es exacto.
#
#   GA, SA y TSr si son estocasticos y necesitan repeticiones para que su
#   media sea representativa.
#
# La potencia del test de Friedman la aportan las INSTANCIAS, que son sus
# bloques; las repeticiones se colapsan en una media dentro de cada celda
# (ver getMatrix en statisticc/Reporter.py). Por eso bajar de 30 a 10
# repeticiones no debilita el contraste, mientras que bajar de 30 instancias
# si lo haria.
# --------------------------------------------------------------------------
SERIES = [
	("TS", "TSc",    1),    # memoria por solucion, arranque NEH  (determinista)
	("TS", "TSattr", 1),    # memoria por atributo, arranque NEH  (determinista)
	("TS", "TSr",   10),    # memoria por solucion, arranque aleatorio
	("GA", "GAS",   10),    # cruce OX permutacional
	("SA", "SAS",   10),    # mutacion SWAPPING
]

# Presupuesto fijado en la fase 4 con datos medidos: con n=20 el vecindario de
# insercion tiene 361 candidatos, de modo que 5000 evaluaciones solo darian 13
# iteraciones a TS y su lista tabu no llegaria a actuar. Con 50000 son ~138.
N_EVALS = 50000

# Banco rapido por defecto: 5 instancias, para demostrar el sistema en minutos.
N_INSTANCES = 5
RUNS_OVERRIDE = None


def readArgs():
	"""Aplica los modificadores de linea de comandos."""
	global N_INSTANCES, N_EVALS, RUNS_OVERRIDE, LOGFILE

	if "--full" in sys.argv:
		N_INSTANCES = 30

	# Calibracion de la tenencia: cuatro valores de la misma metaheuristica, con
	# todo lo demas identico. Las cuatro son deterministas (arranque NEH), asi
	# que basta una corrida por celda y su valor es exacto.
	if "--tenure" in sys.argv:
		global SERIES
		SERIES = [
			("TS", "TS3",  1),
			("TS", "TSc",  1),   # tenencia 7, el valor clasico
			("TS", "TS15", 1),
			("TS", "TS25", 1),
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
	instances = buildInstances(FILES_20)[0:N_INSTANCES]

	series = []
	for method, config, runs in SERIES:
		if RUNS_OVERRIDE is not None:
			runs = RUNS_OVERRIDE
		series.append((method, config, runs))

	print("===============================================")
	print(" PFSP :: TS vs GA vs SA")
	print(" Instancias (bloques) : " + str(len(instances)))
	print(" Series               : " + str([s[0]+"/"+s[1] for s in series]))
	print(" Corridas por serie   : " + str([s[2] for s in series]))
	print(" Evaluaciones/corrida : " + str(N_EVALS))
	print(" Referencia de calidad: opt/optimums.txt (mejor valor conocido)")
	print("===============================================")

	nameParameters = []
	nameinstances = []
	startCosts = []

	nCells = len(instances) * len(series)
	cell = 0
	t0 = _time.perf_counter()
	progress("START %d celdas (%d instancias x %d series), %d evals"
			% (nCells, len(instances), len(series), N_EVALS))

	for label, spec in instances:
		problemv = PermutationFlowShopProblem(spec)
		print("\n-------- instance ------ " + label
				+ "  (n=" + str(problemv.nVar) + ", m=" + str(problemv.nMachines) + ")")

		for method, config, runs in series:
			print("\n---------------------- " + method + " --- " + config)
			agent = Agent(problemv, [method, config, N_EVALS, runs])
			agent.init()

			nameParameters.append(agent.stats)
			nameinstances.append(label)
			# Costo del arranque constructivo por corrida. TS lo reporta via
			# nehCost; GA y SA no, y sus columnas salen como '-'.
			startCosts.append(list(agent.startCosts))

			cell = cell + 1
			el = _time.perf_counter() - t0
			eta = (el / cell) * (nCells - cell)
			ave = agent.stats.average()
			bks = optima.get(label, 0)
			gap = 100.0 * (ave - bks) / bks if bks else 0.0
			progress("CELL %d/%d %s %s/%s best=%.0f mean=%.1f gap=%.2f%% | elapsed %s | ETA %s"
					% (cell, nCells, label, method, config,
						agent.stats.getBetter(), ave, gap,
						elapsedStr(el), elapsedStr(eta)))

	progress("STATS todas las celdas completas en %s; analisis estadistico"
			% elapsedStr(_time.perf_counter() - t0))

	# ---------------- Tablas descriptivas ---------------------------------
	# La columna Delta es la que separa el merito de la busqueda del merito de
	# su arranque: Start% es el gap de NEH y Gap% el de TS tras buscar.
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
	f.fidh("MIN", copy.deepcopy(labels), matrix)

	if "--headless" in sys.argv:
		outdir = "./DATA/output"
		if not os.path.isdir(outdir):
			os.makedirs(outdir)
		# El nombre depende del modo: si no, una corrida --tenure sobrescribe
		# el diagrama del experimento principal.
		suffix = "tenure" if ("--tenure" in sys.argv) else "main"
		outfile = outdir + "/PFSP_ranks_boxplot_" + suffix + ".png"
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

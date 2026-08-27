# coding=UTF-8
"""
Experimento comparativo ILS vs GA vs SA vs HC sobre instancias de QAPLIB del
Quadratic Assignment Problem, con analisis estadistico no parametrico
(Friedman / Iman-Davenport / Holm).

Espejo de ExecuteFlowShop.py, adaptado a las particularidades del QAP.

ACO no figura entre las lineas base a proposito: el QAP no tiene matriz de
costos con la que alimentar la visibilidad heuristica de una metaheuristica
constructiva (ver el comentario de getCostMatrix() en el problema). Las tres
lineas base son GA, SA y HC, que son ademas las que el propio banco de salidas
del repositorio compara sobre QAP en DATA/output/QAP 28_5_2019 18_17.txt.

IMPORTANTE: ejecutar desde la raiz del repositorio; las rutas ./DATA/... son
relativas al directorio de trabajo.

	python ExecuteQAP.py                       # banco rapido (8 inst. x 6 series)
	python ExecuteQAP.py --full                # las 38 instancias, corridas completas
	python ExecuteQAP.py --headless            # no abre ventanas; guarda el boxplot
	python ExecuteQAP.py --instances 12 --runs 5 --evals 20000
	python ExecuteQAP.py --strength --full --headless   # calibra la perturbacion
	python ExecuteQAP.py --full --headless --log DATA/output/qap.log

Con --log se escribe un fichero de progreso, una linea por celda
(instancia x algoritmo), con tiempo transcurrido y ETA:

	tail -f DATA/output/qap.log
"""

import sys
import os

if "--headless" in sys.argv:
	import matplotlib
	matplotlib.use("Agg")

import matplotlib.pyplot as plt

from agent.Agent import *
from examples.QuadraticAssignmentProblem import *
from statisticc.Reporter import printer, getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm

import copy

# agent.Agent hace 'from datetime import ... time ...', asi que el nombre time
# queda sombreado por datetime.time. Se importan con alias tras el star-import.
import time as _time
import traceback as _traceback


LOGFILE = None

INSTDIR = "./DATA/instances/QAP"

# Orden de presentacion de las instancias. Se agrupan por familia y dentro de
# cada familia por tamano, para que el banco rapido (las primeras N) recoja
# familias distintas y no ocho variantes de la misma.
#
# Las familias no son intercambiables, y por eso se cubren todas:
#   had, nug, scr  matrices de distancia euclidianas sobre rejilla, las mas
#                  faciles y las que llevan mas anos resueltas al optimo
#   rou, tai*a     flujos y distancias uniformemente aleatorios
#   tai*b          asimetricas, generadas para ser duras
#   chr            fuertemente estructuradas; son el caso patologico del banco
#   bur, els, kra  instancias de origen real
INSTANCES = [
	"had12", "nug12", "scr12", "rou12", "tai12a", "tai12b", "chr12a", "chr12b",
	"chr12c", "had14", "nug14", "had16", "nug15", "scr15", "rou15", "tai15a",
	"tai15b", "chr15a", "chr15b", "chr15c", "nug17", "tai17a", "had18",
	"nug18", "chr18a", "chr18b", "els19", "had20", "scr20", "rou20",
	"tai20a", "tai20b", "chr20a", "chr20b", "chr20c", "chr22a", "bur26f",
	"kra30a",
]


def elapsedStr(seconds):
	"""Segundos -> H:MM:SS."""

	seconds = int(seconds)
	return "%d:%02d:%02d" % (seconds // 3600, (seconds % 3600) // 60, seconds % 60)


def progress(msg):
	"""Emite una linea de progreso con prefijo fijo, para que un monitor
	externo pueda filtrarla. Se vuelca de inmediato: con la salida redirigida
	a un fichero el buffer es de bloque y las lineas no apareceran a tiempo."""

	line = "[QAP] " + msg
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

	Las instancias de QAPLIB no traen cota en la cabecera: el fichero es solo
	n y las dos matrices. Sin esta tabla no habria forma de comparar el
	desempeno entre instancias, porque los costos van de 578 en nug12 a
	122 455 319 en tai20b y una media cruda no significaria nada.

	@return dict : "had12" -> mejor valor conocido
	@author
	"""

	optima = {}
	with open(INSTDIR + "/opt/optimums.txt", "r") as fh:
		for line in fh.readlines():
			line = line.strip()
			if line.startswith("#"):
				continue
			parts = line.split()
			if len(parts) == 2:
				optima[parts[0].lower()] = int(parts[1])
	return optima


# --------------------------------------------------------------------------
# Series a comparar: (metaheuristica, configuracion, corridas).
#
# Las seis son ESTOCASTICAS: todas arrancan de una permutacion aleatoria, asi
# que todas necesitan repeticiones para que su media sea representativa. Es la
# diferencia con el experimento del PFSP, donde TS con arranque NEH era
# determinista y bastaba una corrida.
#
# La potencia del test de Friedman la aportan las INSTANCIAS, que son sus
# bloques; las repeticiones se colapsan en una media dentro de cada celda
# (ver getMatrix en statisticc/Reporter.py). Por eso 10 repeticiones bastan,
# mientras que bajar el numero de instancias si debilitaria el contraste.
# --------------------------------------------------------------------------
SERIES = [
	("ILS", "ILSc",  10),   # perturbacion por bloques, descenso completo
	("ILS", "ILSFa", 10),   # traduccion de ILSFa.cfg: bloques, vecindario muestreado
	("ILS", "ILSFb", 10),   # traduccion de ILSFb.cfg: intercambios, NIC=500
	("GA",  "GAS",   10),   # cruce OX permutacional
	("SA",  "SAS",   10),   # mutacion SWAPPING
	("HC",  "HCc",   10),   # busqueda local sola: el suelo contra el que medir ILS
]

# El presupuesto es el del propio banco de salidas del repositorio
# (DATA/output/QAP 28_5_2019 18_17.txt, que corre GA, ILS y SA sobre had12 con
# 100000 evaluaciones). Usar el mismo numero permite contrastar estos
# resultados contra los que ya estaban registrados.
N_EVALS = 100000

# Banco rapido por defecto: 8 instancias de familias distintas.
N_INSTANCES = 8
RUNS_OVERRIDE = None


def readArgs():
	"""Aplica los modificadores de linea de comandos."""
	global N_INSTANCES, N_EVALS, RUNS_OVERRIDE, LOGFILE

	if "--full" in sys.argv:
		N_INSTANCES = len(INSTANCES)

	# Calibracion de la fuerza de la perturbacion: cuatro valores de la misma
	# metaheuristica, con todo lo demas identico. Es el parametro que decide
	# el equilibrio entre volver al mismo optimo local (k pequeno) y equivaler
	# a un reinicio aleatorio (k grande).
	if "--strength" in sys.argv:
		global SERIES
		SERIES = [
			("ILS", "ILSk1", 10),
			("ILS", "ILSk3", 10),   # el valor por defecto
			("ILS", "ILSk6", 10),
			("ILS", "ILSk9", 10),
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
	print(" QAP :: ILS vs GA vs SA vs HC")
	print(" Instancias (bloques) : " + str(len(instances)))
	print(" Series               : " + str([s[0]+"/"+s[1] for s in series]))
	print(" Corridas por serie   : " + str([s[2] for s in series]))
	print(" Evaluaciones/corrida : " + str(N_EVALS))
	print(" Referencia de calidad: opt/optimums.txt (mejor valor conocido)")
	print("===============================================")

	nameParameters = []
	nameinstances = []

	nCells = len(instances) * len(series)
	cell = 0
	t0 = _time.perf_counter()
	progress("START %d celdas (%d instancias x %d series), %d evals"
			% (nCells, len(instances), len(series), N_EVALS))

	for label in instances:
		problemv = QuadraticAssignmentProblem(label + ".dat")
		print("\n-------- instance ------ " + label
				+ "  (n=" + str(problemv.nVar) + ")")

		for method, config, runs in series:
			print("\n---------------------- " + method + " --- " + config)
			agent = Agent(problemv, [method, config, N_EVALS, runs])
			agent.init()

			nameParameters.append(agent.stats)
			nameinstances.append(label)

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
	# Ninguna serie declara arranque constructivo, asi que no se pasa
	# startCosts: la columna Delta no tendria contenido.
	printer(nameinstances, nameParameters, optima)

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
		# El nombre depende del modo: si no, una corrida --strength sobrescribe
		# el diagrama del experimento principal.
		suffix = "strength" if ("--strength" in sys.argv) else "main"
		outfile = outdir + "/QAP_ranks_boxplot_" + suffix + ".png"
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

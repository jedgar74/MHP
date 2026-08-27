# coding=UTF-8
"""
Experimento comparativo BPSO vs GA vs SA sobre el problema 0/1 Knapsack (KP).

Enfoque: 3 algoritmos x 6 instancias x 5 corridas x 1000 evaluaciones.

  BPSO  -> DATA/config/BPSO/BPSOc.json  (sin calibrar; declarado en docs)
  GA    -> DATA/config/GA/GAKP.json     (GENERATIONAL, binario)
  SA    -> DATA/config/SA/SAKP.json     (FLIPPING, GEOMETRIC)

KP es un problema MAX: fitness = beneficio total, 0 % gap = optimo, y menor
gap significa mejor desempeno. Se usa el optimo exacto por programacion
dinamica declarado en la cabecera de cada instancia (DATA/instances/KP/).

El analisis estadistico (Friedman / Iman-Davenport / Holm) se hace sobre la
matriz de gaps medios por instancia interpretada como problema MIN (un gap
menor es mejor), reutilizando statisticc/FriedmanImanHolm.py tal cual.

IMPORTANTE:
  - ejecutar desde la raiz del repositorio (rutas ./DATA/... relativas)
  - se fija np.random.seed por celda (instancia x algoritmo) para que el
    experimento sea reproducible tal y como se ejecuta.
"""

from agent.Agent import *
from examples.KnapsackProblem import *
from statisticc.FriedmanImanHolm import FriedmanImanHolm

import copy
import io
import contextlib
import time as _time
import numpy as np

import sys
import os

# La salida estadistica de FriedmanImanHolm.fidh() dibuja el boxplot de los
# rangos y llama a plt.show(), que en un entorno sin display bloquea. El
# mismo patron de ExecuteTSP: con --headless se usa el backend Agg (sin
# ventana) y se guarda el grafico a disco.
if "--headless" in sys.argv:
	import matplotlib
	matplotlib.use("Agg")

import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Medicion del presupuesto consumido.
#
# Agent.init() crea su propio Counter al arrancar y lo vuelve a crear al
# cerrar (por lo que despues de init() el contador del problema siempre
# vale 0). Para no modificar la infraestructura, se intercambia en memoria
# la clase Counter por una subclase que recuerda el pico alcanzado por cada
# instancia; al terminar una celda (instancia, algoritmo) se lee el maximo.
# ---------------------------------------------------------------------------
from problem.Counter import Counter as _BaseCounter


class _PeakCounter(_BaseCounter):
	_instances = []

	def __init__(self, limit):
		super().__init__(limit)
		self._peak = 0
		_PeakCounter._instances.append(self)

	def incCount(self, u=1):
		super().incCount(u)
		if self.count > self._peak:
			self._peak = self.count

	def getPeak(self):
		return self._peak

	@classmethod
	def lastCellPeak(cls):
		"""Pico (maximo) de los contadores creados durante la ultima celda."""
		if not cls._instances:
			return 0
		return max(c.getPeak() for c in cls._instances)

	@classmethod
	def resetTracking(cls):
		cls._instances = []


# Intercambio en memoria de Counter por _PeakCounter en los tres modulos que
# lo referencian (Problem, Agent y el propio probado por los algoritmos).
import problem.Counter
import problem.Problem
import agent.Agent
problem.Counter.Counter = _PeakCounter
problem.Problem.Counter = _PeakCounter
agent.Agent.Counter = _PeakCounter

N_EVALS = 1000
N_EXPERIMENTS = 5

if "--evals" in sys.argv:
	N_EVALS = int(sys.argv[sys.argv.index("--evals") + 1])
if "--runs" in sys.argv:
	N_EXPERIMENTS = int(sys.argv[sys.argv.index("--runs") + 1])

INSTANCES = [
	"kp_10_1.txt", "kp_10_2.txt",
	"kp_20_1.txt", "kp_20_2.txt",
	"kp_30_1.txt", "kp_30_2.txt",
]

# Columna 1 = clave de configuracion dentro de DATA/config/
METHODS = [
	("BPSO", "BPSOc", "BPSO"),
	("GA",   "GAKP",  "GA"),
	("SA",   "SAKP",  "SA"),
]

# Semilla base por celda: se fija con (instancia, algoritmo) para reproducir
# exactamente la corrida si se vuelve a lanzar con los mismos parametros.
def seedFor(instIndex, methIndex):
	return 901_000 + instIndex * 100 + methIndex * 10


def gapPct(optimum, mean):
	"""Gap relativo al optimo en porcentaje. 0 % = optimo; menor = mejor."""
	return 100.0 * (optimum - mean) / optimum


def main():
	print("===============================================")
	print(" KP :: BPSO vs GA vs SA")
	print(" Instancias        : " + str(len(INSTANCES)))
	print(" Algoritmos        : " + str([m[0] for m in METHODS]))
	print(" Evaluaciones/corr : " + str(N_EVALS))
	print(" Corridas          : " + str(N_EXPERIMENTS))
	print(" Presupuesto total : " + str(N_EVALS * N_EXPERIMENTS
			* len(INSTANCES) * len(METHODS)))
	print("===============================================")

	# Resultados por celda: guardamos media, mejor, desv y evals consumidas.
	# La clave es (instancia, algoritmo); el orden de la fila en la tabla es
	# METODOS[]. Se obtiene el pico de evaluaciones con el contador del
	# problema antes de que Agent lo reinicie.
	results = {}

	t0 = _time.perf_counter()

	for ix, instance in enumerate(INSTANCES):
		problemv = KnapsackProblem(instance)
		print("\n-------- instance ------ " + instance
				+ "  (n=" + str(problemv.nVar)
				+ ", capacity=" + str(problemv.capacity)
				+ ", optimum=" + str(problemv.optimum) + ")")

		for mi, (meth, cfg, name) in enumerate(METHODS):
			np.random.seed(seedFor(ix, mi))
			_PeakCounter.resetTracking()
			agent = Agent(problemv, [meth, cfg, N_EVALS, N_EXPERIMENTS])

			# El Agent escribe por stdout el detalle de cada corrida; se
			# silencia durante la ejecucion para que la salida del experimento
			# sea solo el informe tabular.
			with contextlib.redirect_stdout(io.StringIO()):
				agent.init()

			stats = agent.stats
			mean = stats.average()
			sd   = stats.stDeviat(mean)

			# Agent reinicia problemv.counter al cerrar cada corrida; el pico
			# consumido queda registrado en los contadores de la ultima celda.
			evals = _PeakCounter.lastCellPeak()

			results[(instance, name)] = (stats, mean, sd, evals)

			print("  %-4s | best=%-7.2f mean=%-7.2f sd=%-7.2f evals=%d"
					% (name, stats.getBetter(), mean, sd, evals))

	elapsed = _time.perf_counter() - t0
	print("\n[KP] experimento completado en %.2f s" % elapsed)

	# ---------------- Tablas descriptivas (por instancia) ----------------
	print("\n" + "=" * 70)
	print(" Resultados por instancia (MAX: mejor beneficio; gap sobre media)")
	print(" gap %% = 100 * (optimo - media) / optimo")
	print("=" * 70)

	for instance in INSTANCES:
		problemv = KnapsackProblem(instance)
		opt = float(problemv.optimum)
		print("\n:: Instance :: " + instance + "   (optimum " + str(opt) + ")")
		header = ['{: <6s}'.format("Alg"),
		          '{: <10s}'.format("Best"),
		          '{: <10s}'.format("Mean"),
		          '{: <10s}'.format("SD"),
		          '{: <10s}'.format("Gap%"),
		          '{: <8s}'.format("Evals")]
		print("  " + "".join(header))
		print("  " + "-" * 52)
		for _, _, name in METHODS:
			stats, mean, sd, evals = results[(instance, name)]
			print("  " + '{: <6s}'.format(name)
				+ '{: <10.2f}'.format(round(stats.getBetter(), 2))
				+ '{: <10.2f}'.format(round(mean, 2))
				+ '{: <10.2f}'.format(round(sd, 2))
				+ '{: <10.2f}'.format(round(gapPct(opt, mean), 2))
				+ '{: <8d}'.format(evals))
		print("  " + "-" * 52)

	# ---------------- Tabla resumen (media de gaps) ----------------
	print("\n" + "=" * 70)
	print(" Tabla resumen: gap medio por instancia (menor mejor)")
	print("=" * 70)
	header = ['{: <14s}'.format("Instance")]
	for _, _, name in METHODS:
		header.append('{: <10s}'.format(name))
	print("  " + "".join(header))
	print("  " + "-" * 44)
	for instance in INSTANCES:
		opt = float(KnapsackProblem(instance).optimum)
		row = ['{: <14s}'.format(instance)]
		for _, _, name in METHODS:
			_, mean, _, _ = results[(instance, name)]
			row.append('{: <10.2f}'.format(round(gapPct(opt, mean), 2)))
		print("  " + "".join(row))

	# ---------------- Test no parametrico (gaps como MIN) ----------------
	print("\n" + "=" * 70)
	print(" Friedman / Iman-Davenport / Holm sobre gaps medios (MIN)")
	print("=" * 70)

	labels = [m[2] for m in METHODS]
	matrix = np.zeros((len(INSTANCES), len(METHODS)))
	for ix, instance in enumerate(INSTANCES):
		opt = float(KnapsackProblem(instance).optimum)
		for mi, (_, _, name) in enumerate(METHODS):
			_, mean, _, _ = results[(instance, name)]
			matrix[ix][mi] = round(gapPct(opt, mean), 4)

	print("Matriz de gaps (N x K): " + str(matrix.shape[0])
			+ " instancias x " + str(matrix.shape[1]) + " algoritmos")
	print("Labels: " + str(labels))
	if matrix.shape[0] < 10:
		print("\n[AVISO] Con menos de 10 instancias el test de Friedman carece")
		print("        de potencia estadistica. Resultado solo indicativo.")

	f = FriedmanImanHolm()
	f.fidh("MIN", copy.deepcopy(labels), matrix)

	if "--headless" in sys.argv:
		outdir = "./DATA/output"
		if not os.path.isdir(outdir):
			os.makedirs(outdir)
		outfile = outdir + "/KP_ranks_boxplot.png"
		plt.gcf().savefig(outfile, bbox_inches="tight")
		print("\n:: boxplot guardado en :: " + outfile)

	print("\n[KP] DONE en %.2f s" % (_time.perf_counter() - t0))


if __name__ == "__main__":
	main()
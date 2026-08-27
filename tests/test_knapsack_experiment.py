# Tests minimos de la experimentacion KP + BPSO: las 6 instancias, su optimo
# exacto, y smoke de GA / SA sobre KP con sus configuraciones.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_knapsack_experiment.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from problem.Counter import Counter
from examples.KnapsackProblem import KnapsackProblem
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.SimulatingAnnealing import SimulatingAnnealing

EXP_INSTANCES = [
	"kp_10_1.txt", "kp_10_2.txt",
	"kp_20_1.txt", "kp_20_2.txt",
	"kp_30_1.txt", "kp_30_2.txt",
]

# tamaños declarados en el diseno experimental
EXP_N = {"kp_10_1.txt": 10, "kp_10_2.txt": 10,
		"kp_20_1.txt": 20, "kp_20_2.txt": 20,
		"kp_30_1.txt": 30, "kp_30_2.txt": 30}

OPT_FILE = "DATA/instances/KP/opt/optimums.txt"


def loadHeaderOptimum():
	"""Lee los optimos declarados en opt/optimums.txt (formato tabs)."""

	opt = {}
	with open(OPT_FILE, "r") as fh:
		for line in fh:
			line = line.strip()
			if not line:
				continue
			name, value = line.split()
			opt[name] = float(value)
	return opt


class TestKnapsackExperimentInstances(unittest.TestCase):
	# -------------------------------------------------------- carga de las 6
	def test_six_instances_load_with_valid_metadata(self):
		for name in EXP_INSTANCES:
			with self.subTest(instance=name):
				p = KnapsackProblem(name)
				self.assertIsNotNone(p.optimum,
						"%s no declara optimo en la cabecera" % name)
				self.assertEqual(p.nVar, EXP_N[name])
				self.assertEqual(len(p.weights), p.nVar)
				self.assertEqual(len(p.profits), p.nVar)
				self.assertGreater(p.capacity, 0)

	def test_header_optimum_matches_exact_dp_file(self):
		header = {name: float(KnapsackProblem(name).optimum)
				for name in EXP_INSTANCES}
		dp = loadHeaderOptimum()
		self.assertEqual(set(dp.keys()), set(EXP_INSTANCES),
				"optimums.txt no lista exactamente las 6 instancias")
		for name in EXP_INSTANCES:
			with self.subTest(instance=name):
				self.assertEqual(header[name], dp[name],
						"optimo de cabecera != optimums.txt en %s" % name)

	def test_optimum_is_reachable_feasible(self):
		"""El optimo declarado no supera el beneficio total (suma de profits),
		que es una cota superior obvia del problema."""

		for name in EXP_INSTANCES:
			with self.subTest(instance=name):
				p = KnapsackProblem(name)
				self.assertLessEqual(p.optimum, int(np.sum(p.profits)))


class TestKnapsackExperimentSmoke(unittest.TestCase):
	# -------------------------------------------------- GA corre sobre KP
	def test_ga_runs_on_knapsack(self):
		np.random.seed(11)
		p = KnapsackProblem("kp_10_1.txt")
		p.counter = Counter(100)
		ga = GeneticAlgorithm(p, "GAKP")
		best = ga.status.stateFinal.fitness
		used = p.counter.getCount()

		self.assertIsNotNone(best, "GA no produjo fitness")
		self.assertLessEqual(best, p.optimum + 1e-9,
				"GA supero el optimo conocido")
		# La version GENERATIONAL del GA del framework incrementa el contador
		# por poblaciones, de modo que puede exceder el presupuesto en algunos
		# puntos (en el experimento completo uso 1004-1009 sobre 1000). Se
		# verifica el mismo comportamiento aqui con una cota laxa.
		self.assertLessEqual(used, 100 + 9,
				"GA uso %d evaluaciones con limite 100" % used)
		print("\n     GA en kp_10_1 con 100 evals: best = %s  evals = %d" % (best, used))

	def test_sa_runs_on_knapsack(self):
		np.random.seed(12)
		p = KnapsackProblem("kp_10_1.txt")
		p.counter = Counter(100)
		sa = SimulatingAnnealing(p, "SAKP")
		best = sa.status.stateFinal.fitness
		used = p.counter.getCount()

		self.assertIsNotNone(best, "SA no produjo fitness")
		self.assertLessEqual(best, p.optimum + 1e-9,
				"SA supero el optimo conocido")
		self.assertLessEqual(used, 100 + 1,
				"SA uso %d evaluaciones con limite 100" % used)
		print("\n     SA en kp_10_1 con 100 evals: best = %s  evals = %d" % (best, used))


if __name__ == "__main__":
	unittest.main(verbosity=2)
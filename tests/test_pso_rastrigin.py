import copy
import json
import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from algorithm.ParticleSwarmOptimization import ParticleSwarmOptimization
from examples.NQueens import NQueens
from examples.Rastrigin import Rastrigin
from problem.Counter import Counter
from state.Solution import Solution


class TestRastrigin(unittest.TestCase):

	def test_known_global_optimum(self):
		for dimensions in [2, 10, 30]:
			with self.subTest(dimensions=dimensions):
				problem = Rastrigin("Rastrigin%d.json" % dimensions)
				solution = Solution(problem, "RANDOM")
				solution.setValues(np.zeros(dimensions))
				value = problem.evaluate(solution)
				self.assertAlmostEqual(value, 0.0, places=12)
				self.assertEqual(solution.fitness, value)

	def test_reference_point(self):
		problem = Rastrigin("Rastrigin2.json")
		solution = Solution(problem, "RANDOM")
		solution.setValues(np.ones(2))
		problem.evaluate(solution)
		self.assertAlmostEqual(solution.fitness, 2.0, places=12)


class TestParticleSwarmOptimization(unittest.TestCase):

	def setUp(self):
		np.random.seed(7)

	def test_respects_evaluation_budget_and_bounds(self):
		problem = Rastrigin("Rastrigin10.json")
		problem.counter = Counter(517)
		pso = ParticleSwarmOptimization(problem, "PSOS")

		self.assertEqual(problem.counter.getCount(), 517)
		lower = np.asarray(problem.lowerlimits)
		upper = np.asarray(problem.upperlimits)
		for particle in pso.popul.popul:
			self.assertTrue(np.all(particle.vars >= lower))
			self.assertTrue(np.all(particle.vars <= upper))

	def test_best_fitness_never_worsens(self):
		problem = Rastrigin("Rastrigin2.json")
		problem.counter = Counter(600)
		pso = ParticleSwarmOptimization(problem, "PSOS", False)
		initial = copy.deepcopy(pso.status.stateInitial)
		pso.run()
		self.assertLessEqual(pso.status.stateFinal.fitness, initial.fitness)

	def test_quality_on_two_dimensions(self):
		problem = Rastrigin("Rastrigin2.json")
		problem.counter = Counter(3000)
		pso = ParticleSwarmOptimization(problem, "PSOS")
		self.assertLess(pso.status.stateFinal.fitness, 1e-4)

	def test_rejects_non_real_problem(self):
		problem = NQueens(10)
		problem.counter = Counter(100)
		with self.assertRaises(ValueError) as context:
			ParticleSwarmOptimization(problem, "PSOS", False)
		self.assertIn("REAL", str(context.exception))

	def test_incomplete_config_uses_defaults(self):
		path = "./DATA/config/PSO/PSOTEST.json"
		with open(path, "w", encoding="utf-8") as file:
			json.dump({"particles": 5}, file)
		try:
			problem = Rastrigin("Rastrigin2.json")
			problem.counter = Counter(20)
			pso = ParticleSwarmOptimization(problem, "PSOTEST", False)
			for name in ["particles", "inertia", "cognitive", "social",
						 "vmaxRatio", "initialTypeSolution"]:
				self.assertIn(name, pso.parameters)
		finally:
			os.remove(path)


if __name__ == "__main__":
	unittest.main(verbosity=2)

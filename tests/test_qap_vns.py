import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from algorithm.VariableNeighborhoodSearch import VariableNeighborhoodSearch
from examples.QuadraticAssignmentProblem import QuadraticAssignmentProblem
from problem.Counter import Counter
from state.Solution import Solution


class TestQAPVNS(unittest.TestCase):

	def setUp(self):
		self.problem = QuadraticAssignmentProblem('qap4.txt')

	def evaluate(self, permutation):
		solution = Solution(self.problem, 'RANDOM')
		solution.setValues(np.asarray(permutation, dtype=int))
		self.problem.evaluate(solution)
		return int(solution.fitness)

	def test_reader_and_known_cost(self):
		self.assertEqual(self.problem.nVar, 4)
		self.assertEqual(self.evaluate((1, 0, 3, 2)), 96)
		self.assertIsNone(self.problem.getCostMatrix())

	def test_exact_oracle(self):
		costs = [self.evaluate(permutation)
			for permutation in itertools.permutations(range(4))]
		self.assertEqual(min(costs), 96)
		self.assertEqual(costs.count(96), 2)

	def test_vns_finds_exact_optimum_with_fixed_seed(self):
		self.problem.counter = Counter(100)
		np.random.seed(0)
		vns = VariableNeighborhoodSearch(self.problem, 'VNSQAP')
		self.assertEqual(int(vns.status.stateFinal.fitness), 96)
		self.assertLessEqual(self.problem.counter.getCount(), 101)
		self.assertEqual(sorted(vns.status.stateFinal.vars.tolist()), [0, 1, 2, 3])

	def test_invalid_permutation_is_rejected(self):
		solution = Solution(self.problem, 'RANDOM')
		solution.setValues(np.asarray([0, 0, 1, 2]))
		with self.assertRaises(ValueError):
			self.problem.evaluate(solution)


if __name__ == '__main__':
	unittest.main(verbosity=2)
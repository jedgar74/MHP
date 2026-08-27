# coding=UTF-8
import sys, os
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.BerthAllocationProblem import BerthAllocationProblem
from algorithm.VariableNeighborhoodSearch import VariableNeighborhoodSearch
from problem.Counter import Counter
from state.Solution import Solution

class TestBAPandVNS(unittest.TestCase):

	def test_bap_instance_loading(self):
		p = BerthAllocationProblem("bap_10_3.txt")
		self.assertEqual(p.nVar, 10)
		self.assertEqual(p.nBerths, 3)
		self.assertEqual(p.handlingTimes.shape, (10, 3))

	def test_bap_evaluation_validity(self):
		p = BerthAllocationProblem("bap_10_3.txt")
		s = Solution(p, "RANDOM")
		p.evaluate(s)
		self.assertIsNotNone(s.fitness)
		self.assertGreater(s.fitness, 0)

	def test_vns_respects_budget(self):
		BUDGET = 500
		p = BerthAllocationProblem("bap_10_3.txt")
		p.counter = Counter(BUDGET)
		vns = VariableNeighborhoodSearch(p, "VNSc")
		self.assertLessEqual(p.counter.getCount(), BUDGET + 1)

if __name__ == "__main__":
	unittest.main(verbosity=2)
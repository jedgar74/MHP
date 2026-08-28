# coding=UTF-8
import os
import unittest
import numpy as np

from examples.KnapsackProblem import KnapsackProblem
from state.Solution import Solution


class TestKnapsackReader(unittest.TestCase):

    def test_problem_metadata(self):
        p = KnapsackProblem('toy3.txt')
        self.assertEqual(p.nameShort, 'KP')
        self.assertEqual(p.typeState, 'BINARY')
        self.assertEqual(p.typeProblem, 'MAX')
        self.assertEqual(p.nVar, 3)
        self.assertEqual(p.capacity, 50)

    def test_toy_known_optimum(self):
        p = KnapsackProblem('toy3.txt')
        s = Solution(p, '')
        # objetos 2 y 3: 100 + 120 = 220; peso 20 + 30 = 50
        s.vars = np.array([-1, 1, 1], dtype=float)
        p.evaluate(s)
        self.assertEqual(s.fitness, 220.0)
        self.assertTrue(p.isFeasible(s))
        self.assertEqual(p.solutionTotals(s), (220, 50))

    def test_infeasible_solution_is_penalized_below_feasible(self):
        p = KnapsackProblem('toy3.txt')
        s = Solution(p, '')
        s.vars = np.array([1, 1, 1], dtype=float)  # peso 60, exceso 10
        p.evaluate(s)
        self.assertEqual(s.fitness, -10.0)
        self.assertFalse(p.isFeasible(s))

    def test_every_generated_instance_has_recorded_optimum(self):
        pth = './DATA/instances/KNAPSACK/opt/optimums.txt'
        with open(pth, 'r', encoding='utf-8') as fh:
            opt = dict(line.split() for line in fh if line.strip())
        for k in range(1, 11):
            name = 'kp60_%02d' % k
            p = KnapsackProblem(name + '.txt')
            self.assertEqual(p.nVar, 60)
            self.assertIn(name, opt)
            self.assertGreater(int(opt[name]), 0)

    def test_invalid_item_count_raises(self):
        path = './DATA/instances/KNAPSACK/_invalid_test.txt'
        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write('3 10\n5 2\n6 3\n')
            with self.assertRaises(ValueError):
                KnapsackProblem('_invalid_test.txt')
        finally:
            if os.path.exists(path):
                os.remove(path)


if __name__ == '__main__':
    unittest.main()

# coding=UTF-8
import unittest
import numpy as np

from examples.KnapsackProblem import KnapsackProblem
from algorithm.LateAcceptanceHillClimbing import LateAcceptanceHillClimbing
from problem.Counter import Counter
from agent.Agent import Agent


class TestLateAcceptanceHillClimbing(unittest.TestCase):

    def setUp(self):
        np.random.seed(12345)

    def test_configuration_is_loaded(self):
        p = KnapsackProblem('toy3.txt')
        p.counter = Counter(100)
        alg = LateAcceptanceHillClimbing(p, 'LAHCk', False)
        self.assertEqual(alg.parameters['historyLength'], 50)
        self.assertEqual(alg.parameters['mutationoper'], 'FLIPPING')

    def test_budget_is_not_exceeded(self):
        p = KnapsackProblem('kp60_01.txt')
        p.counter = Counter(250)
        alg = LateAcceptanceHillClimbing(p, 'LAHCk')
        # El framework considera valido count <= limit durante el bucle,
        # por eso los algoritmos existentes pueden terminar en limit + 1.
        self.assertLessEqual(p.counter.getCount(), 251)
        self.assertIsNotNone(alg.status.stateFinal.fitness)

    def test_final_state_is_best_or_equal_to_initial(self):
        p = KnapsackProblem('kp60_02.txt')
        p.counter = Counter(1000)
        alg = LateAcceptanceHillClimbing(p, 'LAHCk')
        self.assertGreaterEqual(alg.status.stateFinal.fitness,
                                alg.status.stateInitial.fitness)

    def test_agent_integration(self):
        p = KnapsackProblem('toy3.txt')
        agent = Agent(p, ['LAHC', 'LAHC20', 500, 2])
        agent.init()
        self.assertEqual(agent.stats.nSolutions(), 2)
        self.assertGreaterEqual(agent.stats.getBetter(), 0)

    def test_returns_valid_binary_solution(self):
        p = KnapsackProblem('kp60_03.txt')
        p.counter = Counter(500)
        alg = LateAcceptanceHillClimbing(p, 'LAHC100')
        vals = set(np.asarray(alg.status.stateFinal.vars).tolist())
        self.assertTrue(vals.issubset({-1.0, 1.0}))


if __name__ == '__main__':
    unittest.main()

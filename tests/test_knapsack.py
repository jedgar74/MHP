# Pruebas de la instancia-oraculo de KP: lectura, representacion binaria y
# evaluacion con penalizacion derivada de la instancia.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_knapsack.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.KnapsackProblem import KnapsackProblem
from state.Solution import Solution
from itertools import product

KP_FILE   = "kp_3_1.txt"
N          = 3
CAPACITY  = 50
OPTIMUM    = 220
WEIGHTS   = [10, 20, 30]
PROFITS   = [60, 100, 120]


def evaluate_bits(p, bits):
    """Evalua una solucion desde bits {0,1} mapeados a {-1,+1}."""

    s = Solution(p, "RANDOM")
    s.setValues(2.0 * np.array(bits, dtype=float) - 1.0)
    p.evaluate(s)
    return s


class TestKnapsackProblem(unittest.TestCase):

    def test_problem_metadata(self):
        p = KnapsackProblem(KP_FILE)
        self.assertEqual(p.nameShort, "KP")
        self.assertEqual(p.typeState, "BINARY")
        self.assertEqual(p.typeProblem, "MAX")
        self.assertEqual(p.nVar, N)
        self.assertIsNotNone(p.op, "selOpers() no asigno el operador binario")

    def test_instance_is_read(self):
        p = KnapsackProblem(KP_FILE)
        self.assertEqual(int(p.capacity), CAPACITY)
        self.assertEqual(p.weights.tolist(), WEIGHTS)
        self.assertEqual(p.profits.tolist(), PROFITS)
        self.assertEqual(float(p.optimum), OPTIMUM)

    def test_binary_mapping_matches_ucp_pattern(self):
        s = evaluate_bits(KnapsackProblem(KP_FILE), [0, 1, 1])
        x = (np.asarray(s.vars, dtype=int) + 1) // 2
        self.assertEqual(x.tolist(), [0, 1, 1])
        self.assertEqual(s.vars.tolist(), [-1, 1, 1])

    def test_optimal_solution_is_evaluated(self):
        p = KnapsackProblem(KP_FILE)
        weight, profit = p.packing(evaluate_bits(p, [0, 1, 1]))
        self.assertEqual(weight, 50)
        self.assertEqual(profit, 220)
        self.assertLessEqual(weight, p.capacity)
        self.assertEqual(evaluate_bits(p, [0, 1, 1]).fitness, 220)

    def test_another_feasible_solution(self):
        s = evaluate_bits(KnapsackProblem(KP_FILE), [1, 1, 0])
        self.assertEqual(s.fitness, 160)

    def test_empty_solution_is_feasible(self):
        p = KnapsackProblem(KP_FILE)
        s = evaluate_bits(p, [0, 0, 0])
        weight, profit = p.packing(s)
        self.assertEqual(weight, 0)
        self.assertEqual(profit, 0)
        self.assertEqual(s.fitness, 0)

    def test_infeasible_solution_is_penalized_below_notable_feasible(self):
        p = KnapsackProblem(KP_FILE)
        infeas = evaluate_bits(p, [1, 1, 1])   # peso 60 > 50
        weight, profit = p.packing(infeas)
        self.assertEqual(weight, 60)
        self.assertEqual(profit, 280)
        excess = weight - p.capacity
        self.assertEqual(excess, 10)
        self.assertEqual(p.penalty, sum(PROFITS) + 1)
        self.assertEqual(infeas.fitness, profit - p.penalty * excess)
        self.assertLess(infeas.fitness, 0)

    def test_every_infeasible_solution_has_negative_fitness(self):
        """Con penalty = sum(profits)+1 y exceso >= 1 toda solucion inviable
        queda con fitness < 0, por debajo de la vacia (factible, fitness 0)."""

        p = KnapsackProblem(KP_FILE)
        for bits in product([0, 1], repeat=N):
            s = evaluate_bits(p, bits)
            weight, profit = p.packing(s)
            if weight > p.capacity:
                p.evaluate(s)
                self.assertLess(s.fitness, 0,
                        "inviable %s con peso %d supero 0" % (str(bits), weight))

    def test_reader_rejects_inconsistent_files(self):
        bad = os.path.join("DATA", "instances", "KP", "_bad_kp_tmp.txt")
        cases = [
            ("3 50 220\n10 20\n60 100 120\n", "pesos"),
            ("3 50 220\n10 20 30\n60 100\n", "beneficios"),
            ("0 50 220\n10 20 30\n60 100 120\n", "n"),
        ]
        for content, label in cases:
            with open(bad, "w") as fh:
                fh.write(content)
            try:
                with self.subTest(case=label):
                    with self.assertRaises(ValueError):
                        KnapsackProblem("_bad_kp_tmp.txt")
            finally:
                os.remove(bad)

    def test_truncated_file_raises(self):
        bad = os.path.join("DATA", "instances", "KP", "_bad_kp_tmp.txt")
        with open(bad, "w") as fh:
            fh.write("3 50 220\n10 20 30\n")
        try:
            with self.assertRaises(ValueError):
                KnapsackProblem("_bad_kp_tmp.txt")
        finally:
            os.remove(bad)


if __name__ == "__main__":
    unittest.main(verbosity=2)

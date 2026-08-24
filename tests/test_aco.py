# Pruebas de AntColonyOptimization: validez de permutaciones, contabilidad del
# presupuesto de evaluaciones y calidad respecto al optimo conocido.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_aco.py
#     python -m unittest discover tests/
#     python tests/test_aco.py
import sys, os
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from problem.Counter import Counter
from examples.TravelingSalesmanProblem import TravelingSalesmanProblem
from examples.NQueens import NQueens
from algorithm.AntColonyOptimization import AntColonyOptimization
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.SimulatingAnnealing import SimulatingAnnealing

EIL51_OPT = 426


class TestAntColonyOptimization(unittest.TestCase):

    def setUp(self):
        # Semilla fija: las pruebas de calidad son estocasticas y sin esto
        # fallarian de forma intermitente.
        np.random.seed(7)

    # ------------------------------------------------------------ validez
    def test_build_tour_returns_valid_permutations(self):
        p = TravelingSalesmanProblem("eil51.tsp")
        p.counter = Counter(200)
        aco = AntColonyOptimization(p, "ACOS", False)

        for i in range(50):
            s = aco.buildTour(aco.tau ** 1.0)
            v = np.asarray(s.vars, dtype=int)
            self.assertEqual(sorted(v.tolist()), list(range(p.nVar)),
                    "el tour %d no es una permutacion valida" % i)

    def test_nearest_neighbour_tour_is_valid(self):
        p = TravelingSalesmanProblem("eil51.tsp")
        p.counter = Counter(200)
        aco = AntColonyOptimization(p, "ACOS", False)

        nn = aco.nearestNeighbourTour()
        v = np.asarray(nn.vars, dtype=int)
        self.assertEqual(sorted(v.tolist()), list(range(p.nVar)))

    def test_eta_has_no_division_by_zero(self):
        """eta = 1/(d+eps) debe ser finita pese a d_ii = 0 y coordenadas
        duplicadas, y la diagonal anulada para prohibir el auto-lazo."""

        p = TravelingSalesmanProblem("eil51.tsp")
        p.counter = Counter(200)
        aco = AntColonyOptimization(p, "ACOS", False)

        self.assertTrue(np.all(np.isfinite(aco.eta)), "eta contiene inf o NaN")
        self.assertEqual(aco.eta[0][0], 0.0, "la diagonal de eta no esta anulada")

    # -------------------------------------------------------- presupuesto
    def test_budget_is_not_exceeded_by_any_method(self):
        """ACO evalua por lotes de 'ants'; sin la guarda dentro del lote
        consumiria hasta ants-1 evaluaciones extra y la comparacion contra
        GA y SA dejaria de ser justa.

        isStopCriteria compara con <=, asi que el limite se alcanza en
        limit+1 evaluaciones: lo exigible es que los tres coincidan.
        """

        BUDGET = 1000
        methods = [("ACO", lambda pr: AntColonyOptimization(pr, "ACOS")),
                   ("GA",  lambda pr: GeneticAlgorithm(pr, "GAS")),
                   ("SA",  lambda pr: SimulatingAnnealing(pr, "SAS"))]

        for name, factory in methods:
            with self.subTest(method=name):
                pr = TravelingSalesmanProblem("eil51.tsp")
                pr.counter = Counter(BUDGET)
                factory(pr)
                used = pr.counter.getCount()
                self.assertLessEqual(used, BUDGET + 1,
                        "%s uso %d evaluaciones con limite %d" % (name, used, BUDGET))

    # ------------------------------------------------------------ calidad
    def test_quality_on_eil51(self):
        pr = TravelingSalesmanProblem("eil51.tsp")
        pr.counter = Counter(5000)
        aco = AntColonyOptimization(pr, "ACOS")

        best = aco.status.stateFinal.fitness
        gap = 100.0 * (best - EIL51_OPT) / EIL51_OPT
        print("\n     ACO en eil51 con 5000 evals: best = %.0f  gap = %.2f%%" % (best, gap))

        self.assertEqual(
                sorted(np.asarray(aco.status.stateFinal.vars, dtype=int).tolist()),
                list(range(pr.nVar)),
                "la solucion final no es una permutacion valida")
        self.assertLess(gap, 25.0, "gap de ACO demasiado alto: %.2f%%" % gap)

    # -------------------------------------------------- aplicabilidad
    def test_rejects_problem_without_cost_matrix(self):
        """ACO es constructiva y necesita la matriz de costos. Un problema que
        no la modela debe rechazarse con un mensaje claro, no aceptarse en
        silencio."""

        q = NQueens(10)
        q.counter = Counter(100)

        with self.assertRaises(ValueError) as ctx:
            AntColonyOptimization(q, "ACOS", False)
        self.assertIn("getCostMatrix", str(ctx.exception))

    # ---------------------------------------------------------- defaults
    def test_setparameters_fills_defaults(self):
        """Un JSON incompleto no debe romper la ejecucion."""

        tmp = "./DATA/config/ACO/ACOTEST.json"
        json.dump({"ants": 5}, open(tmp, "w"))
        try:
            p = TravelingSalesmanProblem("eil51.tsp")
            p.counter = Counter(60)
            aco = AntColonyOptimization(p, "ACOTEST", False)

            for k in ["ants", "alpha", "beta", "rho", "q", "elitist",
                      "initialTypeSolution"]:
                self.assertIn(k, aco.parameters, "falta el default de '%s'" % k)
        finally:
            os.remove(tmp)


if __name__ == "__main__":
    unittest.main(verbosity=2)

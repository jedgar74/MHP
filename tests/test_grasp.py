# Valida el GRASP sobre Max-Cut.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_grasp.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.MaxCutProblem import MaxCutProblem
from algorithm.Grasp import Grasp
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.SimulatingAnnealing import SimulatingAnnealing
from algorithm.RandomWalk import RandomWalk
from problem.Counter import Counter
from state.Solution import Solution

# toy4: ciclo de 4 vertices, corte maximo 10.
TOY_OPT = 10
# mc20_1 (20x20 denso). Optimo exacto calculado por fuerza bruta.
MC20_1_OPT = 824


def makeProblem(budget=None, inst="mc20_1.txt"):
    p = MaxCutProblem(inst)
    if budget is not None:
        p.counter = Counter(budget)
    return p


class TestGrasp(unittest.TestCase):
    """Contrato con el framework, mecanica del GRASP y calidad."""

    # ------------------------------------------------------ presupuesto

    def test_budget_is_not_exceeded_by_any_method(self):
        """Todos los metodos binarios deben respetar el mismo presupuesto.

        GRASP evalua por lotes de n flips en la busqueda local; sin la guarda
        dentro del lote se pasaria del cupo. isStopCriteria compara con <=, asi
        que el limite se alcanza en limit+1 evaluaciones: lo exigible es que los
        cuatro coincidan.
        """

        BUDGET = 2000
        methods = [
            ("GRASP", lambda pr: Grasp(pr, "GRASPc")),
            ("GA", lambda pr: GeneticAlgorithm(pr, "GAB")),
            ("SA", lambda pr: SimulatingAnnealing(pr, "SAB")),
            ("RW", lambda pr: RandomWalk(pr, "RWB")),
        ]

        for name, factory in methods:
            with self.subTest(method=name):
                pr = makeProblem(BUDGET)
                factory(pr)
                used = pr.counter.getCount()
                self.assertLessEqual(used, BUDGET + 1,
                        "%s uso %d evaluaciones con limite %d" % (name, used, BUDGET))

    # ------------------------------------------------------ parametros

    def test_setparameters_fills_defaults(self):
        """Un JSON incompleto no debe romper la ejecucion."""

        pr = makeProblem(1500)
        g = Grasp(pr, "GRASPmin", False)

        self.assertIn('alpha', g.parameters)
        self.assertIn('localSearch', g.parameters)
        self.assertEqual(g.parameters.get('localSearch'), 'BEST',
                "no se aplico el valor por defecto de localSearch")
        self.assertEqual(g.parameters.get('alpha'), 0.5,
                "no se respeto el valor que si venia en el JSON")

    # ------------------------------------------------------ construccion

    def test_construct_returns_a_valid_binary_solution(self):
        """La construccion debe entregar n vertices con signo +1 o -1."""

        pr = makeProblem(1500)
        g = Grasp(pr, "GRASPc", False)
        s = g.construct()

        self.assertEqual(len(s.vars), pr.nVar)
        for v in s.vars:
            self.assertIn(float(v), (1.0, -1.0),
                    "la construccion devolvio un valor no binario: %s" % v)

    def test_construct_all_alpha_variants_are_valid(self):
        """Todas las configuraciones de alpha entregan soluciones binarias validas."""

        pr = makeProblem(1500)
        for cfg in ["GRASPg", "GRASPc", "GRASPa05", "GRASPr"]:
            with self.subTest(config=cfg):
                g = Grasp(pr, cfg, False)
                s = g.construct()
                self.assertEqual(len(s.vars), pr.nVar)
                for v in s.vars:
                    self.assertIn(float(v), (1.0, -1.0))

    def test_greedy_construction_beats_uniform_random(self):
        """La construccion voraz (alpha=0) debe partir mucho mejor que un
        reparto uniforme de signos."""

        pr = makeProblem(1500)
        g = Grasp(pr, "GRASPg", False)
        np.random.seed(42)

        greedy = []
        for _ in range(50):
            s = g.construct()
            pr.evaluate(s)
            greedy.append(s.fitness)

        uniform = []
        for _ in range(50):
            s = Solution(pr, "RANDOM")
            pr.evaluate(s)
            uniform.append(s.fitness)

        self.assertGreater(np.mean(greedy), np.mean(uniform),
                "la construccion voraz no supera el reparto aleatorio")

    # ------------------------------------------------------ busqueda local

    def test_local_search_never_worsens(self):
        """La busqueda local no debe devolver nada peor que su entrada."""

        pr = makeProblem(20000)
        g = Grasp(pr, "GRASPc", False)
        s = g.construct()
        pr.evaluate(s)

        mejor = g.localSearch(s)
        self.assertGreaterEqual(mejor.fitness, s.fitness,
                "la busqueda local empeoro la solucion")

    # ------------------------------------------------------ calidad

    def test_grasp_finds_toy_optimum(self):
        """Sobre toy4 (optimo 10) GRASP debe llegar al optimo exacto."""

        np.random.seed(3)
        pr = makeProblem(2000, "toy4.txt")
        g = Grasp(pr, "GRASPc")
        self.assertEqual(g.status.stateFinal.fitness, TOY_OPT,
                "GRASP no encontro el corte maximo de toy4")

    def test_statefinal_is_the_best_seen(self):
        """stateFinal nunca puede ser peor que el arranque constructivo."""

        np.random.seed(5)
        pr = makeProblem(20000)
        g = Grasp(pr, "GRASPc")
        self.assertGreaterEqual(g.status.stateFinal.fitness, g.graspStartCost,
                "stateFinal quedo peor que la solucion constructiva")

    def test_graspstartcost_is_exposed(self):
        """Agent recoge startCosts; GRASP debe exponerlo igual que ACO/TS."""

        pr = makeProblem(20000)
        g = Grasp(pr, "GRASPc")
        self.assertIsNotNone(g.graspStartCost)
        self.assertGreater(g.graspStartCost, 0)

    def test_quality_on_mc20_1(self):
        """GRASP debe quedar dentro del 8 % del optimo exacto de mc20_1."""

        np.random.seed(11)
        pr = makeProblem(20000)
        g = Grasp(pr, "GRASPc")
        best = g.status.stateFinal.fitness
        gap = (MC20_1_OPT - best) / float(MC20_1_OPT) * 100.0

        print("\n     GRASP en mc20_1 con 20000 evals: best = %.0f  gap = %.2f%%  (start = %.0f)"
              % (best, gap, g.graspStartCost))

        self.assertLessEqual(best, MC20_1_OPT + 1e-6,
                "imposible superar el optimo exacto: revisar evaluate()")
        self.assertLess(gap, 8.0, "gap del %.2f%% en mc20_1" % gap)

    def test_search_improves_on_the_constructive_start(self):
        """La busqueda debe aportar por encima de la construccion en mc20_1."""

        np.random.seed(13)
        pr = makeProblem(20000)
        g = Grasp(pr, "GRASPc")

        self.assertGreater(g.status.stateFinal.fitness, g.graspStartCost,
                "GRASP no mejoro el arranque constructivo (%s)" % g.graspStartCost)


if __name__ == "__main__":
    unittest.main(verbosity=2)

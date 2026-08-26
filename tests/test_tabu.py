# Valida la Busqueda Tabu sobre el PFSP (fase 5 del plan).
#
# Se escribio ANTES que algorithm/TabuSearch.py.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_tabu.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.PermutationFlowShopProblem import PermutationFlowShopProblem
from algorithm.TabuSearch import TabuSearch
from algorithm.GeneticAlgorithm import GeneticAlgorithm
from algorithm.SimulatingAnnealing import SimulatingAnnealing
from problem.Counter import Counter
from state.Solution import Solution

# ta001 (20x5). Mejor valor conocido segun DATA/instances/PFSP/opt/optimums.txt.
TA001_BKS = 1278


def makeProblem(budget=None, inst=None):
    p = PermutationFlowShopProblem(inst if inst else ["tai20_5.txt", 1])
    if budget is not None:
        p.counter = Counter(budget)
    return p


class TestTabuSearch(unittest.TestCase):
    """Contrato con el framework, mecanica de la lista tabu y calidad."""

    # ------------------------------------------------------ presupuesto

    def test_budget_is_not_exceeded_by_any_method(self):
        """TS evalua por lotes de (n-1)^2 vecinos.

        Sin la guarda dentro del lote consumiria hasta 360 evaluaciones extra
        con n=20, y la comparacion contra GA y SA dejaria de ser justa.
        isStopCriteria compara con <=, asi que el limite se alcanza en
        limit+1 evaluaciones: lo exigible es que los tres coincidan.
        """

        BUDGET = 2000
        methods = [("TS", lambda pr: TabuSearch(pr, "TSc")),
                   ("GA", lambda pr: GeneticAlgorithm(pr, "GAS")),
                   ("SA", lambda pr: SimulatingAnnealing(pr, "SAS"))]

        for name, factory in methods:
            with self.subTest(method=name):
                pr = makeProblem(BUDGET)
                factory(pr)
                used = pr.counter.getCount()
                self.assertLessEqual(used, BUDGET + 1,
                        "%s uso %d evaluaciones con limite %d" % (name, used, BUDGET))

    def test_neh_alone_respects_a_tiny_budget(self):
        """NEH hace O(n^2) evaluaciones; con presupuesto minusculo debe parar."""

        pr = makeProblem(10)
        TabuSearch(pr, "TSc")
        self.assertLessEqual(pr.counter.getCount(), 11,
                "el arranque NEH ignoro el presupuesto")

    # ------------------------------------------------------ parametros

    def test_setparameters_fills_defaults(self):
        """Un JSON incompleto no debe romper la ejecucion."""

        pr = makeProblem(1500)
        ts = TabuSearch(pr, "TSmin", False)

        self.assertIn('tenure', ts.parameters)
        self.assertIn('aspiration', ts.parameters)
        self.assertIn('initialTypeSolution', ts.parameters)
        self.assertIn('allNeighs', ts.parameters)
        self.assertEqual(ts.parameters.get('neighborhood'), 'INSERTION',
                "no se respeto el valor que si venia en el JSON")

    def test_unknown_neighborhood_raises(self):
        pr = makeProblem(500)
        ts = TabuSearch(pr, "TSc", False)
        ts.parameters.update(dict(neighborhood="NOEXISTE"))
        with self.assertRaises(ValueError):
            ts.run()

    # ------------------------------------------------------ lista tabu

    def test_tabu_attribute_expires_exactly_after_tenure(self):
        """Con tenencia 7, un atributo marcado en la iteracion 0 sigue
        prohibido en la 6 y queda libre en la 7."""

        pr = makeProblem(500)
        ts = TabuSearch(pr, "TSc", False)
        ts.parameters.update(dict(tenure=7))
        ts.tabuList = {}

        ts.addTabu((3, 5, 9), 0)          # el trabajo 3 sale de la posicion 5

        self.assertTrue(ts.isTabu(3, 5, 0),  "deberia estar prohibido al marcarlo")
        self.assertTrue(ts.isTabu(3, 5, 6),  "deberia seguir prohibido en la iteracion 6")
        self.assertFalse(ts.isTabu(3, 5, 7), "deberia quedar libre en la iteracion 7")

    def test_tabu_only_forbids_the_return_position(self):
        """La prohibicion es (trabajo, posicion de origen), no el trabajo entero."""

        pr = makeProblem(500)
        ts = TabuSearch(pr, "TSc", False)
        ts.tabuList = {}
        ts.addTabu((3, 5, 9), 0)

        self.assertTrue(ts.isTabu(3, 5, 1),  "el trabajo 3 no deberia volver a la pos 5")
        self.assertFalse(ts.isTabu(3, 8, 1), "el trabajo 3 si puede ir a la pos 8")
        self.assertFalse(ts.isTabu(4, 5, 1), "el trabajo 4 no tiene por que estar prohibido")

    def test_aspiration_overrides_the_prohibition(self):
        """Un movimiento tabu que mejora el record debe aceptarse igualmente."""

        pr = makeProblem(500)
        ts = TabuSearch(pr, "TSc", False)

        mejor = Solution(pr, "RANDOM")
        mejor.setFitness(1000.0)
        ts.status.stateFinal = mejor

        candidato = Solution(pr, "RANDOM")
        candidato.setFitness(900.0)       # mejor que el record: aspira
        peor = Solution(pr, "RANDOM")
        peor.setFitness(1100.0)           # no aspira

        self.assertTrue(ts.aspires(candidato),
                "un candidato mejor que el record deberia aspirar")
        self.assertFalse(ts.aspires(peor),
                "un candidato peor que el record no deberia aspirar")

    # ------------------------------------------------------ arranque NEH

    def test_neh_returns_a_valid_permutation(self):
        pr = makeProblem(50000)
        ts = TabuSearch(pr, "TSc", False)
        sol = ts.buildNEH()
        vals = sorted(int(x) for x in sol.vars)
        self.assertEqual(vals, list(range(pr.nVar)),
                "NEH no devolvio una permutacion valida")

    def test_neh_is_better_than_a_random_start(self):
        """NEH debe batir claramente la media de arranques aleatorios."""

        pr = makeProblem(50000)
        ts = TabuSearch(pr, "TSc", False)
        sol = ts.buildNEH()
        pr.evaluate(sol)

        np.random.seed(11)
        vals = []
        for _ in range(200):
            r = Solution(pr, "RANDOM")
            pr.evaluate(r)
            vals.append(r.fitness)

        self.assertLess(sol.fitness, np.mean(vals),
                "NEH (%s) no mejora la media aleatoria (%.1f)"
                % (sol.fitness, np.mean(vals)))

    def test_nehcost_is_exposed_like_lnncost(self):
        """Agent recoge startCosts; TS debe exponerlo igual que ACO."""

        pr = makeProblem(20000)
        ts = TabuSearch(pr, "TSc")
        self.assertIsNotNone(ts.nehCost)
        self.assertGreater(ts.nehCost, 0)

    # ------------------------------------------------------ calidad

    def test_statefinal_is_the_best_seen(self):
        """stateFinal nunca puede ser peor que el arranque."""

        pr = makeProblem(20000)
        ts = TabuSearch(pr, "TSc")
        self.assertLessEqual(ts.status.stateFinal.fitness, ts.nehCost,
                "stateFinal quedo peor que la solucion inicial")

    def test_quality_on_ta001(self):
        """TS debe quedar por debajo del 5 % sobre el mejor conocido."""

        pr = makeProblem(20000)
        ts = TabuSearch(pr, "TSc")
        best = ts.status.stateFinal.fitness
        gap = (best - TA001_BKS) / float(TA001_BKS) * 100.0

        print("\n     TS en ta001 con 20000 evals: best = %d  gap = %.2f%%  (NEH = %d)"
              % (best, gap, ts.nehCost))

        self.assertGreaterEqual(best, TA001_BKS,
                "imposible batir el mejor conocido: revisar evaluate()")
        self.assertLess(gap, 5.0, "gap del %.2f%% en ta001" % gap)

    # ------------------------------------------- memoria por solucion

    def test_tabu_mode_defaults_to_solution(self):
        """El modo por defecto es SOLUTION: ATTRIBUTE cicla (ver docstring
        de isForbidden y seccion 3.2 del documento de diseno)."""

        pr = makeProblem(1500)
        ts = TabuSearch(pr, "TSmin", False)
        self.assertEqual(ts.parameters.get('tabuMode'), "SOLUTION")

    def test_solution_memory_is_capped_by_tenure(self):
        pr = makeProblem(500)
        ts = TabuSearch(pr, "TSc", False)
        ts.parameters.update(dict(tenure=5))
        ts.tabuQueue = []
        ts.tabuSet = set()

        for k in range(20):
            s = Solution(pr, "RANDOM")
            s.setValues(np.array(list(range(k, k+pr.nVar)), dtype=int))
            ts.addTabuSolution(s)

        self.assertEqual(len(ts.tabuQueue), 5, "la memoria no respeto la tenencia")
        self.assertEqual(len(ts.tabuSet), 5, "el conjunto y la cola se desincronizaron")

    def test_solution_mode_never_revisits_within_tenure(self):
        """La garantia del modo SOLUTION: no hay ciclos de longitud <= tenencia.

        En modo ATTRIBUTE, sobre ta001, TS entraba en un ciclo de periodo 2 en
        la tercera iteracion y no mejoraba NEH en 166 iteraciones.
        """

        pr = makeProblem(12000)
        ts = TabuSearch(pr, "TSc", False)

        visitadas = []
        original = ts.addTabuSolution

        def espia(sol):
            visitadas.append(ts.signature(sol))
            original(sol)

        ts.addTabuSolution = espia
        ts.run()

        tenure = int(ts.parameters.get('tenure'))
        self.assertGreater(len(visitadas), tenure + 2,
                "la busqueda no dio suficientes pasos para comprobar el ciclo")

        for i in range(len(visitadas)):
            ventana = visitadas[max(0, i-tenure):i]
            self.assertNotIn(visitadas[i], ventana,
                    "se revisito una permutacion dentro de la tenencia (ciclo)")

    def test_search_improves_on_the_neh_start(self):
        """Sobre ta003 la busqueda debe aportar por encima del arranque.

        Se elige ta003 y no ta001 a proposito: en ta001 NEH cae en una meseta
        y ni TS ni ninguna variante la mejoran, asi que no discrimina.
        """

        pr = makeProblem(40000, ["tai20_5.txt", 3])
        ts = TabuSearch(pr, "TSc")

        self.assertLess(ts.status.stateFinal.fitness, ts.nehCost,
                "TS no mejoro el arranque NEH en ta003 (%d)" % ts.nehCost)


if __name__ == "__main__":
    unittest.main(verbosity=2)

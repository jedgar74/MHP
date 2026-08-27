# Valida la Busqueda Local Iterada (ILS) y el Ascenso de Colina (HC) que
# lleva dentro, sobre el QAP.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_ils.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.QuadraticAssignmentProblem import QuadraticAssignmentProblem
from algorithm.IteratedLocalSearch import IteratedLocalSearch
from algorithm.HillClimbing import HillClimbing
from algorithm.SimulatingAnnealing import SimulatingAnnealing
from problem.Counter import Counter
from state.Solution import Solution

# DATA/instances/QAP/opt/optimums.txt
HAD12_BKS = 1652


def makeProblem(budget=None, inst="had12.dat"):
    p = QuadraticAssignmentProblem(inst)
    if budget is not None:
        p.counter = Counter(budget)
    return p


class TestBudget(unittest.TestCase):
    """El presupuesto de evaluaciones es lo que hace comparables las series."""

    def test_budget_is_not_exceeded(self):
        """HC evalua por lotes de n(n-1)/2 vecinos.

        Sin la guarda dentro del lote se pasaria del limite en hasta 66
        evaluaciones con n=12, y la comparacion contra GA y SA dejaria de ser
        justa. isStopCriteria compara con <=, asi que el limite se alcanza en
        limit+1: lo exigible es que ILS no gaste mas que SA.
        """
        budget = 2000

        p = makeProblem(budget)
        np.random.seed(1)
        SimulatingAnnealing(p, "SAS")
        spentSA = p.counter.getCount()

        p = makeProblem(budget)
        np.random.seed(1)
        IteratedLocalSearch(p, "ILSc")
        spentILS = p.counter.getCount()

        self.assertLessEqual(spentILS, spentSA)

    def test_hill_climbing_respects_the_budget(self):
        budget = 500
        p = makeProblem(budget)
        np.random.seed(2)
        HillClimbing(p, "HCc")
        self.assertLessEqual(p.counter.getCount(), budget + 1)

    def test_zero_budget_still_returns_a_solution(self):
        """Con presupuesto agotado debe devolver la inicial, no None."""
        p = makeProblem(0)
        np.random.seed(3)
        ils = IteratedLocalSearch(p, "ILSc")
        self.assertIsNotNone(ils.status.stateFinal)
        self.assertIsNotNone(ils.status.stateFinal.fitness)


class TestPerturbation(unittest.TestCase):
    """La perturbacion es la pieza que distingue a ILS de un multiarranque."""

    def setUp(self):
        self.p = makeProblem(10000)
        np.random.seed(5)
        self.ils = IteratedLocalSearch(self.p, "ILSc", False)
        self.sol = Solution(self.p, "RANDOM")
        self.p.evaluate(self.sol)

    def test_blocking_returns_a_valid_permutation(self):
        for _ in range(30):
            u = self.ils.perturbBlocking(self.sol)
            self.assertEqual(sorted(int(x) for x in u.vars),
                             list(range(self.p.nVar)))

    def test_swapping_returns_a_valid_permutation(self):
        for _ in range(30):
            u = self.ils.perturbSwapping(self.sol)
            self.assertEqual(sorted(int(x) for x in u.vars),
                             list(range(self.p.nVar)))

    def test_perturbation_clears_the_stale_fitness(self):
        """Si arrastrara el fitness viejo, comparar sin evaluar daria un
        resultado silenciosamente falso."""
        u = self.ils.perturbBlocking(self.sol)
        self.assertIsNone(u.fitness)
        u = self.ils.perturbSwapping(self.sol)
        self.assertIsNone(u.fitness)

    def test_blocking_actually_moves_the_solution(self):
        u = self.ils.perturbBlocking(self.sol)
        self.assertFalse(u.isEquals(self.sol))

    def test_blocking_changes_more_than_a_single_swap(self):
        """Esta es la razon de ser del double bridge.

        Reordena la permutacion en A C B D, lo que altera cuatro adyacencias
        de golpe. Un intercambio simple solo puede tocar dos posiciones, asi
        que la busqueda local no puede deshacer el salto en un solo movimiento
        y se ve obligada a descender hacia otro optimo local.
        """
        np.random.seed(7)
        moved = []
        for _ in range(20):
            u = self.ils.perturbBlocking(self.sol)
            d = sum(1 for i in range(self.p.nVar)
                    if int(u.vars[i]) != int(self.sol.vars[i]))
            moved.append(d)
        self.assertGreater(max(moved), 2)

    def test_swapping_strength_controls_how_far_it_jumps(self):
        """Con k=1 toca dos posiciones; con k grande, mas."""
        self.ils.parameters.update(dict(perturbationStrength=1))
        np.random.seed(9)
        u = self.ils.perturbSwapping(self.sol)
        d1 = sum(1 for i in range(self.p.nVar)
                 if int(u.vars[i]) != int(self.sol.vars[i]))
        self.assertEqual(d1, 2)

    def test_unknown_perturbation_is_rejected(self):
        self.ils.parameters.update(dict(perturbation="NOEXISTE"))
        with self.assertRaises(ValueError):
            self.ils.perturb(self.sol)


class TestHillClimbing(unittest.TestCase):
    """La busqueda local que ILS invoca una y otra vez."""

    def test_never_returns_something_worse_than_its_start(self):
        p = makeProblem(5000)
        np.random.seed(11)
        hc = HillClimbing(p, "HCc", False)
        start = Solution(p, "RANDOM")
        p.evaluate(start)
        end = hc.hillClimbing(start)
        self.assertLessEqual(end.fitness, start.fitness)

    def test_stops_at_a_local_optimum(self):
        """Al terminar, ningun vecino debe mejorar: esa es la definicion."""
        p = makeProblem(20000)
        np.random.seed(13)
        hc = HillClimbing(p, "HCc", False)
        start = Solution(p, "RANDOM")
        p.evaluate(start)
        end = hc.hillClimbing(start)

        for neighbour, move in p.op.neighborhood("SWAP", end, None):
            p.evaluate(neighbour)
            self.assertGreaterEqual(neighbour.fitness, end.fitness)

    def test_defaults_fill_in_a_partial_configuration(self):
        p = makeProblem(100)
        hc = HillClimbing(p, "HCc", False)
        for key in ("neighborhood", "strategy", "allNeighs", "factorNeighs"):
            self.assertIn(key, hc.parameters)


class TestIteratedLocalSearch(unittest.TestCase):
    """Contrato con el framework y calidad."""

    def test_reads_its_configuration(self):
        p = makeProblem(100)
        ils = IteratedLocalSearch(p, "ILSc", False)
        for key in ("localSearch", "configLocalSearch", "perturbation",
                    "perturbationStrength", "nonImprovingLimit", "acceptance"):
            self.assertIn(key, ils.parameters)

    def test_builds_its_local_search_from_the_configured_file(self):
        """INCLUDEMETHODS/CONFIGMETHODS de los .cfg originales."""
        p = makeProblem(100)
        ils = IteratedLocalSearch(p, "ILSFb", False)
        self.assertIsInstance(ils.localSearch, HillClimbing)
        self.assertEqual(ils.parameters.get("configLocalSearch"), "HCF")
        self.assertEqual(ils.localSearch.parameters.get("factorNeighs"), 4)

    def test_final_state_is_evaluated_and_is_a_permutation(self):
        p = makeProblem(3000)
        np.random.seed(17)
        ils = IteratedLocalSearch(p, "ILSc")
        s = ils.status.stateFinal
        self.assertIsNotNone(s.fitness)
        self.assertEqual(sorted(int(x) for x in s.vars), list(range(p.nVar)))

    def test_final_state_fitness_matches_a_fresh_evaluation(self):
        """Blinda contra devolver un fitness que no corresponde a las vars."""
        p = makeProblem(3000)
        np.random.seed(19)
        ils = IteratedLocalSearch(p, "ILSc")
        reported = ils.status.stateFinal.fitness
        p.evaluate(ils.status.stateFinal)
        self.assertAlmostEqual(reported, ils.status.stateFinal.fitness, places=6)

    def test_never_worse_than_its_own_initial_solution(self):
        p = makeProblem(3000)
        np.random.seed(23)
        ils = IteratedLocalSearch(p, "ILSc")
        self.assertLessEqual(ils.status.stateFinal.fitness,
                             ils.status.stateInitial.fitness)

    def test_beats_the_bare_local_search(self):
        """La razon de existir del envoltorio.

        Con el mismo presupuesto, iterar la busqueda local desde optimos
        locales perturbados tiene que ganarle a lanzarla una sola vez.
        """
        budget = 5000

        p = makeProblem(budget)
        np.random.seed(29)
        hc = HillClimbing(p, "HCc")

        p = makeProblem(budget)
        np.random.seed(29)
        ils = IteratedLocalSearch(p, "ILSc")

        self.assertLess(ils.status.stateFinal.fitness, hc.status.stateFinal.fitness)

    def test_reaches_the_known_optimum_of_had12(self):
        """had12 = 1652, el mismo valor que ILS obtiene en el fichero
        DATA/output/QAP 28_5_2019 18_17.txt del repositorio."""
        p = makeProblem(10000)
        np.random.seed(31)
        ils = IteratedLocalSearch(p, "ILSc")
        self.assertAlmostEqual(ils.status.stateFinal.fitness, HAD12_BKS, places=6)

    def test_restart_triggers_when_progress_stalls(self):
        """Con un limite muy bajo el reinicio debe dispararse."""
        p = makeProblem(6000)
        np.random.seed(37)
        ils = IteratedLocalSearch(p, "ILSc", False)
        ils.parameters.update(dict(nonImprovingLimit=200))
        ils.iteratedLocalSearch()
        self.assertGreater(ils.nRestarts, 0)

    def test_random_walk_acceptance_accepts_more_than_better(self):
        """RW acepta siempre; BETTER solo si mejora."""
        budget = 4000

        p = makeProblem(budget)
        np.random.seed(41)
        better = IteratedLocalSearch(p, "ILSc")

        p = makeProblem(budget)
        np.random.seed(41)
        rw = IteratedLocalSearch(p, "ILSrw")

        self.assertGreaterEqual(rw.nAccepted, better.nAccepted)

    def test_run_accepts_an_external_solution(self):
        """Contrato que usan las metaheuristicas cooperativas."""
        p = makeProblem(2000)
        np.random.seed(43)
        ils = IteratedLocalSearch(p, "ILSc", False)
        seed = Solution(p, "RANDOM")
        p.evaluate(seed)
        ils.run(seed)
        self.assertIsNotNone(ils.status.stateFinal.fitness)


class TestAgentIntegration(unittest.TestCase):
    """Registro en agent/Agent.py."""

    def test_agent_runs_ils_and_hc_on_qap(self):
        from agent.Agent import Agent
        import io, contextlib

        for method, config in (("ILS", "ILSc"), ("HC", "HCc")):
            p = QuadraticAssignmentProblem("had12.dat")
            np.random.seed(47)
            with contextlib.redirect_stdout(io.StringIO()):
                a = Agent(p, [method, config, 2000, 2])
                a.init()
            self.assertEqual(len(a.stats.solutions), 2, method)
            self.assertGreaterEqual(a.stats.getBetter(), HAD12_BKS, method)


if __name__ == "__main__":
    unittest.main()

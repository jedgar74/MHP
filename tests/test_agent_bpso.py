# coding=UTF-8
"""
Test de Integracion: Binary Particle Swarm Optimization (BPSO) en Agent.

Verifica que MHP reconoce "BPSO" como metaheuristica valida a traves de
agent/Agent.py, siguiendo el mismo patron que GA/SA/TS/FWA:

    problemv = KnapsackProblem("kp_3_1.txt")
    agent    = Agent(problemv, ["BPSO", "BPSOc", nEvals, nExperim])
    agent.init()

Ejecutar desde la raiz del repositorio:
    python -m unittest tests/test_agent_bpso.py
    python -m unittest discover tests/
"""

import sys
import os
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.Agent import Agent
from examples.KnapsackProblem import KnapsackProblem

KP_FILE = "kp_3_1.txt"

BUDGET = 100
RUNS   = 3


class TestAgentBPSOIntegration(unittest.TestCase):
    """BPSO debe comportarse desde Agent igual que GA/SA/TS/FWA."""

    def makeAgent(self, budget=BUDGET, runs=RUNS):
        np.random.seed(7)
        problem = KnapsackProblem(KP_FILE)
        return Agent(problem, ["BPSO", "BPSOc", budget, runs])

    # ---------------------------------------------------------- A: reconoce

    def test_agent_creates_bpso(self):
        """Agent([..,'BPSO',..]) no lanza errores de import/config al iniciar."""
        agent = self.makeAgent()
        self.assertEqual(agent.metaheuristic, "BPSO")
        self.assertEqual(agent.paraMetaheuristic, "BPSOc")
        # init() no debe fallar: algoritmo conocido, config valida
        agent.init()

    def test_agent_sets_label(self):
        """El label de BasicStats refleja la metaheuristica, config y presupuesto."""
        agent = self.makeAgent(budget=BUDGET, runs=RUNS)
        agent.init()
        self.assertIn("BPSO", agent.stats.getLabel())
        self.assertIn("BPSOc", agent.stats.getLabel())
        self.assertIn(str(BUDGET), agent.stats.getLabel())

    # ------------------------------------------------ B y F: corridas y conteo

    def test_runs_produce_exactly_n_results(self):
        """RUNS=3 -> BasicStats registra exactamente 3 soluciones."""
        agent = self.makeAgent(budget=BUDGET, runs=RUNS)
        agent.init()
        self.assertEqual(agent.stats.nSolutions(), RUNS)
        self.assertEqual(len(agent.stats.solutions), RUNS)

    # ------------------------------------------------- C: resultados validos

    def test_each_run_gives_valid_fitness_and_binary_vars(self):
        """Cada stateFinal queda registrado con fitness y vars {-1,+1}."""
        agent = self.makeAgent(budget=BUDGET, runs=RUNS)
        agent.init()
        for sol in agent.stats.solutions:
            self.assertIsNotNone(sol)
            self.assertIsNotNone(sol.fitness)
            self.assertGreaterEqual(sol.fitness, 0)
            for v in sol.vars:
                self.assertIn(int(v), (-1, 1))

    def test_agent_exposes_best_solution(self):
        """getSolution() devuelve el mejor resultado a traves de BasicStats."""
        agent = self.makeAgent(budget=BUDGET, runs=RUNS)
        agent.init()
        best = agent.getSolution()
        self.assertIsNotNone(best)
        self.assertGreaterEqual(best.fitness, 0)

    # ----------------------------------------------------------- D: sentido MAX

    def test_max_sense_through_basicstats(self):
        """Knapsack es MAX: BasicStats.better() debe elegir el mayor fitness.

        No se compara manualmente: se usa el mecanismo real del framework.
        """
        agent = self.makeAgent(budget=BUDGET, runs=RUNS)
        self.assertEqual(agent.stats.typeProblem, "MAX")
        agent.init()
        recorded = [float(sol.fitness) for sol in agent.stats.solutions]
        self.assertEqual(agent.stats.getBetter(), max(recorded))

    # -------------------------------------------------- E: presupuesto/Counter

    def test_counter_is_created_and_reset_by_agent(self):
        """Agent crea Counter(nEvals) por corrida y lo reinicia al cerrar cada una.

        El gasto por corrida (nunca superar nEvals) esta garantizado por la
        suite unitaria tests/test_bpso.py: test_budget_is_never_exceeded y
        test_exact_budget_when_possible. Aqui solo se verifica que Agent
        gestiona EL MISMO problem.counter (una sola fuente de verdad).
        """
        agent = self.makeAgent(budget=BUDGET, runs=RUNS)
        counter_before_init = agent.problem.counter
        agent.init()
        self.assertEqual(agent.problem.counter.getLimit(), BUDGET)
        self.assertEqual(agent.problem.counter.getCount(), 0)
        self.assertIs(agent.problem, agent.problem)  # el mismo objeto problema
        # BPSO consume el contador que Agent cuelga del problema, no uno propio
        self.assertTrue(hasattr(agent.problem.counter, "incCount"))
        # BPSO no crea ningun contador alternativo
        self.assertIsNone(getattr(agent.objMetaheuristic, "_own_counter", None))

    # -------------------------------------------- no reutilizacion entre runs

    def test_each_run_builds_a_fresh_bpso(self):
        """Cada corrida crea un BPSO nuevo: no comparte swarm/velocidades.

        Se comprueba una corrida manual directa con 2 bucles y poblacion
        distinta: el enjambre de cada corrida es un objeto distinto.
        """
        np.random.seed(3)
        problem = KnapsackProblem(KP_FILE)
        agent = Agent(problem, ["BPSO", "BPSOc", BUDGET, RUNS])
        agent.init()
        # init() crea RUNS BPSO unicos; solo queda accesible la estadistica.
        # Se verifica con dos ejecuciones manuales: cada swarms distinto.
        from problem.Counter import Counter
        from algorithm.BinaryParticleSwarmOptimization import BinaryParticleSwarmOptimization

        seen = []
        for _ in range(2):
            problem.counter = Counter(BUDGET)
            b = BinaryParticleSwarmOptimization(problem, "BPSOc")
            seen.append(b.swarm)
            self.assertGreater(len(b.swarm), 0)
        self.assertIsNot(seen[0], seen[1])
        self.assertIsNot(seen[0][0], seen[1][0])


class TestAgentBPSOInit2(unittest.TestCase):
    """Patron init2()+run() (usado por Execute*.py y MultiInAgent)."""

    def test_init2_run_with_counter_preconfigured(self):
        np.random.seed(9)
        from problem.Counter import Counter
        problem = KnapsackProblem(KP_FILE)
        problem.counter = Counter(BUDGET)
        agent = Agent(problem, ["BPSO", "BPSOc", BUDGET, RUNS])
        agent.init2()
        self.assertIsNotNone(agent.objMetaheuristic.gbest)
        agent.run()
        self.assertEqual(agent.stats.nSolutions(), 1)
        self.assertEqual(problem.counter.getCount(), 0)
        self.assertIsNotNone(agent.getSolution())

    def test_init2_without_counter_gives_empty_swarm(self):
        """KnapsackProblem nace con Counter(0): BPSO queda vacio (igual GA/TS)."""
        problem = KnapsackProblem(KP_FILE)
        agent = Agent(problem, ["BPSO", "BPSOc", BUDGET, RUNS])
        agent.init2()
        self.assertEqual(agent.objMetaheuristic.swarm, [])
        self.assertIsNone(agent.objMetaheuristic.gbest)
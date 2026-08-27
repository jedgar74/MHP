# Pruebas de BinaryParticleSwarmOptimization: invariantes del algoritmo BPSO sobre
# la instancia KP con representacion binaria {-1,+1}.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_bpso.py
#     python -m unittest discover tests/
import sys, os
import unittest
import copy
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.KnapsackProblem import KnapsackProblem
from state.Solution import Solution
from algorithm.BinaryParticleSwarmOptimization import BinaryParticleSwarmOptimization

KP_FILE   = "kp_3_1.txt"
N         = 3

CONFIG_DIR = os.path.join("DATA", "config", "BPSO")
CONFIG_REF = {
    "particles": 4,
    "w": 0.5,
    "c1": 0.5,
    "c2": 0.5,
    "vmax": 4.0,
    "initialTypeSolution": "RANDOM",
}


class BPSOBuilder(unittest.TestCase):

    def makeProblem(self, budget):
        from problem.Counter import Counter
        p = KnapsackProblem(KP_FILE)
        p.counter = Counter(budget)
        return p

    def makeBPSO(self, budget, overrides=None, run=True):
        """Crea un BPSO sobre un config temporal y lo devuelve con su problema.

        El config temporal se elimina siempre (try/finally). Cada test fija
        np.random.seed ANTES de crear el BPSO para que la inicializacion sea
        determinista, de modo que el test pueda apoyarse en las evaluaciones."""
        np.random.seed(7)
        p = self.makeProblem(budget)

        params = dict(CONFIG_REF)
        if overrides:
            params.update(overrides)

        cfg = os.path.join(CONFIG_DIR, "_test.json")
        with open(cfg, "w") as f:
            json.dump(params, f)

        try:
            bpso = BinaryParticleSwarmOptimization(p, "_test", run=run)
        finally:
            if os.path.exists(cfg):
                os.remove(cfg)

        return p, bpso


class TestBPSOConfig(BPSOBuilder, unittest.TestCase):

    def test_short_term(self):
        _, bpso = self.makeBPSO(60)
        self.assertEqual(bpso.shortTerm, "BPSO")

    def test_defaults_when_missing(self):
        cfg = os.path.join(CONFIG_DIR, "_missing.json")
        with open(cfg, "w") as f:
            json.dump({"particles": 2, "vmax": 3.0}, f)
        try:
            bpso = BinaryParticleSwarmOptimization(self.makeProblem(60), "_missing", run=False)
        finally:
            os.remove(cfg)
        self.assertEqual(int(bpso.parameters.get("particles")), 2)
        self.assertAlmostEqual(float(bpso.parameters.get("c1")), 1.49445)
        self.assertAlmostEqual(float(bpso.parameters.get("c2")), 1.49445)
        self.assertAlmostEqual(float(bpso.parameters.get("w")), 0.729)
        self.assertEqual(bpso.parameters.get("initialTypeSolution"), "RANDOM")

    def test_invalid_particles_raise(self):
        self.assertRaises(ValueError, self.makeBPSO, 60, {"particles": 0})
        self.assertRaises(ValueError, self.makeBPSO, 60, {"particles": -3})

    def test_invalid_vmax_raises(self):
        self.assertRaises(ValueError, self.makeBPSO, 60, {"vmax": 0})
        self.assertRaises(ValueError, self.makeBPSO, 60, {"vmax": -1})

    def test_invalid_c_raises(self):
        self.assertRaises(ValueError, self.makeBPSO, 60, {"c1": -1})
        self.assertRaises(ValueError, self.makeBPSO, 60, {"c2": -1})

    def test_budget_zero_gives_empty_swarm(self):
        p, bpso = self.makeBPSO(0, run=True)
        self.assertEqual(bpso.swarm, [])
        self.assertEqual(bpso.pbest, [])
        self.assertIsNone(bpso.gbest)
        self.assertIsNone(bpso.status.stateInitial)
        self.assertIsNone(bpso.status.stateFinal)
        self.assertEqual(p.counter.getCount(), 0)

    def test_budget_smaller_than_particles(self):
        p, bpso = self.makeBPSO(2, {"particles": 4}, run=True)
        self.assertEqual(len(bpso.swarm), 2)
        self.assertEqual(len(bpso.pbest), 2)
        self.assertEqual(bpso.velocities.shape, (2, N))
        self.assertEqual(p.counter.getCount(), 2)


class TestBPSOInvariants(BPSOBuilder, unittest.TestCase):

    def test_positions_are_binary_after_updates(self):
        _, bpso = self.makeBPSO(20, {"particles": 2}, run=False)
        np.random.seed(11)
        bpso.binaryParticleSwarmOptimization()
        for sol in bpso.swarm:
            for v in sol.vars:
                self.assertIn(int(v), (-1, 1))
        for sol in bpso.pbest:
            for v in sol.vars:
                self.assertIn(int(v), (-1, 1))
        for v in bpso.gbest.vars:
            self.assertIn(int(v), (-1, 1))

    def test_velocities_are_clipped(self):
        p, bpso = self.makeBPSO(20, {"particles": 2, "vmax": 4.0}, run=False)
        np.random.seed(5)
        vmax = float(bpso.parameters.get("vmax"))
        bpso.binaryParticleSwarmOptimization()
        vel = bpso.velocities
        self.assertGreaterEqual(vel.min(), -vmax)
        self.assertLessEqual(vel.max(), vmax)

    def test_sigmoid_shape(self):
        _, bpso = self.makeBPSO(60, run=False)
        self.assertAlmostEqual(bpso.sigmoid(0.0), 0.5, places=6)
        self.assertGreater(bpso.sigmoid(2.0), 0.5)
        self.assertLess(bpso.sigmoid(-2.0), 0.5)

    def test_pbest_gbest_respect_op(self):
        """gbest debe ser el mejor de los pbest segun el operador (MAX)."""
        _, bpso = self.makeBPSO(12, {"particles": 2}, run=False)
        op = bpso.objProblem.op
        # gbest no debe ser PEOR que ningun pbest
        for sol in bpso.pbest:
            self.assertFalse(op.isBetter([sol, bpso.gbest]))
        # gbest debe ser al MENOS tan bueno como cualquiera
        best_value = max(float(sol.fitness) for sol in bpso.pbest)
        self.assertEqual(float(bpso.gbest.fitness), best_value)

    def test_budget_is_never_exceeded(self):
        for budget in (5, 11, 20, 60):
            with self.subTest(budget=budget):
                p, bpso = self.makeBPSO(budget, {"particles": 4}, run=True)
                np.random.seed(3)
                # run=True ya ejecuto; volver a ejecutar suma mas evaluaciones
                # -> solo comprobar que no supero el presupuesto tras una corrida
                self.assertLessEqual(p.counter.getCount(), budget)

    def test_exact_budget_when_possible(self):
        p, bpso = self.makeBPSO(11, {"particles": 4}, run=False)
        np.random.seed(3)
        bpso.binaryParticleSwarmOptimization()
        self.assertEqual(p.counter.getCount(), 11)


class TestBPSODeepCopy(BPSOBuilder, unittest.TestCase):

    def test_mutating_particle_does_not_change_pbest_gbest(self):
        p, bpso = self.makeBPSO(12, {"particles": 2}, run=False)
        old_fit_pbest = copy.deepcopy(bpso.pbest[0].fitness)
        old_fit_gbest = copy.deepcopy(bpso.gbest.fitness)

        # Forzar una mutacion de la particula 0
        bpso.swarm[0].setValues(-bpso.swarm[0].vars)
        p.evaluate(bpso.swarm[0])

        self.assertEqual(bpso.pbest[0].fitness, old_fit_pbest)
        self.assertEqual(bpso.gbest.fitness, old_fit_gbest)


class TestBPSOSmoke(BPSOBuilder, unittest.TestCase):

    def test_smoke_on_toy_does_not_crash_and_stays_in_limits(self):
        p, bpso = self.makeBPSO(60, {"particles": 4}, run=True)
        used = p.counter.getCount()
        self.assertLessEqual(used, 60)
        self.assertIsNotNone(bpso.status.stateFinal.fitness)
        for v in bpso.status.stateFinal.vars:
            self.assertIn(int(v), (-1, 1))

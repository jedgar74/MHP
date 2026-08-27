# coding=UTF-8
"""
Pruebas unitarias para FireworksAlgorithm (FWA).

Valida el contrato con el framework (respeto estricto del presupuesto de
evaluaciones), el manejo de parametros por defecto, la validez y calidad de
soluciones en problemas continuos (Ackley) y combinatorios/permutacionales (PFSP/TSP),
y la mecanica de generacion de chispas y mutacion gaussiana.

Ejecutar desde la raiz del repositorio:
    python -m unittest tests/test_fireworks.py
    python -m unittest discover tests/
"""

import sys
import os
import unittest
import json
import copy
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from problem.Counter import Counter
from state.Solution import Solution
from state.Population import Population
from examples.Ackley import Ackley
from examples.PermutationFlowShopProblem import PermutationFlowShopProblem
from examples.TravelingSalesmanProblem import TravelingSalesmanProblem
from algorithm.FireworksAlgorithm import FireworksAlgorithm


class TestFireworksAlgorithm(unittest.TestCase):
    """Pruebas unitarias de Fireworks Algorithm."""

    def setUp(self):
        np.random.seed(42)

    # ------------------------------------------------------ Presupuesto y Contrato
    def test_budget_is_not_exceeded_on_continuous_problem(self):
        """FWA no debe exceder el presupuesto de evaluaciones en problemas continuos (Ackley)."""
        BUDGET = 200
        prob = Ackley("Ackley.json")
        prob.counter = Counter(BUDGET)

        fwa = FireworksAlgorithm(prob, "FWAc")
        used = prob.counter.getCount()
        self.assertLessEqual(used, BUDGET + 1,
            "FWA uso %d evaluaciones con limite %d en Ackley" % (used, BUDGET))

    def test_budget_is_not_exceeded_on_permutational_problem(self):
        """FWA no debe exceder el presupuesto en problemas permutacionales (PFSP)."""
        BUDGET = 500
        prob = PermutationFlowShopProblem(["tai20_5.txt", 1])
        prob.counter = Counter(BUDGET)

        fwa = FireworksAlgorithm(prob, "FWAc")
        used = prob.counter.getCount()
        self.assertLessEqual(used, BUDGET + 1,
            "FWA uso %d evaluaciones con limite %d en PFSP" % (used, BUDGET))

    # ------------------------------------------------------ Parametros por Defecto
    def test_setparameters_fills_defaults(self):
        """Un archivo de configuracion incompleto debe rellenar los parametros por defecto."""
        tmp_cfg = "./DATA/config/FWA/FWATEST_TEMP.json"
        with open(tmp_cfg, "w") as fh:
            json.dump({"fireworks": 8}, fh)

        try:
            prob = Ackley("Ackley.json")
            prob.counter = Counter(50)
            fwa = FireworksAlgorithm(prob, "FWATEST_TEMP", run=False)

            self.assertEqual(fwa.parameters.get("fireworks"), 8)
            self.assertEqual(fwa.parameters.get("initialTypeSolution"), "RANDOM")
            self.assertEqual(fwa.parameters.get("version"), "BASIC")
            self.assertEqual(fwa.parameters.get("m"), 4)
            self.assertEqual(fwa.parameters.get("a"), 0.3)
            self.assertEqual(fwa.parameters.get("b"), 0.7)
            self.assertEqual(fwa.parameters.get("aprime"), 3)
        finally:
            if os.path.exists(tmp_cfg):
                os.remove(tmp_cfg)

    # ------------------------------------------------------ Resolucion Continua (Ackley)
    def test_continuous_ackley_optimization(self):
        """Demuestra la eficacia de FWA optimizando la funcion continua multimodal Ackley."""
        prob = Ackley("Ackley.json")
        prob.counter = Counter(1500)

        # Generar una solucion aleatoria de referencia
        random_sol = Solution(prob, "RANDOM")
        prob.evaluate(random_sol)
        random_fitness = random_sol.fitness

        fwa = FireworksAlgorithm(prob, "FWAc")
        final_sol = fwa.status.stateFinal

        self.assertIsNotNone(final_sol)
        self.assertIsNotNone(final_sol.fitness)
        # La solucion final de FWA debe mejorar sustancialmente el arranque aleatorio
        self.assertLess(final_sol.fitness, random_fitness,
            "FWA (%.4f) no mejoro la solucion aleatoria inicial (%.4f)" % (final_sol.fitness, random_fitness))
        # En Ackley con 1500 evaluaciones en 2D debe descender hacia el optimo global f(0,0)=0
        self.assertLess(final_sol.fitness, 15.0,
            "El fitness obtenido en Ackley (%.4f) fue demasiado alto" % final_sol.fitness)

    def test_continuous_bounds_respected(self):
        """Todas las variables generadas por displacement y mutation deben respetar los limites."""
        prob = Ackley("Ackley.json")
        prob.counter = Counter(500)
        fwa = FireworksAlgorithm(prob, "FWAc")

        final_vars = fwa.status.stateFinal.vars
        for i in range(prob.nVar):
            self.assertGreaterEqual(final_vars[i], prob.lowerlimits[i],
                "Variable %d menor al limite inferior" % i)
            self.assertLessEqual(final_vars[i], prob.upperlimits[i],
                "Variable %d mayor al limite superior" % i)

    # ------------------------------------------------------ Resolucion Permutacional (PFSP & TSP)
    def test_permutational_pfsp_validity_and_quality(self):
        """FWA sobre PFSP debe mantener siempre permutaciones validas y mejorar o igualar el arranque."""
        prob = PermutationFlowShopProblem(["tai20_5.txt", 1])
        prob.counter = Counter(2000)

        fwa = FireworksAlgorithm(prob, "FWAc")
        final_sol = fwa.status.stateFinal
        v = np.asarray(final_sol.vars, dtype=int).tolist()

        self.assertEqual(sorted(v), list(range(prob.nVar)),
            "La solucion final de FWA en PFSP no es una permutacion valida")
        self.assertLessEqual(final_sol.fitness, fwa.status.stateInitial.fitness,
            "La solucion final empeoro respecto a la inicial")

    def test_permutational_tsp_validity(self):
        """FWA sobre TSP debe generar un tour valido."""
        prob = TravelingSalesmanProblem("eil51.tsp")
        prob.counter = Counter(1000)

        fwa = FireworksAlgorithm(prob, "FWAc")
        final_sol = fwa.status.stateFinal
        v = np.asarray(final_sol.vars, dtype=int).tolist()

        self.assertEqual(sorted(v), list(range(prob.nVar)),
            "El tour final en TSP no es una permutacion valida")

    # ------------------------------------------------------ Mecanica de FWA (Sparks & Amplitudes)
    def test_sparks_calculation_logic(self):
        """Calculo de chispas asigna mas chispas a mejores soluciones y acota dentro de limites."""
        prob = Ackley("Ackley.json")
        prob.counter = Counter(100)
        fwa = FireworksAlgorithm(prob, "FWAc", run=False)

        s = fwa.nSparks()
        self.assertEqual(len(s), fwa.popul.popSize)
        self.assertTrue(np.all(s >= 0), "El numero de chispas no puede ser negativo")
        # El mejor individuo (indice 0) debe recibir al menos tantas chispas como el peor (ultimo)
        self.assertGreaterEqual(s[0], s[-1],
            "El mejor fuego artificial deberia recibir >= chispas que el peor")

    def test_amplitudes_calculation_logic(self):
        """Calculo de amplitudes asigna menor amplitud de busqueda a mejores soluciones (explotacion)."""
        prob = Ackley("Ackley.json")
        prob.counter = Counter(100)
        fwa = FireworksAlgorithm(prob, "FWAc", run=False)

        a = fwa.amplitudes()
        self.assertEqual(len(a), fwa.popul.popSize)
        self.assertTrue(np.all(a >= 0), "Las amplitudes no pueden ser negativas")
        # El mejor individuo debe tener menor amplitud que el peor (busqueda local vs global)
        self.assertLessEqual(a[0], a[-1] + 1e-6,
            "El mejor individuo deberia tener menor amplitud de explosion para explotar")

    def test_run_method_integration(self):
        """El metodo run() y replaceSolution() deben funcionar correctamente."""
        prob = Ackley("Ackley.json")
        prob.counter = Counter(300)
        fwa = FireworksAlgorithm(prob, "FWAc", run=False)

        fwa.run()
        self.assertIsNotNone(fwa.status.stateFinal)

        new_sol = Solution(prob, "RANDOM")
        prob.evaluate(new_sol)
        fwa.replaceSolution(new_sol)
        self.assertEqual(fwa.status.stateFinal.fitness, new_sol.fitness)


if __name__ == "__main__":
    unittest.main(verbosity=2)

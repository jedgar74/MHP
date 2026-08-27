# coding=UTF-8
"""
Test Comparativo de Eficiencia: FireworksAlgorithm (FWA) vs TabuSearch (TS).

Compara de forma rigurosa la eficiencia, tiempo de computo, convergencia y
calidad de solucion de Fireworks Algorithm frente a Tabu Search sobre el
Permutation Flow Shop Scheduling Problem (PFSP) con instancias de Taillard (tai20_5.txt).

Ejecutar desde la raiz del repositorio:
    python -m unittest tests/test_comparative_fwa_vs_ts.py
    python -m unittest discover tests/
"""

import sys
import os
import unittest
import time
import copy
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from problem.Counter import Counter
from state.Solution import Solution
from examples.PermutationFlowShopProblem import PermutationFlowShopProblem
from algorithm.FireworksAlgorithm import FireworksAlgorithm
from algorithm.TabuSearch import TabuSearch

# Instancia ta001 (20 trabajos, 5 maquinas). Mejor valor conocido segun opt/optimums.txt
TA001_BKS = 1278


def create_pfsp_instance(instance_idx=1, budget=2000):
    """Crea una instancia de PFSP con presupuesto acotado."""
    problem = PermutationFlowShopProblem(["tai20_5.txt", instance_idx])
    problem.counter = Counter(budget)
    return problem


class TestComparativeFireworksVsTabu(unittest.TestCase):
    """Suite de pruebas comparativas de eficiencia entre FWA y TS."""

    def setUp(self):
        np.random.seed(123)

    # ------------------------------------------------------ Presupuesto y Equidad
    def test_both_algorithms_respect_exact_same_evaluation_budget(self):
        """Ambos algoritmos deben respetar estrictamente el mismo presupuesto de evaluaciones."""
        BUDGET = 1500

        # FWA
        prob_fwa = create_pfsp_instance(1, BUDGET)
        fwa = FireworksAlgorithm(prob_fwa, "FWAc")
        evals_fwa = prob_fwa.counter.getCount()

        # TS
        prob_ts = create_pfsp_instance(1, BUDGET)
        ts = TabuSearch(prob_ts, "TSc")
        evals_ts = prob_ts.counter.getCount()

        self.assertLessEqual(evals_fwa, BUDGET + 1,
            "FWA supero el presupuesto (%d > %d)" % (evals_fwa, BUDGET))
        self.assertLessEqual(evals_ts, BUDGET + 1,
            "TS supero el presupuesto (%d > %d)" % (evals_ts, BUDGET))

    # ------------------------------------------------------ Comparacion de Rendimiento
    def test_comparative_efficiency_and_speed(self):
        """
        Ejecuta FWA y TS bajo idéntico presupuesto (2500 evaluaciones), midiendo:
        - Makespan final (calidad)
        - Gap respecto al mejor valor conocido (BKS)
        - Tiempo de ejecucion (eficiencia computacional)
        """
        BUDGET = 2500

        # Ejecucion FWA
        prob_fwa = create_pfsp_instance(1, BUDGET)
        t0_fwa = time.perf_counter()
        fwa = FireworksAlgorithm(prob_fwa, "FWAc")
        time_fwa = time.perf_counter() - t0_fwa
        fit_fwa = fwa.status.stateFinal.fitness
        gap_fwa = 100.0 * (fit_fwa - TA001_BKS) / TA001_BKS

        # Ejecucion TS
        prob_ts = create_pfsp_instance(1, BUDGET)
        t0_ts = time.perf_counter()
        ts = TabuSearch(prob_ts, "TSc")
        time_ts = time.perf_counter() - t0_ts
        fit_ts = ts.status.stateFinal.fitness
        gap_ts = 100.0 * (fit_ts - TA001_BKS) / TA001_BKS

        # Verificaciones de integridad y calidad
        self.assertGreater(fit_fwa, 0)
        self.assertGreater(fit_ts, 0)
        self.assertLess(gap_fwa, 30.0, "Gap de FWA en ta001 demasiado elevado: %.2f%%" % gap_fwa)
        self.assertLess(gap_ts, 10.0, "Gap de TS en ta001 demasiado elevado: %.2f%%" % gap_ts)

        # Imprimir reporte comparativo estructurado
        print("\n" + "=" * 70)
        print("          TEST COMPARATIVO DE EFICIENCIA: FWA vs TABU SEARCH")
        print("=" * 70)
        print(" Instancia           : ta001 (20x5, BKS = %d)" % TA001_BKS)
        print(" Presupuesto (evals) : %d" % BUDGET)
        print("-" * 70)
        print(" %-20s | %-12s | %-12s | %-12s" % ("Metrica", "Fireworks (FWA)", "Tabu Search (TS)", "Diferencia"))
        print("-" * 70)
        print(" %-20s | %-12.1f | %-12.1f | %+.1f" % ("Makespan Final", fit_fwa, fit_ts, fit_fwa - fit_ts))
        print(" %-20s | %-11.2f%% | %-11.2f%% | %+.2f%%" % ("Gap vs BKS", gap_fwa, gap_ts, gap_fwa - gap_ts))
        print(" %-20s | %-12.4f | %-12.4f | %+.4f s" % ("Tiempo CPU (s)", time_fwa, time_ts, time_fwa - time_ts))
        print(" %-20s | %-12d | %-12d | %d" % ("Evals Consumidas", prob_fwa.counter.getCount(), prob_ts.counter.getCount(), prob_fwa.counter.getCount() - prob_ts.counter.getCount()))
        print(" %-20s | %-16s | %-16s | %-12s" % ("Paradigma", "Poblacional/Enjambre", "Trayectoria/Memoria", "-"))
        print(" %-20s | %-16s | %-16s | %-12s" % ("Arranque", "Aleatorio", "NEH Constructivo", "-"))
        print("=" * 70 + "\n")

    # ------------------------------------------------------ Comparacion Multi-corrida Estocastica
    def test_multi_run_consistency_comparison(self):
        """
        Compara la consistencia estadística de FWA en 5 corridas estocásticas
        frente al arranque determinista de TS.
        """
        BUDGET = 2000
        N_RUNS = 5

        fwa_results = []
        for seed in range(N_RUNS):
            np.random.seed(seed * 17 + 3)
            prob = create_pfsp_instance(1, BUDGET)
            fwa = FireworksAlgorithm(prob, "FWAc")
            fwa_results.append(fwa.status.stateFinal.fitness)

        # TS es determinista con NEH
        prob_ts = create_pfsp_instance(1, BUDGET)
        ts = TabuSearch(prob_ts, "TSc")
        ts_fit = ts.status.stateFinal.fitness

        mean_fwa = np.mean(fwa_results)
        std_fwa = np.std(fwa_results)
        best_fwa = np.min(fwa_results)

        self.assertGreater(len(fwa_results), 0)
        self.assertLess(best_fwa, fwa.status.stateInitial.fitness,
            "FWA debe mejorar la solucion inicial promedio")

        print("  -> FWA (5 corridas) :: Mejor = %.1f, Media = %.1f, Desv = %.2f" % (best_fwa, mean_fwa, std_fwa))
        print("  -> TS  (1 corrida)  :: Makespan = %.1f (NEH = %d)" % (ts_fit, ts.nehCost))


if __name__ == "__main__":
    unittest.main(verbosity=2)

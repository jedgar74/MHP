# Valida el lector de instancias del Max-Cut y el calculo del corte.
#
# El oraculo es la instancia juguete toy4.txt: un ciclo de 4 vertices con pesos
# 1, 4, 3, 2, calculado a mano. El grafo es bipartito, asi que el corte maximo
# toma las 4 aristas y vale 10.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_maxcut_reader.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.MaxCutProblem import MaxCutProblem
from state.Solution import Solution

INSTDIR = "./DATA/instances/MAXCUT"

# toy4: aristas (0,1)=1, (0,2)=4, (1,3)=3, (2,3)=2. Max cut = 10.
TOY_ADJ = np.array([
    [0, 1, 4, 0],
    [1, 0, 0, 3],
    [4, 0, 0, 2],
    [0, 3, 2, 0],
], dtype=int)
TOY_OPT = 10

# Las 20 instancias del banco principal.
INSTANCES = ["mc20_%d.txt" % k for k in range(1, 21)]


def evaluateAssignment(problem, signs):
    """Evalua una asignacion concreta (lista de +1/-1) y devuelve el corte."""
    s = Solution(problem, "RANDOM")
    s.setValues(np.array(signs, dtype=float))
    problem.evaluate(s)
    return s.fitness


def bruteForceOptimum(problem):
    """Corte maximo por enumeracion exhaustiva 2^n (solo para n pequeno)."""
    n = problem.nVar
    best = -1.0
    for mask in range(1 << n):
        signs = []
        for i in range(n):
            signs.append(1.0 if ((mask >> i) & 1) == 0 else -1.0)
        best = max(best, evaluateAssignment(problem, signs))
    return best


class TestMaxCutReader(unittest.TestCase):
    """Lector de adyacencia y evaluacion del corte."""

    def test_toy_reproduces_manual_calculation(self):
        """El oraculo: cortar los 4 vertices en {0,3} vs {1,2} da las 4 aristas."""

        p = MaxCutProblem("toy4.txt")
        self.assertEqual(p.nVar, 4)
        self.assertTrue(np.array_equal(p.adj, TOY_ADJ),
                "matriz de adyacencia mal leida")

        # Todas las aristas cruzan con S = {0, 3} (x = +1, -1, -1, +1)
        self.assertEqual(evaluateAssignment(p, [1, -1, -1, 1]), TOY_OPT)
        # Ninguna arista cruza si todos van al mismo lado
        self.assertEqual(evaluateAssignment(p, [1, 1, 1, 1]), 0)
        self.assertEqual(evaluateAssignment(p, [-1, -1, -1, -1]), 0)

    def test_toy_optimum_is_unique(self):
        """El maximo sobre las 16 asignaciones debe valer 10."""

        p = MaxCutProblem("toy4.txt")
        self.assertEqual(bruteForceOptimum(p), TOY_OPT)

    def test_dimensions_and_symmetry_of_all_instances(self):
        """Las 20 instancias: nVar=20, matriz simetrica y diagonal cero."""

        for name in INSTANCES:
            with self.subTest(instance=name):
                p = MaxCutProblem(name)
                self.assertEqual(p.nVar, 20)
                self.assertEqual(p.adj.shape, (20, 20))
                self.assertTrue(np.array_equal(p.adj, p.adj.T),
                        "%s: matriz no simetrica" % name)
                self.assertEqual(int(np.diag(p.adj).sum()), 0,
                        "%s: diagonal no nula" % name)

    def test_weights_are_positive_integers(self):
        """Los pesos generados estan en [1, 20] (o 0 donde no hay arista)."""

        for name in INSTANCES:
            with self.subTest(instance=name):
                p = MaxCutProblem(name)
                off = p.adj[np.triu_indices(20, k=1)]
                self.assertTrue(((off >= 0) & (off <= 20)).all(),
                        "%s: pesos fuera de [0, 20]" % name)

    def test_total_weight_matches_adjacency(self):
        """totalWeight debe ser la suma de los pesos con i < j."""

        p = MaxCutProblem("toy4.txt")
        expected = 1 + 4 + 3 + 2
        self.assertEqual(p.totalWeight, expected)

    def test_non_symmetric_instance_raises(self):
        """Una matriz no simetrica debe lanzar ValueError."""

        bad = os.path.join(INSTDIR, "_bad_sym_tmp.txt")
        with open(bad, "w") as fh:
            fh.write("3\n")
            fh.write("0 1 0\n")
            fh.write("0 0 1\n")   # (1,0) != 1 -> no simetrica
            fh.write("0 0 0\n")
        try:
            with self.assertRaises(ValueError):
                MaxCutProblem("_bad_sym_tmp.txt")
        finally:
            os.remove(bad)

    def test_inconsistent_dimensions_raise(self):
        """Declarar mas vertices que filas debe lanzar ValueError."""

        bad = os.path.join(INSTDIR, "_bad_dim_tmp.txt")
        with open(bad, "w") as fh:
            fh.write("5\n")
            fh.write("0 1 0\n")
            fh.write("1 0 0\n")
            fh.write("0 0 0\n")
        try:
            with self.assertRaises(ValueError):
                MaxCutProblem("_bad_dim_tmp.txt")
        finally:
            os.remove(bad)

    def test_instance_name_is_derived_from_file(self):
        p = MaxCutProblem("mc20_1.txt")
        self.assertEqual(p.instanceName, "mc20_1")

    def test_getcostmatrix_returns_adjacency(self):
        p = MaxCutProblem("toy4.txt")
        self.assertTrue(np.array_equal(p.getCostMatrix(), TOY_ADJ))

    def test_problem_metadata(self):
        p = MaxCutProblem("toy4.txt")
        self.assertEqual(p.nameShort, "MAXCUT")
        self.assertEqual(p.typeState, "BINARY")
        self.assertEqual(p.typeProblem, "MAX")
        self.assertIsNotNone(p.op, "selOpers() no asigno el operador binario")


if __name__ == "__main__":
    unittest.main(verbosity=2)

# Valida el lector de instancias QAPLIB y la funcion objetivo del QAP.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_qap_reader.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.QuadraticAssignmentProblem import QuadraticAssignmentProblem
from state.Solution import Solution

INSTANCE_DIR = os.path.join(
    os.path.dirname(__file__), "..", "DATA", "instances", "QAP")

# Permutaciones optimas publicadas en QAPLIB, en base 1 tal como aparecen alli.
# Son la unica forma de comprobar que la funcion objetivo esta bien: reproducen
# un valor que no depende de esta implementacion.
KNOWN_OPTIMA = {
    "nug12.dat": ([12, 7, 9, 3, 4, 8, 11, 1, 5, 6, 10, 2], 578),
    "had12.dat": ([3, 10, 11, 2, 12, 5, 6, 7, 8, 1, 4, 9], 1652),
    "had14.dat": ([8, 13, 10, 5, 12, 11, 2, 14, 3, 6, 7, 1, 9, 4], 2724),
}


def solutionFrom(problem, perm1):
    """Construye una Solution a partir de una permutacion en base 1."""
    s = Solution(problem, "RANDOM")
    s.vars = np.array([x - 1 for x in perm1], dtype=int)
    return s


class TestQAPReader(unittest.TestCase):
    """Lectura del formato QAPLIB."""

    def test_reads_dimension_and_two_square_matrices(self):
        p = QuadraticAssignmentProblem("had12.dat")
        self.assertEqual(p.nVar, 12)
        self.assertEqual(p.matA.shape, (12, 12))
        self.assertEqual(p.matB.shape, (12, 12))

    def test_reads_every_instance_in_the_directory(self):
        """El reparto por posicion debe funcionar en las 38 instancias.

        Se lee el fichero entero y se reparten los numeros por posicion, no
        linea a linea, porque en QAPLIB una fila se parte en varias lineas
        cuando n es grande y el numero de lineas en blanco entre bloques varia
        entre ficheros.
        """
        files = sorted(f for f in os.listdir(INSTANCE_DIR) if f.endswith(".dat"))
        self.assertEqual(len(files), 38)

        for f in files:
            p = QuadraticAssignmentProblem(f)
            self.assertGreater(p.nVar, 0, f)
            self.assertEqual(p.matA.shape, (p.nVar, p.nVar), f)
            self.assertEqual(p.matB.shape, (p.nVar, p.nVar), f)

    def test_matrices_are_not_swapped(self):
        """had12 tiene diagonal nula en flujos y distancias no nulas fuera."""
        p = QuadraticAssignmentProblem("had12.dat")
        self.assertEqual(np.trace(p.matA), 0.0)
        self.assertGreater(p.matB.sum(), 0.0)

    def test_missing_data_is_rejected(self):
        """Un fichero que declara mas de lo que trae debe fallar, no truncar."""
        path = os.path.join(INSTANCE_DIR, "_tmp_broken.dat")
        with open(path, "w") as fh:
            fh.write("5\n1 2 3\n")
        try:
            with self.assertRaises(ValueError):
                QuadraticAssignmentProblem("_tmp_broken.dat")
        finally:
            os.remove(path)


class TestQAPObjective(unittest.TestCase):
    """Funcion objetivo f(p) = SUM_i SUM_j A[i][j] * B[p[i]][p[j]]."""

    def test_reproduces_published_optima(self):
        """Si la formula estuviera mal, estos tres valores no saldrian."""
        for fich, (perm1, value) in KNOWN_OPTIMA.items():
            p = QuadraticAssignmentProblem(fich)
            s = solutionFrom(p, perm1)
            p.evaluate(s)
            self.assertAlmostEqual(s.fitness, value, places=6, msg=fich)

    def test_identity_permutation_matches_direct_sum(self):
        """La version vectorizada debe coincidir con el doble bucle."""
        p = QuadraticAssignmentProblem("nug12.dat")
        s = solutionFrom(p, list(range(1, 13)))
        p.evaluate(s)

        expected = 0.0
        idx = [int(x) for x in s.vars]
        for i in range(p.nVar):
            for j in range(p.nVar):
                expected = expected + p.matA[i][j] * p.matB[idx[i]][idx[j]]

        self.assertAlmostEqual(s.fitness, expected, places=6)

    def test_objective_agrees_with_double_loop_on_random_permutations(self):
        p = QuadraticAssignmentProblem("rou15.dat")
        np.random.seed(3)

        for _ in range(5):
            s = Solution(p, "RANDOM")
            p.evaluate(s)

            idx = [int(x) for x in s.vars]
            expected = 0.0
            for i in range(p.nVar):
                for j in range(p.nVar):
                    expected = expected + p.matA[i][j] * p.matB[idx[i]][idx[j]]

            self.assertAlmostEqual(s.fitness, expected, places=6)

    def test_evaluate_accepts_a_python_list(self):
        """crossoverAlternatingPosition devuelve vars como lista, no ndarray."""
        p = QuadraticAssignmentProblem("had12.dat")
        s = solutionFrom(p, KNOWN_OPTIMA["had12.dat"][0])
        s.vars = [int(x) for x in s.vars]
        p.evaluate(s)
        self.assertAlmostEqual(s.fitness, 1652, places=6)

    def test_problem_declares_permutational_minimisation(self):
        """Sin esto el Agent elegiria el juego de operadores equivocado."""
        p = QuadraticAssignmentProblem("had12.dat")
        self.assertEqual(p.typeState, "PERMUTATIONAL")
        self.assertEqual(p.typeProblem, "MIN")
        self.assertEqual(p.nameShort, "QAP")

    def test_cost_matrix_is_none_on_purpose(self):
        """El QAP no tiene matriz de costos: ACO no es linea base valida aqui.

        Ver el comentario de getCostMatrix(). Devolver matA daria a las
        metaheuristicas constructivas una visibilidad heuristica que no
        significa nada.
        """
        p = QuadraticAssignmentProblem("had12.dat")
        self.assertIsNone(p.getCostMatrix())


class TestQAPOptimums(unittest.TestCase):
    """Tabla de mejores valores conocidos."""

    def test_every_instance_has_a_recorded_optimum(self):
        opt = {}
        with open(os.path.join(INSTANCE_DIR, "opt", "optimums.txt")) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    k, v = line.split()
                    opt[k] = float(v)

        dats = {f[:-4] for f in os.listdir(INSTANCE_DIR) if f.endswith(".dat")}
        self.assertEqual(dats - set(opt), set())
        self.assertEqual(set(opt) - dats, set())

    def test_recorded_optimum_matches_published_permutation(self):
        """Cruza la tabla con las permutaciones optimas publicadas."""
        opt = {}
        with open(os.path.join(INSTANCE_DIR, "opt", "optimums.txt")) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    k, v = line.split()
                    opt[k] = float(v)

        for fich, (perm1, value) in KNOWN_OPTIMA.items():
            self.assertEqual(opt[fich[:-4]], value, fich)


if __name__ == "__main__":
    unittest.main()

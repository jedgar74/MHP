# Valida el lector de instancias Taillard del PFSP y el calculo del makespan.
#
# Se escribio ANTES que el lector (fase 3 del plan): el oraculo es la instancia
# 3x3 de la seccion 2.3 del documento de diseno, calculada a mano.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_pfsp_reader.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.PermutationFlowShopProblem import PermutationFlowShopProblem
from state.Solution import Solution

INSTDIR = "./DATA/instances/PFSP"

# Los seis ficheros descargados: nombre -> (n, m, numero de instancias).
FILES = {
    "tai20_5.txt":  (20,  5, 10),
    "tai20_10.txt": (20, 10, 10),
    "tai20_20.txt": (20, 20, 10),
    "tai50_5.txt":  (50,  5, 10),
    "tai50_10.txt": (50, 10, 10),
    "tai50_20.txt": (50, 20, 10),
}

# Instancia 3x3 del documento de diseno, seccion 2.3. Calculada a mano.
# Trabajos A=0, B=1, C=2.  p[trabajo][maquina]:
#     A = (5, 1, 1)   B = (1, 1, 5)   C = (2, 3, 2)
TOY_TIMES = {0: [5, 1, 1], 1: [1, 1, 5], 2: [2, 3, 2]}
TOY_CMAX = {
    (1, 2, 0): 10,   # (B, C, A)  <- optimo
    (1, 0, 2): 13,   # (B, A, C)
    (2, 1, 0): 13,   # (C, B, A)
    (0, 1, 2): 14,   # (A, B, C)
    (2, 0, 1): 14,   # (C, A, B)
    (0, 2, 1): 17,   # (A, C, B)
}


def evaluatePerm(problem, perm):
    """Evalua una permutacion concreta y devuelve su makespan."""

    s = Solution(problem, "RANDOM")
    s.setValues(np.array(perm, dtype=int))
    problem.evaluate(s)
    return int(round(s.fitness))


class TestPFSPReader(unittest.TestCase):
    """Lector Taillard: cabecera, orden maquina-mayor y seleccion de instancia."""

    def test_toy_instance_reproduces_manual_calculation(self):
        """El oraculo del proyecto: las 6 permutaciones de la instancia 3x3.

        Un error en el max{} de la recurrencia, o leer la matriz transpuesta,
        cambiaria al menos uno de estos seis numeros.
        """

        p = PermutationFlowShopProblem(["toy3x3.txt", 1])

        self.assertEqual(p.nVar, 3, "toy3x3: nVar deberia ser 3")
        self.assertEqual(p.nMachines, 3, "toy3x3: nMachines deberia ser 3")

        for job, times in TOY_TIMES.items():
            for k, t in enumerate(times):
                self.assertEqual(int(p.times[job][k]), t,
                        "toy3x3: p[%d][%d] mal leido (orden maquina-mayor?)" % (job, k))

        for perm, cmax in sorted(TOY_CMAX.items()):
            with self.subTest(perm=perm):
                self.assertEqual(evaluatePerm(p, perm), cmax,
                        "makespan de %s != %d calculado a mano" % (str(perm), cmax))

    def test_optimum_of_toy_is_unique(self):
        """(B, C, A) debe ser estrictamente mejor que las otras cinco."""

        p = PermutationFlowShopProblem(["toy3x3.txt", 1])
        values = dict((perm, evaluatePerm(p, perm)) for perm in TOY_CMAX)
        best = min(values.values())

        self.assertEqual(best, 10, "el optimo de toy3x3 deberia ser 10")
        self.assertEqual([k for k, v in values.items() if v == best], [(1, 2, 0)],
                "el optimo de toy3x3 deberia ser unico y valer (B, C, A)")

    def test_dimensions_match_header_in_every_instance(self):
        """Las 60 instancias: n y m leidos coinciden con los declarados."""

        for fname, (n, m, count) in sorted(FILES.items()):
            for idx in range(1, count + 1):
                with self.subTest(instance=fname, index=idx):
                    p = PermutationFlowShopProblem([fname, idx])
                    self.assertEqual(p.nVar, n)
                    self.assertEqual(p.nMachines, m)
                    self.assertEqual(p.times.shape, (n, m),
                            "%s[%d]: forma de la matriz != (n, m)" % (fname, idx))

    def test_each_file_holds_ten_instances(self):
        """Cada fichero de Taillard concatena 10 bloques (correccion 2.4b)."""

        for fname, (n, m, count) in sorted(FILES.items()):
            with self.subTest(instance=fname):
                p = PermutationFlowShopProblem([fname, 1])
                self.assertEqual(p.nInstances, count,
                        "%s deberia contener %d instancias" % (fname, count))

    def test_index_selects_a_different_instance(self):
        """El indice debe seleccionar de verdad, no devolver siempre la primera.

        SMTWTP tiene 'instancer = 1' fijo en el codigo; aqui es un parametro.
        """

        p1 = PermutationFlowShopProblem(["tai20_5.txt", 1])
        p2 = PermutationFlowShopProblem(["tai20_5.txt", 2])

        self.assertFalse(np.array_equal(p1.times, p2.times),
                "el indice 2 devolvio la misma matriz que el indice 1")
        self.assertNotEqual(p1.upperBound, p2.upperBound,
                "el indice 2 devolvio la misma cabecera que el indice 1")

    def test_processing_times_are_in_taillard_range(self):
        """Taillard genero los tiempos con distribucion uniforme en [1, 99]."""

        for fname in sorted(FILES):
            with self.subTest(instance=fname):
                p = PermutationFlowShopProblem([fname, 1])
                self.assertGreaterEqual(int(p.times.min()), 1)
                self.assertLessEqual(int(p.times.max()), 99)

    def test_bounds_are_read_from_header(self):
        """La cabecera de ta001 declara UB=1278 y LB=1232."""

        p = PermutationFlowShopProblem(["tai20_5.txt", 1])
        self.assertEqual(p.upperBound, 1278)
        self.assertEqual(p.lowerBound, 1232)
        self.assertLessEqual(p.lowerBound, p.upperBound)

    def test_index_out_of_range_raises(self):
        for idx in [0, 11, 99]:
            with self.subTest(index=idx):
                with self.assertRaises(ValueError):
                    PermutationFlowShopProblem(["tai20_5.txt", idx])

    def test_inconsistent_header_raises(self):
        """Una cabecera que promete mas maquinas de las que trae debe fallar."""

        bad = os.path.join(INSTDIR, "_bad_header_tmp.txt")
        with open(bad, "w") as fh:
            fh.write("number of jobs, number of machines, initial seed,"
                     " upper bound and lower bound :\n")
            fh.write("           3           5           0          10          10\n")
            fh.write("processing times :\n")
            fh.write(" 5 1 2\n 1 1 3\n 1 5 2\n")
        try:
            with self.assertRaises(ValueError):
                PermutationFlowShopProblem(["_bad_header_tmp.txt", 1])
        finally:
            os.remove(bad)

    def test_getcostmatrix_returns_none(self):
        """El PFSP no es un problema de grafo: ACO debe rechazarlo limpiamente."""

        p = PermutationFlowShopProblem(["toy3x3.txt", 1])
        self.assertIsNone(p.getCostMatrix())

    def test_problem_metadata(self):
        p = PermutationFlowShopProblem(["toy3x3.txt", 1])
        self.assertEqual(p.nameShort, "PFSP")
        self.assertEqual(p.typeState, "PERMUTATIONAL")
        self.assertEqual(p.typeProblem, "MIN")
        self.assertIsNotNone(p.op, "selOpers() no asigno el operador permutacional")


if __name__ == "__main__":
    unittest.main(verbosity=2)

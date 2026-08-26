# Valida la API de vecindarios anadida a OperatorsPerm (fase 4 del plan).
#
# Se escribio ANTES que la implementacion. La API no existia en el repositorio:
# OperatorsPerm solo ofrecia mutation('SWAPPING'), que devuelve UN vecino al
# azar. La Busqueda Tabu necesita enumerar el vecindario completo y elegir el
# mejor candidato no prohibido, de ahi este anadido.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_neighborhood.py
#     python -m unittest discover tests/
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.PermutationFlowShopProblem import PermutationFlowShopProblem
from state.Solution import Solution


def makeSolution(problem, perm=None):
    """Construye una Solution con una permutacion concreta (o la identidad)."""

    s = Solution(problem, "RANDOM")
    if perm is None:
        perm = list(range(problem.nVar))
    s.setValues(np.array(perm, dtype=int))
    return s


def applyInsertion(perm, origen, destino):
    """Aplica el movimiento de insercion a una lista y devuelve el resultado."""

    aux = list(perm)
    job = aux.pop(origen)
    aux.insert(destino, job)
    return aux


class TestNeighborhoodAPI(unittest.TestCase):
    """El generador de vecindarios: tamano, validez y coherencia del movimiento."""

    @classmethod
    def setUpClass(cls):
        cls.small = PermutationFlowShopProblem(["toy3x3.txt", 1])     # n = 3
        cls.big   = PermutationFlowShopProblem(["tai20_5.txt", 1])    # n = 20

    def test_insertion_neighborhood_has_exact_size(self):
        """El vecindario de insercion tiene (n-1)^2 vecinos DISTINTOS.

        n(n-1) pares (i,j) con i != j, menos los (n-1) movimientos adyacentes
        que estan contados dos veces: mover i a i+1 es lo mismo que mover
        i+1 a i.
        """

        for problem in [self.small, self.big]:
            n = problem.nVar
            with self.subTest(n=n):
                s = makeSolution(problem)
                neighs = problem.op.neighborhood('INSERTION', s)
                self.assertEqual(len(neighs), (n-1)**2,
                        "n=%d: se esperaban %d vecinos y llegaron %d"
                        % (n, (n-1)**2, len(neighs)))

    def test_swap_neighborhood_has_exact_size(self):
        """El vecindario de intercambio tiene n(n-1)/2 vecinos distintos."""

        for problem in [self.small, self.big]:
            n = problem.nVar
            with self.subTest(n=n):
                s = makeSolution(problem)
                neighs = problem.op.neighborhood('SWAP', s)
                self.assertEqual(len(neighs), n*(n-1)//2,
                        "n=%d: se esperaban %d vecinos y llegaron %d"
                        % (n, n*(n-1)//2, len(neighs)))

    def test_all_neighbours_are_valid_permutations(self):
        for name in ['INSERTION', 'SWAP']:
            for problem in [self.small, self.big]:
                n = problem.nVar
                with self.subTest(neighborhood=name, n=n):
                    s = makeSolution(problem)
                    for vecino, mov in problem.op.neighborhood(name, s):
                        vals = sorted(int(x) for x in vecino.vars)
                        self.assertEqual(vals, list(range(n)),
                                "%s n=%d: el vecino no es una permutacion valida"
                                % (name, n))

    def test_no_neighbour_equals_the_origin(self):
        for name in ['INSERTION', 'SWAP']:
            for problem in [self.small, self.big]:
                with self.subTest(neighborhood=name, n=problem.nVar):
                    s = makeSolution(problem)
                    origen = [int(x) for x in s.vars]
                    for vecino, mov in problem.op.neighborhood(name, s):
                        self.assertNotEqual([int(x) for x in vecino.vars], origen,
                                "%s: un vecino es identico a la solucion de origen" % name)

    def test_insertion_neighbours_are_all_distinct(self):
        """Si hubiera duplicados, TS evaluaria dos veces el mismo candidato."""

        for problem in [self.small, self.big]:
            with self.subTest(n=problem.nVar):
                s = makeSolution(problem)
                neighs = problem.op.neighborhood('INSERTION', s)
                firmas = set(tuple(int(x) for x in v.vars) for v, mov in neighs)
                self.assertEqual(len(firmas), len(neighs),
                        "hay vecinos duplicados en el vecindario de insercion")

    def test_move_is_consistent_with_the_neighbour(self):
        """El movimiento devuelto debe reproducir exactamente el vecino.

        Sin esta garantia la lista tabu de TS prohibiria atributos que no se
        corresponden con el candidato aceptado.
        """

        problem = self.big
        s = makeSolution(problem)
        origen = [int(x) for x in s.vars]

        for vecino, mov in problem.op.neighborhood('INSERTION', s):
            job, desde, hasta = mov
            self.assertEqual(origen[desde], job,
                    "el movimiento dice que se mueve el trabajo %s pero en la"
                    " posicion %d hay %s" % (job, desde, origen[desde]))
            self.assertEqual([int(x) for x in vecino.vars],
                    applyInsertion(origen, desde, hasta),
                    "aplicar el movimiento no reproduce el vecino")

    def test_origin_solution_is_not_mutated(self):
        """Generar el vecindario no debe tocar la solucion de partida."""

        problem = self.big
        s = makeSolution(problem)
        antes = [int(x) for x in s.vars]
        problem.op.neighborhood('INSERTION', s)
        self.assertEqual([int(x) for x in s.vars], antes,
                "el generador de vecindarios modifico la solucion de origen")

    def test_sampling_with_factor_limits_the_size(self):
        """FACTORNEIGHS: con factor k se muestrean k*n vecinos, no (n-1)^2."""

        problem = self.big
        n = problem.nVar
        s = makeSolution(problem)

        for factor in [1, 2, 4]:
            with self.subTest(factor=factor):
                neighs = problem.op.neighborhood('INSERTION', s, factor)
                self.assertEqual(len(neighs), factor*n,
                        "factor=%d: se esperaban %d vecinos" % (factor, factor*n))
                for vecino, mov in neighs:
                    vals = sorted(int(x) for x in vecino.vars)
                    self.assertEqual(vals, list(range(n)),
                            "el muestreo produjo una permutacion invalida")

    def test_factor_larger_than_neighborhood_falls_back_to_all(self):
        """Si k*n supera el vecindario completo, se devuelve el completo."""

        problem = self.small          # n = 3, vecindario completo = 4
        s = makeSolution(problem)
        neighs = problem.op.neighborhood('INSERTION', s, 100)
        self.assertEqual(len(neighs), (problem.nVar-1)**2)

    def test_unknown_neighborhood_raises(self):
        problem = self.small
        s = makeSolution(problem)
        with self.assertRaises(ValueError):
            problem.op.neighborhood('NOEXISTE', s)

    def test_existing_mutation_still_works(self):
        """Regresion: el operador que ya usaban SA y GA no debe verse afectado."""

        problem = self.big
        s = makeSolution(problem)
        mutado = problem.op.mutation('SWAPPING', [s])
        vals = sorted(int(x) for x in mutado.vars)
        self.assertEqual(vals, list(range(problem.nVar)))


if __name__ == "__main__":
    unittest.main(verbosity=2)

# Valida el lector TSPLIB + evaluate() contra los tours optimos oficiales.
#
# Ejecutar DESDE LA RAIZ del repositorio:
#     python -m unittest tests/test_tsp_reader.py
#     python -m unittest discover tests/
#     python tests/test_tsp_reader.py
import sys, os
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from examples.TravelingSalesmanProblem import TravelingSalesmanProblem
from state.Solution import Solution

# Directorio de tours optimos. Se puede reapuntar con la variable de entorno
# TSP_OPT_DIR; no se usa sys.argv porque bajo unittest lo consume el runner.
OPTDIR = os.environ.get("TSP_OPT_DIR", "./DATA/instances/TSP/opt")

# Las 8 instancias que tienen .opt.tour disponible.
OPTIMA = {
    "eil51": 426, "berlin52": 7542, "st70": 675, "eil76": 538,
    "pr76": 108159, "kroA100": 21282, "ch130": 6110, "lin105": 14379,
}


def readOptTour(path):
    """Lee un fichero .opt.tour de TSPLIB y devuelve la permutacion 0-based."""

    tour = []
    inSec = False
    with open(path) as fh:
        lines = fh.readlines()
    for line in lines:
        s = line.strip()
        if not s:
            continue
        u = s.upper()
        if u.startswith("TOUR_SECTION"):
            inSec = True
            continue
        if u.startswith("EOF") or u == "-1":
            break
        if inSec:
            for t in s.split():
                v = int(t)
                if v == -1:
                    inSec = False
                    break
                tour.append(v - 1)   # TSPLIB es 1-based
    return tour


class TestTSPLIBReader(unittest.TestCase):
    """El lector TSPLIB, el redondeo nint y el cierre del ciclo en evaluate().

    Evaluar el tour optimo oficial y exigir el costo publicado valida las tres
    cosas a la vez: cualquier error de una sola unidad en el redondeo, o un
    ciclo que no cierre, haria fallar las 8 instancias.
    """

    def test_optimal_tours_reproduce_published_optimum(self):
        for name, opt in sorted(OPTIMA.items()):
            with self.subTest(instance=name):
                p = TravelingSalesmanProblem(name + ".tsp")
                tour = readOptTour(os.path.join(OPTDIR, name + ".opt.tour"))

                self.assertEqual(len(tour), p.nVar,
                        "%s: longitud del tour != nVar" % name)
                self.assertEqual(sorted(tour), list(range(p.nVar)),
                        "%s: el tour optimo no es una permutacion" % name)

                s = Solution(p, "RANDOM")
                s.setValues(np.array(tour, dtype=int))
                p.evaluate(s)

                self.assertEqual(int(round(s.fitness)), opt,
                        "%s: costo calculado != optimo publicado" % name)

    def test_distance_matrix_is_symmetric_integer_and_hollow(self):
        for name in sorted(OPTIMA):
            with self.subTest(instance=name):
                p = TravelingSalesmanProblem(name + ".tsp")
                self.assertTrue(np.array_equal(p.matA, p.matA.T),
                        "%s: matriz no simetrica" % name)
                self.assertTrue(np.all(np.diag(p.matA) == 0),
                        "%s: diagonal no nula" % name)
                self.assertTrue(np.all(p.matA == np.floor(p.matA)),
                        "%s: distancias no enteras (nint mal aplicado)" % name)

    def test_flat_matrix_format_still_works(self):
        """Retrocompatibilidad: ven.txt es una matriz plana sin cabecera."""

        pv = TravelingSalesmanProblem("ven.txt")
        self.assertEqual(pv.nVar, 6, "ven.txt deberia tener 6 ciudades")
        self.assertEqual(pv.matA[0][1], 264.0, "ven.txt mal leido")
        self.assertEqual(pv.matA[2][4], 537.0, "ven.txt mal leido")


if __name__ == "__main__":
    unittest.main(verbosity=2)

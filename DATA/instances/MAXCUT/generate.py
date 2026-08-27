# coding=UTF-8
"""
Genera las instancias del Maximum Cut (Max-Cut) que usa la extension.

Cada instancia es un grafo no dirigido ponderado y se guarda en un fichero de
texto con el formato:

    <n>
    <n filas de n enteros, matriz de adyacencia simetrica, diagonal 0>

Los pesos son enteros en [1, 20]. El valor de referencia (optimo) se calcula
por enumeracion exhaustiva 2^(n-1) --fijando un vertice por simetria--, asi que
es EXACTO y no un "mejor valor conocido". Se vuelca a opt/optimums.txt con la
forma "<instancia> <optimo>".

Ademas se escribe la instancia juguete toy4.txt, cuyo optimo (10) esta calculado
a mano: un ciclo de 4 vertices con pesos 1, 4, 3, 2; el grafo es bipartito, asi
que el corte maximo toma las 4 aristas.

Uso (desde la raiz del repositorio):

    python DATA/instances/MAXCUT/generate.py

Es reproducible: las semillas estan fijadas. No se necesita ejecutar en el
experimento; los ficheros .txt y opt/optimums.txt ya quedan generados.
"""

import os
import numpy as np

INSTDIR = os.path.join("DATA", "instances", "MAXCUT")

# (nombre, n, densidad p, semilla)
SPECS = [
    ("mc20_1",  20, 0.5,  1),
    ("mc20_2",  20, 0.5,  2),
    ("mc20_3",  20, 0.5,  3),
    ("mc20_4",  20, 0.2,  4),
    ("mc20_5",  20, 0.2,  5),
    ("mc20_6",  20, 0.5,  6),
    ("mc20_7",  20, 0.5,  7),
    ("mc20_8",  20, 0.2,  8),
    ("mc20_9",  20, 0.2,  9),
    ("mc20_10", 20, 0.5, 10),
    ("mc20_11", 20, 0.5, 11),
    ("mc20_12", 20, 0.2, 12),
    ("mc20_13", 20, 0.5, 13),
    ("mc20_14", 20, 0.2, 14),
    ("mc20_15", 20, 0.5, 15),
    ("mc20_16", 20, 0.2, 16),
    ("mc20_17", 20, 0.5, 17),
    ("mc20_18", 20, 0.2, 18),
    ("mc20_19", 20, 0.5, 19),
    ("mc20_20", 20, 0.2, 20),
]


def randomGraph(n, p, seed):
    """Matriz de adyacencia simetrica, diagonal 0, pesos enteros [1, 20]."""
    rng = np.random.default_rng(seed)
    W = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                w = int(rng.integers(1, 21))
                W[i][j] = w
                W[j][i] = w
    return W


def maxcutBruteForce(W):
    """Optimo exacto por enumeracion 2^(n-1). cut = 0.5*(total - 0.5*x^T W x)."""
    n = W.shape[0]
    total = float(W.sum()) / 2.0
    best = -1.0
    half = 1 << (n - 1)
    for mask in range(half):
        x = np.ones(n, dtype=float)
        for i in range(1, n):
            if (mask >> (i - 1)) & 1:
                x[i] = -1.0
        quad = float(x @ W @ x)
        cut = 0.5 * (total - 0.5 * quad)
        if cut > best:
            best = cut
    return int(round(best))


def writeInstance(name, W):
    n = W.shape[0]
    lines = [str(n)]
    for i in range(n):
        lines.append(" ".join(str(int(W[i][j])) for j in range(n)))
    with open(os.path.join(INSTDIR, name + ".txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")


def writeToy():
    """Ciclo de 4 vertices (bipartito). Max cut = 10, calculado a mano."""
    W = np.zeros((4, 4), dtype=int)
    edges = [(0, 1, 1), (0, 2, 4), (1, 3, 3), (2, 3, 2)]
    for i, j, w in edges:
        W[i][j] = w
        W[j][i] = w
    writeInstance("toy4", W)
    return 10


def main():
    os.makedirs(INSTDIR, exist_ok=True)
    os.makedirs(os.path.join(INSTDIR, "opt"), exist_ok=True)

    optimums = []

    toyOpt = writeToy()
    optimums.append(("toy4", toyOpt))
    print("toy4  ->  %s" % toyOpt)

    for name, n, p, seed in SPECS:
        W = randomGraph(n, p, seed)
        writeInstance(name, W)
        opt = maxcutBruteForce(W)
        optimums.append((name, opt))
        print("%s  ->  %s" % (name, opt))

    with open(os.path.join(INSTDIR, "opt", "optimums.txt"), "w") as fh:
        for name, opt in optimums:
            fh.write("%s %s\n" % (name, opt))

    print("\nEscritos %d ficheros en %s y opt/optimums.txt" % (len(optimums), INSTDIR))


if __name__ == "__main__":
    main()

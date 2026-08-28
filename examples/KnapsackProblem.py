# coding=UTF-8
"""
0/1 Knapsack Problem para MHP.

La plataforma representa las variables binarias como {-1, +1}. En esta clase:
    +1 -> el objeto se selecciona
    -1 -> el objeto no se selecciona

El objetivo es maximizar el valor total sin superar la capacidad de la mochila.
Las soluciones inviables reciben fitness negativo igual al exceso de peso. De
esta forma cualquier solucion viable (fitness >= 0) domina a una inviable y no
se necesita modificar/reparar silenciosamente la solucion durante evaluate().
"""

from problem.Problem import *
import numpy as np
import os


class KnapsackProblem(Problem):

    def __init__(self, namInst=None, verbose=False):
        super().__init__()
        self.nameShort = "KP"
        self.typeState = "BINARY"
        self.typeProblem = "MAX"
        self.verbose = verbose

        self.capacity = 0
        self.values = None
        self.weights = None
        self.instanceName = None

        self.selOpers()

        if namInst is not None:
            self.readInstance(namInst)

    def readInstance(self, namFile):
        """
        Formato de instancia (se permiten comentarios iniciados con #):

            n capacity
            value_1 weight_1
            value_2 weight_2
            ...
            value_n weight_n
        """
        path = os.path.join('./DATA/instances/KNAPSACK', namFile)
        with open(path, 'r', encoding='utf-8') as fh:
            lines = []
            for raw in fh:
                line = raw.split('#', 1)[0].strip()
                if line:
                    lines.append(line)

        if not lines:
            raise ValueError("Instancia vacia: " + namFile)

        header = lines[0].split()
        if len(header) != 2:
            raise ValueError("Cabecera invalida en " + namFile + ": se espera 'n capacity'")

        n = int(header[0])
        capacity = int(header[1])
        if n <= 0 or capacity <= 0:
            raise ValueError("n y capacity deben ser positivos en " + namFile)

        if len(lines) - 1 != n:
            raise ValueError("La instancia " + namFile + " declara " + str(n)
                             + " objetos y contiene " + str(len(lines) - 1))

        values = []
        weights = []
        for idx, line in enumerate(lines[1:], start=1):
            parts = line.split()
            if len(parts) != 2:
                raise ValueError("Fila " + str(idx) + " invalida en " + namFile)
            value, weight = int(parts[0]), int(parts[1])
            if value < 0 or weight <= 0:
                raise ValueError("Valor/peso invalido en fila " + str(idx)
                                 + " de " + namFile)
            values.append(value)
            weights.append(weight)

        self.nVar = n
        self.capacity = capacity
        self.values = np.asarray(values, dtype=int)
        self.weights = np.asarray(weights, dtype=int)
        self.instanceName = os.path.splitext(os.path.basename(namFile))[0]

        if self.verbose:
            print("Knapsack", self.instanceName, "n=", self.nVar,
                  "capacity=", self.capacity)

    def selectedMask(self, solution):
        """Mascara booleana de objetos seleccionados (+1)."""
        if len(solution.vars) != self.nVar:
            raise ValueError("La solucion no tiene el numero esperado de variables")
        return np.asarray(solution.vars) > 0

    def solutionTotals(self, solution):
        """Devuelve (valor_total, peso_total)."""
        mask = self.selectedMask(solution)
        total_value = int(self.values[mask].sum())
        total_weight = int(self.weights[mask].sum())
        return total_value, total_weight

    def isFeasible(self, solution):
        return self.solutionTotals(solution)[1] <= self.capacity

    def evaluate(self, s):
        total_value, total_weight = self.solutionTotals(s)
        if total_weight <= self.capacity:
            fitness = float(total_value)
        else:
            # Toda solucion inviable queda por debajo de cualquier viable.
            fitness = -float(total_weight - self.capacity)
        s.setFitness(fitness)

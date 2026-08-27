from problem.Problem import *

import numpy as np


class QuadraticAssignmentProblem (Problem):

	"""Problema de Asignacion Cuadratica (QAP)."""

	def __init__(self, namInst=None, verbose=False):
		super().__init__()
		self.nameShort = "QAP"
		self.typeState = "PERMUTATIONAL"
		self.typeProblem = "MIN"
		self.verbose = verbose
		self.flow = None
		self.distance = None
		self.selOpers()
		if namInst is not None:
			self.readInstance(namInst)

	def readInstance(self, namFile):
		"""Lee ``n``, una matriz de flujo y una matriz de distancia."""
		with open('./DATA/instances/QAP/' + namFile, 'r') as fileobj:
			lines = [line.strip() for line in fileobj if line.strip()]

		if not lines or not lines[0].isdigit():
			raise ValueError("La instancia QAP debe comenzar con el tamano n")
		n = int(lines[0])
		if len(lines) != 1 + 2 * n + 2:
			raise ValueError("Formato QAP invalido: se esperaban dos matrices")
		if lines[1].lower() != 'flow' or lines[n + 2].lower() != 'distance':
			raise ValueError("La instancia QAP debe contener flow y distance")

		self.flow = self._readMatrix(lines[2:2 + n], n, "flow")
		self.distance = self._readMatrix(lines[n + 3:n + 3 + n], n, "distance")
		self.nVar = n
		self.matA = self.distance
		if self.verbose:
			print(self.flow)
			print(self.distance)

	def _readMatrix(self, rows, n, name):
		matrix = []
		for row in rows:
			values = [int(value) for value in row.split()]
			if len(values) != n:
				raise ValueError("Fila invalida en matriz " + name)
			matrix.append(values)
		return np.asarray(matrix, dtype=float)

	def getCostMatrix(self):
		return None

	def evaluate(self, s):
		idx = np.asarray(s.vars, dtype=int)
		if len(idx) != self.nVar or sorted(idx.tolist()) != list(range(self.nVar)):
			raise ValueError("La solucion QAP debe ser una permutacion de 0..n-1")
		value = 0.0
		for i in range(self.nVar):
			for j in range(self.nVar):
				value += self.flow[i][j] * self.distance[idx[i]][idx[j]]
		s.setFitness(value)
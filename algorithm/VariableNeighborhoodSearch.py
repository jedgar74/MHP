# coding=UTF-8
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *
import numpy as np
import copy

class VariableNeighborhoodSearch(Heuristic):
	"""
	Variable Neighborhood Search (VNS - Mladenovic & Hansen).
	
	Metaheuristica de trayectoria que combina fases de perturbacion (Shaking)
	para escapar de minimos locales con busqueda local descendente (VND / Local Search)
	a traves de multiples estructuras de vecindarios (SWAP, INSERTION).

	:author: Maria
	"""

	def __init__(self, problem, fileConfig, run=True):
		super().__init__()
		self.shortTerm  = "VNS"
		self.objProblem = problem

		self.setParameters(fileConfig)

		# Inicializacion
		self.status.stateInitial = Solution(self.objProblem, self.parameters.get('initialTypeSolution'))
		if self.status.stateInitial.fitness is None:
			self.objProblem.evaluate(self.status.stateInitial)
			self.objProblem.counter.incCount()

		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)

		if run:
			self.variableNeighborhoodSearch()

	def run(self, solution=None):
		if solution is None:
			self.variableNeighborhoodSearch()
		else:
			self.variableNeighborhoodSearch(solution)

	def setParameters(self, fileConfig):
		"""
		Lee el JSON de configuracion y aplica valores por defecto en caso de ausencia.
		"""
		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		if 'kmax' not in self.parameters:
			self.parameters.update(dict(kmax=3))

		if 'neighborhoods' not in self.parameters:
			self.parameters.update(dict(neighborhoods=["SWAP", "INSERTION"]))

		if 'initialTypeSolution' not in self.parameters:
			self.parameters.update(dict(initialTypeSolution="RANDOM"))

		if 'localSearchType' not in self.parameters:
			self.parameters.update(dict(localSearchType="FIRST_IMPROVEMENT"))

		if 'factorNeighs' not in self.parameters:
			self.parameters.update(dict(factorNeighs=2))

	def shake(self, solution, k):
		"""
		Fase de perturbacion (Shaking): aplica k mutaciones consecutivas
		para alejar la solucion del optimo local actual.
		"""
		shaken = copy.deepcopy(solution)
		for _ in range(k):
			shaken = self.objProblem.op.mutation('SWAPPING', [shaken])
		return shaken

	def localSearch(self, solution):
		"""
		Busqueda local usando la lista de vecindarios configurados.
		"""
		current = copy.deepcopy(solution)
		neigh_names = self.parameters.get('neighborhoods')
		factor = self.parameters.get('factorNeighs')
		mode = self.parameters.get('localSearchType')

		improved = True
		while improved and self.isStopCriteria():
			improved = False
			for name in neigh_names:
				if not self.isStopCriteria():
					break
				
				neighbors = self.objProblem.op.neighborhood(name, current, factor)
				for cand, _ in neighbors:
					if not self.isStopCriteria():
						break

					self.objProblem.evaluate(cand)
					self.objProblem.counter.incCount()

					if self.objProblem.op.isBetter([cand, current]):
						current = cand
						improved = True
						if mode == "FIRST_IMPROVEMENT":
							break
				if improved:
					break

		return current

	def variableNeighborhoodSearch(self, solution=None):
		"""
		Bucle principal de VNS.
		"""
		if solution is None:
			current = copy.deepcopy(self.status.stateFinal)
		else:
			current = copy.deepcopy(solution)

		kmax = int(self.parameters.get('kmax'))

		while self.isStopCriteria():
			k = 1
			while k <= kmax and self.isStopCriteria():
				# 1. Shaking
				x_prime = self.shake(current, k)
				self.objProblem.evaluate(x_prime)
				self.objProblem.counter.incCount()

				# 2. Local Search
				x_second = self.localSearch(x_prime)

				# 3. Decision de movimiento
				if self.objProblem.op.isBetter([x_second, current]):
					current = copy.deepcopy(x_second)
					k = 1  # Reiniciar vecindario
					if self.objProblem.op.isBetter([current, self.status.stateFinal]):
						self.status.stateFinal = copy.deepcopy(current)
				else:
					k += 1  # Siguiente estructura de vecindario

	def replaceSolution(self, solution):
		self.status.stateFinal = copy.deepcopy(solution)
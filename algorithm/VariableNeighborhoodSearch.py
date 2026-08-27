from algorithm.Heuristic import *
from state.Solution import *

import copy
import numpy as np


class VariableNeighborhoodSearch (Heuristic):

	"""Busqueda de Vecindario Variable (VNS) para permutaciones."""

	def __init__(self, problem, fileConfig, run=True):
		super().__init__()
		self.shortTerm = "VNS"
		self.objProblem = problem
		self.setParameters(fileConfig)
		self.status.stateInitial = Solution(self.objProblem,
			self.parameters.get('initialTypeSolution'))
		self.objProblem.evaluate(self.status.stateInitial)
		self.objProblem.counter.incCount()
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)
		self.startCost = self.status.stateInitial.fitness
		if run:
			self.variableNeighborhoodSearch()

	def setParameters(self, fileConfig):
		self.parameters = self.readParameters(fileConfig, self.shortTerm)
		defaults = {'neighborhoods': ['SWAP', 'INSERTION'],
			'initialTypeSolution': 'RANDOM', 'maxNeighbors': None}
		for key, value in defaults.items():
			if key not in self.parameters:
				self.parameters[key] = value

	def makeNeighbor(self, solution, kind, first, second):
		candidate = copy.deepcopy(solution)
		values = list(candidate.vars)
		if kind == 'SWAP':
			values[first], values[second] = values[second], values[first]
		elif kind == 'INSERTION':
			value = values.pop(first)
			values.insert(second, value)
		else:
			raise ValueError("Vecindario VNS no definido: " + str(kind))
		candidate.setValues(np.asarray(values, dtype=int))
		return candidate

	def neighborhood(self, solution, kind):
		neighbors = []
		n = solution.nVar
		for first in range(n):
			for second in range(n):
				if first == second:
					continue
				if kind == 'SWAP' and first > second:
					continue
				neighbors.append(self.makeNeighbor(solution, kind, first, second))
				limit = self.parameters.get('maxNeighbors')
				if limit is not None and len(neighbors) >= int(limit):
					return neighbors
		return neighbors

	def variableNeighborhoodSearch(self, solution=None):
		current = copy.deepcopy(solution if solution is not None else self.status.stateFinal)
		k = 0
		neighborhoods = self.parameters.get('neighborhoods')
		while self.isStopCriteria():
			if k >= len(neighborhoods):
				break
			best = None
			for candidate in self.neighborhood(current, neighborhoods[k]):
				if not self.isStopCriteria():
					break
				self.objProblem.evaluate(candidate)
				self.objProblem.counter.incCount()
				if best is None or self.objProblem.op.isBetter([candidate, best]):
					best = candidate
			if best is None:
				break
			if self.objProblem.op.isBetter([best, current]):
				current = best
				if self.objProblem.op.isBetter([current, self.status.stateFinal]):
					self.status.stateFinal = copy.deepcopy(current)
				k = 0
			else:
				k += 1

	def run(self, solution=None):
		self.variableNeighborhoodSearch(solution)

	def replaceSolution(self, solution):
		self.status.stateFinal = copy.deepcopy(solution)
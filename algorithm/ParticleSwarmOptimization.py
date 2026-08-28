# coding=UTF-8
from algorithm.Heuristic import Heuristic
from state.Population import Population

import copy
import numpy as np


class ParticleSwarmOptimization(Heuristic):
	"""Particle Swarm Optimization (PSO) para problemas continuos."""

	def __init__(self, problem, fileConfig, run=True):
		super().__init__()
		self.shortTerm = "PSO"
		self.objProblem = problem
		self.setParameters(fileConfig)
		self._validateProblem()

		budget = self.objProblem.counter.getLimit()
		if budget < 1:
			raise ValueError("PSO requiere un presupuesto de al menos una evaluacion")

		self.swarmSize = min(self.parameters["particles"], budget)
		self.popul = Population(
			self.swarmSize,
			self.objProblem,
			self.parameters["initialTypeSolution"],
		)
		self.objProblem.counter.incCount(self.swarmSize)

		span = np.asarray(self.objProblem.upperlimits, dtype=float) - np.asarray(
			self.objProblem.lowerlimits, dtype=float
		)
		self.maxVelocity = self.parameters["vmaxRatio"] * span
		self.velocities = np.random.uniform(
			-self.maxVelocity, self.maxVelocity, (self.swarmSize, self.objProblem.nVar)
		)

		self.personalBest = [copy.deepcopy(s) for s in self.popul.popul]
		self.globalBest = copy.deepcopy(self._best(self.personalBest))
		self.status.stateInitial = copy.deepcopy(self.globalBest)
		self.status.stateFinal = copy.deepcopy(self.globalBest)

		if run:
			self.run()

	def setParameters(self, fileConfig):
		self.parameters = self.readParameters(fileConfig, self.shortTerm)
		defaults = {
			"particles": 30,
			"inertia": 0.7298,
			"cognitive": 1.49618,
			"social": 1.49618,
			"vmaxRatio": 0.2,
			"initialTypeSolution": "RANDOM",
		}
		for name, value in defaults.items():
			self.parameters.setdefault(name, value)

		self.parameters["particles"] = int(self.parameters["particles"])
		for name in ["inertia", "cognitive", "social", "vmaxRatio"]:
			self.parameters[name] = float(self.parameters[name])

		if self.parameters["particles"] < 1:
			raise ValueError("particles debe ser mayor que cero")
		if self.parameters["inertia"] < 0:
			raise ValueError("inertia no puede ser negativa")
		if self.parameters["cognitive"] < 0 or self.parameters["social"] < 0:
			raise ValueError("cognitive y social no pueden ser negativos")
		if self.parameters["vmaxRatio"] <= 0:
			raise ValueError("vmaxRatio debe ser mayor que cero")

	def _validateProblem(self):
		if self.objProblem.typeState != "REAL":
			raise ValueError("PSO requiere un problema con variables de tipo REAL")
		if self.objProblem.nVar < 1:
			raise ValueError("PSO requiere al menos una variable")
		if self.objProblem.lowerlimits is None or self.objProblem.upperlimits is None:
			raise ValueError("PSO requiere limites inferiores y superiores")
		if len(self.objProblem.lowerlimits) != self.objProblem.nVar or len(
			self.objProblem.upperlimits
		) != self.objProblem.nVar:
			raise ValueError("Los limites del problema deben tener nVar elementos")

	def _isBetter(self, candidate, incumbent):
		if self.objProblem.typeProblem == "MIN":
			return candidate.fitness < incumbent.fitness
		return candidate.fitness > incumbent.fitness

	def _best(self, solutions):
		best = solutions[0]
		for solution in solutions[1:]:
			if self._isBetter(solution, best):
				best = solution
		return best

	def run(self, sol=None):
		if sol is not None and self._isBetter(sol, self.personalBest[0]):
			self.popul.popul[0] = copy.deepcopy(sol)
			self.personalBest[0] = copy.deepcopy(sol)
			if self._isBetter(sol, self.globalBest):
				self.globalBest = copy.deepcopy(sol)

		lower = np.asarray(self.objProblem.lowerlimits, dtype=float)
		upper = np.asarray(self.objProblem.upperlimits, dtype=float)
		limit = self.objProblem.counter.getLimit()

		while self.objProblem.counter.getCount() < limit:
			for index, particle in enumerate(self.popul.popul):
				if self.objProblem.counter.getCount() >= limit:
					break

				r1 = np.random.random(self.objProblem.nVar)
				r2 = np.random.random(self.objProblem.nVar)
				velocity = (
					self.parameters["inertia"] * self.velocities[index]
					+ self.parameters["cognitive"]
					* r1
					* (self.personalBest[index].vars - particle.vars)
					+ self.parameters["social"]
					* r2
					* (self.globalBest.vars - particle.vars)
				)
				velocity = np.clip(velocity, -self.maxVelocity, self.maxVelocity)
				position = particle.vars + velocity

				outside = (position < lower) | (position > upper)
				position = np.clip(position, lower, upper)
				velocity[outside] = 0.0

				particle.setValues(position)
				self.velocities[index] = velocity
				self.objProblem.evaluate(particle)
				self.objProblem.counter.incCount()

				if self._isBetter(particle, self.personalBest[index]):
					self.personalBest[index] = copy.deepcopy(particle)
					if self._isBetter(particle, self.globalBest):
						self.globalBest = copy.deepcopy(particle)

		self.status.stateFinal = copy.deepcopy(self.globalBest)
		return self.status.stateFinal

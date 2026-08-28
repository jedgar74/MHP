from problem.Problem import Problem

import json
import math
import os


class Rastrigin(Problem):
	"""Funcion benchmark de Rastrigin para optimizacion continua."""

	def __init__(self, namInst=None):
		super().__init__()
		self.nameShort = "Rastrigin"
		self.typeState = "REAL"
		self.selOpers()

		if namInst is not None:
			self.readInstance(namInst)

	def readInstance(self, namFile):
		path = os.path.join(".", "DATA", "instances", "Rastrigin", namFile)
		with open(path, encoding="utf-8") as file:
			data = json.load(file)

		self.nVar = int(data["N"])
		self.A = float(data.get("A", 10.0))

		lower = data.get("lowerlimits", -5.12)
		upper = data.get("upperlimits", 5.12)
		self.lowerlimits = self._expandLimits(lower, "lowerlimits")
		self.upperlimits = self._expandLimits(upper, "upperlimits")

		if any(lo >= hi for lo, hi in zip(self.lowerlimits, self.upperlimits)):
			raise ValueError("Cada limite inferior debe ser menor que el superior")

	def _expandLimits(self, value, name):
		if isinstance(value, (int, float)):
			return [float(value)] * self.nVar
		if len(value) != self.nVar:
			raise ValueError("%s debe tener N elementos" % name)
		return [float(item) for item in value]

	def evaluate(self, solution):
		if len(solution.vars) != self.nVar:
			raise ValueError("La solucion debe tener %d variables" % self.nVar)

		fitness = self.A * self.nVar
		for value in solution.vars:
			fitness += value ** 2 - self.A * math.cos(2.0 * math.pi * value)
		solution.setFitness(float(fitness))
		return float(fitness)

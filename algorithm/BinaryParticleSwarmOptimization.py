# coding=UTF-8
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *

import numpy as np
import copy


class BinaryParticleSwarmOptimization(Heuristic):

	"""
	Binary Particle Swarm Optimization (BPSO). Version binaria de la PSO
	clasica, debida a Kennedy y Eberhart (1997) sobre la PSO de 1995.

	Metaheuristica poblacional de enjambre. La PSO clasica actualiza una
	velocidad real y desplaza una posicion real; BPSO actualiza la misma
	velocidad real pero la posicion es binaria, y el paso se decide con una
	sigmoide de la velocidad: se fija a 1 si U(0,1) < sigmoid(v), si
	no 0.

	MHP codifica lo binario como {-1, +1}. BPSO mapea temporalmente a
	{0, 1} SOLO para la ecuacion de velocidad, y guarda en Solution.vars
	exclusivamente {-1, +1}.

	:version:
	:author:
	"""

	def __init__(self, problem, fileConfig, run=True):
		"""
		@param problem.Problem problem :
		@param String fileConfig :
		@param boolean run :
		@return  :
		@author
		"""
		super().__init__()

		self.shortTerm   = "BPSO"
		self.objProblem = problem

		self.setParameters(fileConfig)

		self.swarm      = []
		self.velocities = None
		self.pbest      = []
		self.gbest     = None

		# ---- Inicializacion -------------------------------------------
		# Se crean tan solo 'budget' particulas cuando el presupuesto no
		# alcanza para configuracion: asi la inicializacion nunca excede el
		# cupo (ver la politica en binaryParticleSwarmOptimization).
		cap  = int(self.objProblem.counter.getLimit())
		part = min(int(self.parameters.get('particles')), max(cap, 0))

		self.velocities = np.random.uniform(-float(self.parameters.get('vmax')),
		                                   float(self.parameters.get('vmax')),
		                                   (part, self.objProblem.nVar))

		for i in range(part):
			particle = Solution(self.objProblem, self.parameters.get('initialTypeSolution'))
			self.objProblem.evaluate(particle)
			self.objProblem.counter.incCount()
			self.swarm.append(copy.deepcopy(particle))
			self.pbest.append(copy.deepcopy(particle))

		self.status.stateInitial = copy.deepcopy(self.pbest[0]) if part > 0 else None

		if part > 0:
			self.gbest = copy.deepcopy(self.pbest[0])
			for i in range(1, part):
				if self.objProblem.op.isBetter([self.pbest[i], self.gbest]):
					self.gbest = copy.deepcopy(self.pbest[i])

		self.status.stateFinal = copy.deepcopy(self.gbest)

		if run == True and part > 0:
			self.binaryParticleSwarmOptimization()


	def run(self, solution=None):
		"""
		Executa el BPSO desde la mejor posicion conocida.

		@param state.Solution solution :
		@return  :
		@author
		"""
		if solution != None:
			self.swarm = [copy.deepcopy(solution)]
			self.pbest = [copy.deepcopy(solution)]
			self.velocities = np.zeros((1, self.objProblem.nVar))
			self.gbest = copy.deepcopy(solution)
			self.status.stateFinal = copy.deepcopy(solution)

		if len(self.swarm) > 0:
			self.binaryParticleSwarmOptimization()


	def setParameters(self, fileConfig):
		"""
		Lee el JSON de configuracion y rellena los valores ausentes, de modo
		que una configuracion incompleta no rompa la ejecucion. Los valores por
		defecto son la calibracion clasica de Clerc (restriccion).
		'initialTypeSolution = RANDOM' es el unico arranque coherente: BPSO
		no tiene una nocion de solucion determinista de partida.

		@param String fileConfig :
		@return  :
		@author
		"""

		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		if not 'particles' in self.parameters:
			self.parameters.update(dict(particles=30))

		if not 'w' in self.parameters:
			self.parameters.update(dict(w=0.729))

		if not 'c1' in self.parameters:
			self.parameters.update(dict(c1=1.49445))

		if not 'c2' in self.parameters:
			self.parameters.update(dict(c2=1.49445))

		if not 'vmax' in self.parameters:
			self.parameters.update(dict(vmax=6.0))

		if not 'initialTypeSolution' in self.parameters:
			self.parameters.update(dict(initialTypeSolution="RANDOM"))

		if int(self.parameters.get('particles')) <= 0:
			raise ValueError("particles debe ser positivo (BPSO)")
		if float(self.parameters.get('vmax')) <= 0:
			raise ValueError("vmax debe ser positivo (BPSO)")
		if float(self.parameters.get('c1')) < 0:
			raise ValueError("c1 debe ser no negativo (BPSO)")
		if float(self.parameters.get('c2')) < 0:
			raise ValueError("c2 debe ser no negativo (BPSO)")


	def hasBudget(self):
		"""
		Guarda exacta de presupuesto. Heuristic.isStopCriteria compara con <=,
		asi que sin esta guarda BPSO podria consumir una evaluacion de mas
		cuando count == limit.

		@return boolean :
		@author
		"""

		return self.objProblem.counter.getCount() < self.objProblem.counter.getLimit()


	def sigmoid(self, v):
		"""
		Sigmoide logistica, estable para el rango recortado por vmax.

		@param float v :
		@return float :
		@author
		"""

		return 1.0 / (1.0 + np.exp(-v))


	def binaryParticleSwarmOptimization(self):
		"""
		Bucle principal del BPSO.

		La condicion del while es hasBudget() y NO self.isStopCriteria() del
		framework. isStopCriteria compara con <=, de modo que con count == limit
		el bucle pasaria y hasBudget() (que pide count < limit) cortaria el
		for interno sin avanzar: bucle infinito. Con hasBudget() en ambos
		lugares, el gasto se corta SIEMPRE en count == limit, nunca en el
		presupuesto+1 del contrato generico.

		Esto difiere de GA/DE/HS (que usan isStopCriteria y toleran el
		excedente de 1): el enunciado pide que BPSO adopte la politica
		estricta de TabuSearch.

		@return  :
		@author
		"""

		problem = self.objProblem
		op      = problem.op

		# La condicion es estricta (count < limit), no <= (isStopCriteria).
		# Ver el docstring: con <= y la guarda hasBudget() interna el bucle
		# se colgaria en count == limit.
		while self.hasBudget():

			for i in range(len(self.swarm)):
				particle = self.swarm[i]

				x = (np.asarray(particle.vars, dtype=int) + 1) // 2
				p = (np.asarray(self.pbest[i].vars, dtype=int) + 1) // 2
				g = (np.asarray(self.gbest.vars, dtype=int) + 1) // 2

				r1 = np.random.rand(self.objProblem.nVar)
				r2 = np.random.rand(self.objProblem.nVar)

				self.velocities[i] = (self.parameters.get('w') * self.velocities[i]
					+ self.parameters.get('c1') * r1 * (p - x)
					+ self.parameters.get('c2') * r2 * (g - x))

				self.velocities[i] = np.clip(
					self.velocities[i],
					-float(self.parameters.get('vmax')),
					 float(self.parameters.get('vmax')))

				s = self.sigmoid(self.velocities[i])
				new  = np.where(np.random.rand(self.objProblem.nVar) < s, 1, 0)
				particle.setValues(2.0 * new - 1.0)

				if not self.hasBudget():
					break

				problem.evaluate(particle)
				problem.counter.incCount()

				if op.isBetter([particle, self.pbest[i]]):
					self.pbest[i] = copy.deepcopy(particle)

					if op.isBetter([self.pbest[i], self.gbest]):
						self.gbest = copy.deepcopy(self.pbest[i])

			self.status.stateFinal = copy.deepcopy(self.gbest)


	def replaceSolution(self, solution):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		self.gbest = copy.deepcopy(solution)
		self.status.stateFinal = copy.deepcopy(solution)

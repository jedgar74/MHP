# coding=UTF-8
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *

import numpy as np
import math
import copy


class AntColonyOptimization (Heuristic):

	"""
	Ant System / Elitist Ant System para problemas modelados sobre una matriz
	de costos (TSP, QAP, ...). A diferencia del resto de metaheuristicas de la
	plataforma, ACO es constructiva y necesita acceder a dicha matriz mediante
	Problem.getCostMatrix().

	:version:
	:author:
	"""

	""" ATTRIBUTES
	shortTerm  (public)
	ants  (implementation)
	alpha  (implementation)
	beta  (implementation)
	rho  (implementation)
	q  (implementation)
	elitist  (implementation)
	initialSolution  (implementation)
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

		self.shortTerm  = "ACO"
		self.objProblem = problem

		self.setParameters(fileConfig)

		# ---- Matriz de costos. ACO no es aplicable sin ella --------------
		D = self.objProblem.getCostMatrix()
		if D is None :
			raise ValueError("ACO requiere un problema que exponga una matriz de costos (getCostMatrix).")

		self.D = np.asarray(D, dtype=float)
		nVar = self.objProblem.nVar

		if self.D.shape != (nVar, nVar) :
			raise ValueError("La matriz de costos debe ser "+str(nVar)+"x"+str(nVar)
					+", recibida "+str(self.D.shape))

		# ---- Visibilidad heuristica eta = 1/(d + eps) --------------------
		# eps cubre tanto la diagonal (d_ii = 0) como pares de ciudades con
		# coordenadas duplicadas. La diagonal se anula para prohibir el lazo.
		eps = 1e-10
		self.eta = 1.0 / (self.D + eps)
		np.fill_diagonal(self.eta, 0.0)
		self.etaBeta = self.eta ** self.parameters.get('beta')

		# ---- Solucion inicial (convencion del framework) ------------------
		self.status.stateInitial = Solution(self.objProblem, self.parameters.get('initialTypeSolution'))
		self.objProblem.evaluate(self.status.stateInitial)
		self.objProblem.counter.incCount()
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)

		# ---- Feromona inicial tau0 = m / Lnn -----------------------------
		# Lnn se obtiene de un tour por vecino mas cercano. Se evalua como
		# cualquier otra solucion candidata, por lo que se contabiliza.
		nnSol = self.nearestNeighbourTour()
		self.objProblem.evaluate(nnSol)
		self.objProblem.counter.incCount()

		if self.objProblem.op.isBetter([nnSol, self.status.stateFinal]) :
			self.status.stateFinal = copy.deepcopy(nnSol)

		lnn = nnSol.fitness
		# Se conserva el costo del tour NN: es el punto de partida efectivo de
		# ACO y permite separar el merito de la colonia del merito del arranque
		# constructivo. Varia entre corridas porque nearestNeighbourTour parte
		# de una ciudad aleatoria.
		self.lnnCost = lnn
		if lnn <= 0 :
			lnn = 1.0
		tau0 = float(self.parameters.get('ants')) / lnn
		self.tau = np.full((nVar, nVar), tau0)

		if run == True :
			self.antColonyOptimization()


	def run(self, solution=None):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		if solution is not None :
			self.replaceSolution(solution)
		self.antColonyOptimization()


	def setParameters(self, fileConfig):
		"""
		@param String fileConfig :
		@return  :
		@author
		"""

		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		for i in range(7):

			if not 'ants' in self.parameters :
				self.parameters.update(dict(ants=25))

			if not 'alpha' in self.parameters :
				self.parameters.update(dict(alpha=1.0))

			if not 'beta' in self.parameters :
				self.parameters.update(dict(beta=3.0))

			if not 'rho' in self.parameters :
				self.parameters.update(dict(rho=0.5))

			if not 'q' in self.parameters :
				self.parameters.update(dict(q=100.0))

			if not 'elitist' in self.parameters :
				self.parameters.update(dict(elitist=True))

			if not 'initialTypeSolution' in self.parameters :
				self.parameters.update(dict(initialTypeSolution="RANDOM"))


	def antColonyOptimization(self, solution=None):
		"""
		Bucle principal del Ant System.

		@param state.Solution solution :
		@return  :
		@author
		"""

		if solution is not None :
			self.replaceSolution(solution)

		ants  = int(self.parameters.get('ants'))
		alpha = float(self.parameters.get('alpha'))
		rho   = float(self.parameters.get('rho'))

		while self.isStopCriteria():

			tauAlpha = self.tau ** alpha
			tours = []

			# El criterio de parada se comprueba DENTRO del lote de hormigas.
			# De lo contrario ACO consumiria hasta ants-1 evaluaciones extra y
			# la comparacion contra GA/SA dejaria de ser justa.
			for k in range(ants):
				if not self.isStopCriteria():
					break

				sol = self.buildTour(tauAlpha)
				self.objProblem.evaluate(sol)
				self.objProblem.counter.incCount()
				tours.append(sol)

				if self.objProblem.op.isBetter([sol, self.status.stateFinal]):
					self.status.stateFinal = copy.deepcopy(sol)

			if len(tours) == 0 :
				break

			self.updatePheromone(tours, rho)


	def buildTour(self, tauAlpha):
		"""
		Construye un tour completo eligiendo la siguiente ciudad con
		probabilidad proporcional a [tau_ij]^alpha * [eta_ij]^beta sobre las
		ciudades no visitadas.

		@param numpy.ndarray tauAlpha : matriz de feromona elevada a alpha
		@return state.Solution :
		@author
		"""

		nVar = self.objProblem.nVar
		visited = np.zeros(nVar, dtype=bool)
		tour = np.zeros(nVar, dtype=int)

		current = np.random.randint(nVar)
		tour[0] = current
		visited[current] = True

		for k in range(1, nVar):
			w = tauAlpha[current] * self.etaBeta[current]
			w = np.where(visited, 0.0, w)

			total = w.sum()
			if (not np.isfinite(total)) or (total <= 0.0):
				# Degeneracion numerica: se elige uniformemente entre las
				# ciudades pendientes para no romper la permutacion.
				pending = np.where(~visited)[0]
				nxt = int(pending[np.random.randint(len(pending))])
			else:
				r = np.random.rand() * total
				# side='right' impide seleccionar una ciudad con peso 0
				nxt = int(np.searchsorted(np.cumsum(w), r, side='right'))
				if (nxt >= nVar) or visited[nxt]:
					pending = np.where(~visited)[0]
					nxt = int(pending[np.random.randint(len(pending))])

			tour[k] = nxt
			visited[nxt] = True
			current = nxt

		sol = Solution(self.objProblem, self.parameters.get('initialTypeSolution'))
		sol.setValues(tour)

		return sol


	def updatePheromone(self, tours, rho):
		"""
		Evaporacion y deposito. Si el parametro elitist esta activo se anade el
		refuerzo del mejor global con peso e = numero de hormigas (Elitist Ant
		System de Dorigo).

		@param list tours : soluciones construidas en la iteracion
		@param float rho : tasa de evaporacion
		@return  :
		@author
		"""

		q = float(self.parameters.get('q'))

		self.tau = (1.0 - rho) * self.tau

		for sol in tours:
			length = sol.fitness
			if (length is None) or (length <= 0):
				continue
			self.depositTour(sol, q / length)

		if self.parameters.get('elitist') == True :
			best = self.status.stateFinal
			if (best is not None) and (best.fitness is not None) and (best.fitness > 0):
				e = float(self.parameters.get('ants'))
				self.depositTour(best, e * q / best.fitness)

		# Cota inferior: evita que un arco quede con feromona exactamente 0 y
		# se vuelva inalcanzable de forma permanente.
		self.tau = np.maximum(self.tau, 1e-12)


	def depositTour(self, sol, amount):
		"""
		Deposita 'amount' sobre todos los arcos del ciclo cerrado de sol.

		@param state.Solution sol :
		@param float amount :
		@return  :
		@author
		"""

		idx = np.asarray(sol.vars, dtype=int)
		nxt = np.roll(idx, -1)
		self.tau[idx, nxt] = self.tau[idx, nxt] + amount
		self.tau[nxt, idx] = self.tau[nxt, idx] + amount


	def nearestNeighbourTour(self):
		"""
		Tour por vecino mas cercano desde una ciudad aleatoria. Se usa para
		estimar Lnn y con ello tau0 = m / Lnn.

		@return state.Solution :
		@author
		"""

		nVar = self.objProblem.nVar
		visited = np.zeros(nVar, dtype=bool)
		tour = np.zeros(nVar, dtype=int)

		current = np.random.randint(nVar)
		tour[0] = current
		visited[current] = True

		for k in range(1, nVar):
			d = np.where(visited, np.inf, self.D[current])
			nxt = int(np.argmin(d))
			tour[k] = nxt
			visited[nxt] = True
			current = nxt

		sol = Solution(self.objProblem, self.parameters.get('initialTypeSolution'))
		sol.setValues(tour)

		return sol


	def replaceSolution(self, solution):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		self.status.stateFinal = copy.deepcopy(solution)

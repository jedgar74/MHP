
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *

import numpy as np
import copy


class Grasp (Heuristic):

	"""
	Greedy Randomized Adaptive Search Procedure (GRASP) para Max-Cut.

	GRASP (Feo y Resende, 1989) es una metaheuristica constructiva de
	multi-arranque. Cada iteracion consta de dos fases:

	  1. Construccion voraz aleatorizada. Los vertices se asignan a un lado del
	     corte de uno en uno. Para cada vertice sin asignar se calcula la
	     ganancia de ponerlo en cada lado (el peso de las aristas que cruzarian
	     hacia los ya asignados) y se toma la mejor. Una lista restringida de
	     candidatos (RCL) reune a los vertices cuya mejor ganancia esta dentro
	     de una fraccion 'alpha' de la mejor; de ahi se elige uno al azar. Con
	     alpha = 0 la construccion es puramente voraz; con alpha = 1 puramente
	     aleatoria.

	  2. Busqueda local. Desde la solucion construida se aplica un vecindario
	     1-flip (invertir el signo de un vertice), con mejora primero (FIRST) o
	     mejor (BEST), hasta un optimo local.

	El proceso se repite hasta agotar el presupuesto de evaluaciones y se
	devuelve la mejor solucion global. La fase constructiva expone su costo en
	'graspStartCost', espejo de TS.nehCost y ACO.lnnCost, de modo que Agent lo
	recolecta en startCosts y el reporte separa el merito de la busqueda del de
	la construccion.

	Contrasta con las metaheuristicas ya presentes: GA es poblacional, SA y RW
	son trayectoriales estocasticos y TS es de memoria explicita; GRASP aporta
	el paradigma constructivo de multi-arranque.

	:version:
	:author:
	"""

	""" ATTRIBUTES
	alpha  (implementation)         fraccion de la RCL (0 voraz, 1 aleatorio)
	localSearch  (implementation)   FIRST o BEST
	graspStartCost  (implementation) costo de la primera solucion constructiva
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

		self.shortTerm  = "GRASP"
		self.objProblem = problem

		self.setParameters(fileConfig)

		self.graspStartCost = None

		# Arranque constructivo: la primera solucion de la RCL. Se evalua y se
		# conserva su costo para el reporte (espejo de TS.nehCost).
		self.status.stateInitial = self.construct()
		self.objProblem.evaluate(self.status.stateInitial)
		self.objProblem.counter.incCount()
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)
		self.graspStartCost = self.status.stateInitial.fitness

		if run == True:
			self.grasp()


	def run(self, solution=None):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""
		if solution == None:
			self.grasp()
		else:
			self.grasp(solution)


	def replaceSolution(self, solution):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""
		self.status.stateFinal = copy.deepcopy(solution)


	def setParameters(self, fileConfig):
		"""
		Lee el JSON de configuracion y rellena los valores ausentes para que
		una configuracion incompleta no rompa la ejecucion.

		@param String fileConfig :
		@return  :
		@author
		"""

		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		if not 'alpha' in self.parameters:
			self.parameters.update(dict(alpha=0.3))

		if not 'localSearch' in self.parameters:
			self.parameters.update(dict(localSearch="BEST"))


	# ------------------------------------------------------------ construccion

	def construct(self):
		"""
		Construccion voraz aleatorizada (RCL). Asigna los n vertices a un lado
		del corte de uno en uno, eligiendo en cada paso un vertice de la lista
		restringida de candidatos y poniendolo en el lado que mas aristas
		cruce con los ya asignados.

		La ganancia no se computa llamando a evaluate(): es una contribucion
		marginal O(n) por vertice. Por eso la construccion no consume
		evaluaciones; la solucion completa se evalua una sola vez al terminar.

		@return state.Solution : solucion binaria (+1/-1) sin evaluar
		@author
		"""

		problem = self.objProblem
		alpha   = self.parameters.get('alpha')
		n       = problem.nVar

		x = np.zeros(n, dtype=float)   # 0 = sin asignar, +/-1 = lado del corte
		assigned = []

		for _step in range(n):

			candidates = [i for i in range(n) if x[i] == 0]
			if len(candidates) == 0:
				break

			gainPlus  = {}
			gainMinus = {}
			gainBest  = {}

			for v in candidates:
				gp = 0.0
				gm = 0.0
				for u in assigned:
					w = problem.adj[v][u]
					if w != 0:
						if x[u] > 0:
							gm += w
						else:
							gp += w
				gainPlus[v]  = gp
				gainMinus[v] = gm
				gainBest[v]  = gp if gp >= gm else gm

			gmax = max(gainBest.values())
			gmin = min(gainBest.values())
			threshold = gmax - alpha * (gmax - gmin)

			rcl = [v for v in candidates if gainBest[v] >= threshold - 1e-12]

			v = int(np.random.choice(rcl))

			# Se asigna al lado con mayor ganancia; el empate se rompe hacia +1
			x[v] = 1.0 if gainPlus[v] >= gainMinus[v] else -1.0
			assigned.append(v)

		s = Solution(problem, "RANDOM")
		s.setValues(x.copy())
		return s


	# ----------------------------------------------------------- busqueda local

	def localSearch(self, current):
		"""
		Vecindario 1-flip con mejora FIRST o BEST, hasta un optimo local.

		Cada flip evaluado incrementa el contador del framework. Se comprueba
		isStopCriteria() antes de cada evaluacion para no pasarse del
		presupuesto.

		@param state.Solution current :
		@return state.Solution :
		@author
		"""

		problem = self.objProblem
		op      = problem.op
		mode    = self.parameters.get('localSearch')
		n       = problem.nVar

		current = copy.deepcopy(current)
		improved = True

		while improved and self.isStopCriteria():

			improved = False
			bestNeighbor = None

			for i in range(n):

				if not self.isStopCriteria():
					break

				neighbor = copy.deepcopy(current)
				neighbor.vars[i] = neighbor.vars[i] * -1.0
				problem.evaluate(neighbor)
				problem.counter.incCount()

				if mode == "FIRST":
					if op.isBetter([neighbor, current]):
						current = neighbor
						improved = True
						break
				else:  # BEST
					if (bestNeighbor == None) or op.isBetter([neighbor, bestNeighbor]):
						bestNeighbor = neighbor

			if mode == "BEST" and bestNeighbor != None:
				if op.isBetter([bestNeighbor, current]):
					current = bestNeighbor
					improved = True

		return current


	# ----------------------------------------------------------- multi-arranque

	def grasp(self, solution=None):
		"""
		Bucle principal: busqueda local sobre el arranque constructivo y luego
		multi-arranque (construir + buscar) hasta agotar el presupuesto.

		@param state.Solution solution :
		@return  :
		@author
		"""

		problem = self.objProblem
		op      = problem.op

		if solution == None:
			best = copy.deepcopy(self.status.stateFinal)
		else:
			best = copy.deepcopy(solution)
			if best.fitness == None:
				problem.evaluate(best)
				problem.counter.incCount()

		# Busqueda local sobre el arranque constructivo
		best = self.localSearch(best)
		if op.isBetter([best, self.status.stateFinal]):
			self.status.stateFinal = copy.deepcopy(best)

		# Multi-arranque
		while self.isStopCriteria():
			s = self.construct()
			problem.evaluate(s)
			problem.counter.incCount()
			s = self.localSearch(s)
			if op.isBetter([s, best]):
				best = copy.deepcopy(s)

		self.status.stateFinal = copy.deepcopy(best)

from algorithm.Heuristic import *
from algorithm.HillClimbing import *
from problem.Problem import *
from state.Solution import *

import numpy as np
import copy


class IteratedLocalSearch (Heuristic):

	"""
	Busqueda Local Iterada (Lourenco, Martin y Stuetzle), siglas ILS.

	Metaheuristica de trayectoria construida sobre una busqueda local. El
	esquema son cuatro piezas y el merito esta en la tercera:

		s  = solucionInicial()
		s* = busquedaLocal(s)
		repetir:
			s' = perturbacion(s*)      <- salto que la busqueda local no puede deshacer
			s'' = busquedaLocal(s')
			s* = aceptacion(s*, s'')

	La idea central es que un optimo local no es un punto del que haya que
	huir al azar, sino un buen sitio desde el que volver a empezar. La
	perturbacion tiene que ser lo bastante grande como para que la busqueda
	local no regrese al mismo optimo, y lo bastante pequena como para no
	equivaler a un reinicio aleatorio, que tiraria a la basura todo lo
	aprendido. Ese equilibrio es el parametro que de verdad importa aqui.

	Contraste con lo que ya hay en la plataforma, en las dos dimensiones que
	estructuran el campo:

	  - SA  es de trayectoria y sin memoria: escapa del optimo local aceptando
	        empeoramientos con probabilidad decreciente.
	  - TS  es de trayectoria y con memoria explicita: escapa aceptando el
	        mejor vecino no prohibido, aunque sea peor.
	  - ILS es de trayectoria y con memoria implicita en el punto de reinicio:
	        no acepta empeoramientos nunca, escapa saltando y volviendo a
	        descender desde el mejor punto conocido.
	  - GA  es poblacional: escapa recombinando individuos distintos.

	Los ficheros DATA/config/ILS/ILSFa.cfg y ILSFb.cfg, que ya estaban en el
	repositorio sin implementacion que los leyera, fijan la nomenclatura de los
	parametros que se respeta aqui.

	:version:
	:author: Jordano Pernia
	"""

	""" ATTRIBUTES
	localSearch  (implementation)     objeto HillClimbing que hace la explotacion
	perturbation  (implementation)    BLOCKING o SWAPPING
	nonImprovingLimit  (implementation)  evaluaciones sin mejora antes de reiniciar
	nRestarts  (implementation)       reinicios efectuados, para el informe
	nAccepted  (implementation)       perturbaciones aceptadas, para el informe
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

		self.shortTerm  = "ILS"
		self.objProblem = problem

		self.setParameters(fileConfig)

		# La busqueda local se instancia con run=False: ILS decide cuando y
		# desde donde se ejecuta. Es el mismo patron con el que Agent.init2()
		# construye una metaheuristica sin lanzarla.
		self.localSearch = HillClimbing(self.objProblem,
				self.parameters.get('configLocalSearch'), False)

		self.nRestarts = 0
		self.nAccepted = 0

		self.status.stateInitial = Solution(self.objProblem, "RANDOM")

		if self.status.stateInitial.fitness == None:
			self.objProblem.evaluate(self.status.stateInitial)
			self.objProblem.counter.incCount()

		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)

		if run == True:
			self.iteratedLocalSearch()


	def run(self, solution=None):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		if solution == None:
			self.iteratedLocalSearch()
		else:
			self.iteratedLocalSearch(solution)


	def setParameters(self, fileConfig):
		"""
		Lee el JSON de configuracion y rellena los valores ausentes, de modo
		que una configuracion incompleta no rompa la ejecucion.

		@param String fileConfig :
		@return  :
		@author
		"""

		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		# Corresponde a INCLUDEMETHODS / CONFIGMETHODS de los .cfg originales
		if not 'localSearch' in self.parameters:
			self.parameters.update(dict(localSearch="HC"))

		if not 'configLocalSearch' in self.parameters:
			self.parameters.update(dict(configLocalSearch="HCc"))

		# PERTURBATION de los .cfg originales
		if not 'perturbation' in self.parameters:
			self.parameters.update(dict(perturbation="BLOCKING"))

		# Cuantos intercambios encadena la perturbacion SWAPPING. Con 1 la
		# busqueda local casi siempre deshace el salto y ILS se queda quieto.
		if not 'perturbationStrength' in self.parameters:
			self.parameters.update(dict(perturbationStrength=3))

		# NICCONSTANT de los .cfg originales: evaluaciones consumidas sin
		# mejorar el mejor global antes de reiniciar desde una solucion nueva.
		if not 'nonImprovingLimit' in self.parameters:
			self.parameters.update(dict(nonImprovingLimit=2000))

		# BETTER acepta solo si mejora; RW acepta siempre (paseo aleatorio
		# sobre optimos locales). BETTER es el criterio clasico.
		if not 'acceptance' in self.parameters:
			self.parameters.update(dict(acceptance="BETTER"))

		if not 'initialTypeSolution' in self.parameters:
			self.parameters.update(dict(initialTypeSolution="RANDOM"))


	# ---------------------------------------------------------- perturbacion

	def perturb(self, sol):
		"""
		Aplica el salto que la busqueda local no debe poder deshacer en un
		solo paso.

		@param state.Solution sol :
		@return state.Solution :
		@author
		"""

		name = self.parameters.get('perturbation')

		if name == "SWAPPING":
			return self.perturbSwapping(sol)
		elif name == "BLOCKING":
			return self.perturbBlocking(sol)
		else:
			raise ValueError("This perturbation method is not defined: "+name)


	def perturbSwapping(self, sol):
		"""
		Encadena k intercambios aleatorios, con k = perturbationStrength.

		Se reutiliza mutationSwapping de OperatorsPerm en vez de reimplementar
		el intercambio, que es el operador que ya usan SA y GA.

		@param state.Solution sol :
		@return state.Solution :
		@author
		"""

		u = copy.deepcopy(sol)
		k = int(self.parameters.get('perturbationStrength'))

		for i in range(k):
			u = self.objProblem.op.mutation('SWAPPING', [u])

		u.fitness = None
		return u


	def perturbBlocking(self, sol):
		"""
		Movimiento de bloques, conocido como double bridge: se corta la
		permutacion en cuatro trozos A B C D por tres puntos al azar y se
		reensambla como A C B D.

		Es la perturbacion clasica de ILS sobre permutaciones porque cambia
		cuatro adyacencias de golpe, y ni el vecindario de intercambio ni el de
		insercion pueden deshacerla en un solo movimiento: la busqueda local se
		ve obligada a descender hacia otro optimo local. Una perturbacion de un
		solo intercambio no tendria esa propiedad.

		@param state.Solution sol :
		@return state.Solution :
		@author
		"""

		u = copy.deepcopy(sol)
		n = sol.nVar

		base = [int(x) for x in sol.vars]

		# Con menos de cuatro posiciones no hay cuatro bloques que reordenar
		if n < 4:
			return self.perturbSwapping(sol)

		# Tres puntos de corte distintos y ordenados, cada bloque no vacio
		cuts = np.random.choice(range(1, n), 3, replace=False)
		cuts = sorted([int(c) for c in cuts])
		p1, p2, p3 = cuts[0], cuts[1], cuts[2]

		a = base[0:p1]
		b = base[p1:p2]
		c = base[p2:p3]
		d = base[p3:n]

		u.vars = np.array(a + c + b + d, dtype=int)
		u.fitness = None

		return u


	# --------------------------------------------------------------- bucle

	def iteratedLocalSearch(self, solution=None):
		"""
		Bucle principal.

		@param state.Solution solution :
		@return  :
		@author
		"""

		problem = self.objProblem
		op = problem.op

		if solution == None:
			current = copy.deepcopy(self.status.stateFinal)
		else:
			current = copy.deepcopy(solution)

		acceptance = self.parameters.get('acceptance')
		limit = int(self.parameters.get('nonImprovingLimit'))

		self.nRestarts = 0
		self.nAccepted = 0

		# Primer descenso: ILS no itera sobre la solucion aleatoria sino sobre
		# el optimo local al que esta conduce.
		current = self.localSearch.hillClimbing(current)

		if op.isBetter([current, self.status.stateFinal]):
			self.status.stateFinal = copy.deepcopy(current)

		# Se cuentan evaluaciones y no iteraciones porque el coste de una
		# iteracion de ILS es variable: depende de cuantos pasos de descenso
		# necesite la busqueda local, que no se sabe de antemano.
		lastImprovement = problem.counter.getCount()

		while self.isStopCriteria():

			candidate = self.perturb(current)
			candidate = self.localSearch.hillClimbing(candidate)

			if op.isBetter([candidate, self.status.stateFinal]):
				self.status.stateFinal = copy.deepcopy(candidate)
				lastImprovement = problem.counter.getCount()

			# Criterio de aceptacion: decide desde donde se perturbara la
			# proxima vez. Es lo que separa ILS de un multiarranque, que
			# volveria siempre a un punto aleatorio.
			if acceptance == "RW":
				current = candidate
				self.nAccepted = self.nAccepted + 1
			elif op.isBetter([candidate, current]):
				current = candidate
				self.nAccepted = self.nAccepted + 1

			# Reinicio: si el mejor global lleva demasiadas evaluaciones sin
			# moverse, la trayectoria esta atrapada en una cuenca de la que la
			# perturbacion no basta para salir.
			if (problem.counter.getCount() - lastImprovement) >= limit:

				if not self.isStopCriteria():
					break

				current = Solution(problem, "RANDOM")
				problem.evaluate(current)
				problem.counter.incCount()
				current = self.localSearch.hillClimbing(current)

				if op.isBetter([current, self.status.stateFinal]):
					self.status.stateFinal = copy.deepcopy(current)

				lastImprovement = problem.counter.getCount()
				self.nRestarts = self.nRestarts + 1


	def replaceSolution(self, solution):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		self.status.stateFinal = copy.deepcopy(solution)

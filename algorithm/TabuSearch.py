
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *

import numpy as np
import copy


class TabuSearch (Heuristic):

	"""
	Busqueda Tabu (Glover). Tabla 1.1 del texto, siglas TS, referencia [94],
	metafora "-".

	Metaheuristica de trayectoria con memoria explicita. En cada iteracion
	enumera el vecindario completo de la solucion actual y se mueve al mejor
	candidato que no este prohibido, AUNQUE SEA PEOR que la solucion actual.
	Es la lista tabu, y no la mejora, la que impide deshacer los pasos ya dados.

	Contrasta con ACO en las dos dimensiones que estructuran el campo: ACO es
	poblacional, constructivo y con memoria implicita (feromona); TS es de
	trayectoria, mejorativo y con memoria explicita.

	:version:
	:author: Maria Fernanda Cachopo Rojas
	"""

	""" ATTRIBUTES
	tabuList  (implementation)   diccionario (trabajo, posicion) -> iteracion de expiracion
	tenure  (implementation)
	neighborhood  (implementation)
	aspiration  (implementation)
	nehCost  (implementation)    costo del arranque constructivo, espejo de ACO.lnnCost
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

		self.shortTerm  = "TS"
		self.objProblem = problem

		self.setParameters(fileConfig)

		# Memoria a corto plazo. Dos representaciones, segun tabuMode:
		#  - ATTRIBUTE: (trabajo, posicion) -> iteracion en que expira
		#  - SOLUTION : las ultimas 'tenure' permutaciones visitadas
		self.tabuList  = {}
		self.tabuQueue = []
		self.tabuSet   = set()
		self.nehCost   = None

		# ---- Solucion inicial (convencion del framework) ------------------
		# A diferencia de SA, el arranque puede ser constructivo. NEH evalua
		# internamente y esas evaluaciones se contabilizan, igual que hace ACO
		# con su tour por vecino mas cercano.
		if self.parameters.get('initialTypeSolution') == "NEH":
			self.status.stateInitial = self.buildNEH()
		else:
			self.status.stateInitial = Solution(self.objProblem, "RANDOM")

		if self.status.stateInitial.fitness == None:
			self.objProblem.evaluate(self.status.stateInitial)
			self.objProblem.counter.incCount()

		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)

		# Se conserva el costo del arranque: permite separar el merito de la
		# busqueda del merito de la heuristica constructiva. Agent lo recoge en
		# startCosts, igual que ACO.lnnCost.
		self.nehCost = self.status.stateInitial.fitness

		if run == True:
			self.tabuSearch()


	def run(self, solution=None):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		if solution == None:
			self.tabuSearch()
		else:
			self.tabuSearch(solution)


	def setParameters(self, fileConfig):
		"""
		Lee el JSON de configuracion y rellena los valores ausentes, de modo
		que una configuracion incompleta no rompa la ejecucion.

		Los nombres allNeighs y factorNeighs conservan la nomenclatura que el
		profesor ya habia fijado en sus ficheros .cfg de HC e ILS.

		@param String fileConfig :
		@return  :
		@author
		"""

		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		if not 'tenure' in self.parameters:
			self.parameters.update(dict(tenure=7))

		if not 'neighborhood' in self.parameters:
			self.parameters.update(dict(neighborhood="INSERTION"))

		if not 'allNeighs' in self.parameters:
			self.parameters.update(dict(allNeighs="ALL"))

		if not 'factorNeighs' in self.parameters:
			self.parameters.update(dict(factorNeighs=2))

		if not 'aspiration' in self.parameters:
			self.parameters.update(dict(aspiration=True))

		if not 'initialTypeSolution' in self.parameters:
			self.parameters.update(dict(initialTypeSolution="NEH"))

		# SOLUTION o ATTRIBUTE. Ver el comentario de isForbidden().
		if not 'tabuMode' in self.parameters:
			self.parameters.update(dict(tabuMode="SOLUTION"))


	# ---------------------------------------------------------------- memoria

	def isTabu(self, job, position, iteration):
		"""
		Indica si el trabajo tiene prohibido ocupar esa posicion ahora mismo.

		@param int job :
		@param int position :
		@param int iteration :
		@return boolean :
		@author
		"""

		expires = self.tabuList.get((int(job), int(position)))

		if expires == None:
			return False

		return expires > iteration


	def addTabu(self, move, iteration):
		"""
		Registra el atributo del movimiento aceptado. Se prohibe que el trabajo
		REGRESE a la posicion de la que acaba de salir, durante 'tenure'
		iteraciones. Se guarda el atributo y no la solucion completa: es mas
		barato en memoria y diversifica mejor.

		@param tuple move : (trabajo, posicion origen, posicion destino)
		@param int iteration :
		@return  :
		@author
		"""

		job, source, target = move
		self.tabuList[(int(job), int(source))] = iteration + int(self.parameters.get('tenure'))


	def aspires(self, sol):
		"""
		Criterio de aspiracion: un movimiento prohibido se acepta igualmente si
		produce una solucion mejor que la mejor encontrada hasta el momento.
		Sin el, la lista tabu podria descartar el optimo global.

		@param state.Solution sol :
		@return boolean :
		@author
		"""

		return self.objProblem.op.isBetter([sol, self.status.stateFinal])


	def signature(self, sol):
		"""
		Permutacion como tupla, para usarla de clave en la memoria por solucion.

		@param state.Solution sol :
		@return tuple :
		@author
		"""

		return tuple(int(x) for x in sol.vars)


	def addTabuSolution(self, sol):
		"""
		Registra una permutacion visitada y descarta la mas antigua cuando la
		memoria supera la tenencia.

		@param state.Solution sol :
		@return  :
		@author
		"""

		key = self.signature(sol)
		if key in self.tabuSet:
			return

		self.tabuQueue.append(key)
		self.tabuSet.add(key)

		while len(self.tabuQueue) > int(self.parameters.get('tenure')):
			self.tabuSet.discard(self.tabuQueue.pop(0))


	def isTabuSolution(self, sol):
		"""
		@param state.Solution sol :
		@return boolean :
		@author
		"""

		return self.signature(sol) in self.tabuSet


	def isForbidden(self, neighbour, move, iteration):
		"""
		Decide si un candidato esta prohibido, segun el modo configurado.

		ATTRIBUTE es la formulacion clasica: se prohibe que el trabajo regrese a
		la posicion de la que salio. Tiene un punto ciego demostrado sobre el
		vecindario de insercion: mover el trabajo J de la posicion i a la i+1
		equivale a intercambiar J con el trabajo K que ocupaba i+1, y el
		movimiento inverso puede atribuirse a K en vez de a J, con lo que el
		atributo de J no lo bloquea. Medido sobre ta001, TS entraba en un ciclo
		de periodo 2 a partir de la tercera iteracion y no mejoraba el arranque
		NEH en 166 iteraciones.

		SOLUTION guarda las ultimas 'tenure' permutaciones visitadas y prohibe
		volver a cualquiera de ellas. Impide por construccion los ciclos de
		longitud menor o igual que la tenencia. Es el modo por defecto.

		@param state.Solution neighbour :
		@param tuple move :
		@param int iteration :
		@return boolean :
		@author
		"""

		if self.parameters.get('tabuMode') == "ATTRIBUTE":
			job, source, target = move
			return self.isTabu(job, target, iteration)

		return self.isTabuSolution(neighbour)


	# ------------------------------------------------------------- arranque

	def makeSolution(self, perm):
		"""
		Envuelve una permutacion en una Solution del framework.

		@param list perm :
		@return state.Solution :
		@author
		"""

		# El segundo argumento no es "RANDOM" a proposito: evita que Solution
		# genere una permutacion aleatoria que vamos a sobrescribir igualmente.
		s = Solution(self.objProblem, "NEH")
		s.setValues(np.array(perm, dtype=int))
		return s


	def hasBudget(self):
		"""
		Comprueba que quede sitio para una evaluacion mas ADEMAS de la final.

		isStopCriteria compara con <=, asi que agotaria el presupuesto justo en
		el limite y la evaluacion de cierre del arranque se saldria del cupo.
		Con esta guarda, NEH nunca hace que TS gaste mas que GA o SA.

		@return boolean :
		@author
		"""

		return self.objProblem.counter.getCount() < self.objProblem.counter.getLimit()


	def buildNEH(self):
		"""
		Heuristica constructiva NEH (Nawaz, Enscore y Ham) para flow shop.

		1. Se ordenan los trabajos por tiempo total de proceso decreciente.
		2. Se toman los dos primeros y se conserva el mejor de sus dos ordenes.
		3. Cada trabajo restante se prueba en TODAS las posiciones de la
		   secuencia parcial y se conserva la mejor insercion.

		El desempate del paso 1 es por indice de trabajo ascendente, fijado
		para que el arranque sea reproducible entre corridas.

		@return state.Solution :
		@author
		"""

		problem = self.objProblem
		op = problem.op
		n = problem.nVar

		# Paso 1. Orden por tiempo total decreciente, desempate por indice
		totals = [(int(problem.times[j].sum()), j) for j in range(n)]
		totals.sort(key=lambda t: (-t[0], t[1]))
		order = [t[1] for t in totals]

		seq = [order[0]]
		best = None

		# Pasos 2 y 3: son el mismo bucle, insertar en todas las posiciones
		for k in range(1, n):
			job = order[k]

			bestSeq = None
			best = None

			for pos in range(len(seq)+1):

				if not self.hasBudget():
					break

				candidate = list(seq)
				candidate.insert(pos, job)

				s = self.makeSolution(candidate)
				problem.evaluate(s)
				problem.counter.incCount()

				if (best == None) or op.isBetter([s, best]):
					best = s
					bestSeq = candidate

			if bestSeq == None:
				# Presupuesto agotado a mitad de la construccion. Se completa la
				# secuencia sin evaluar para devolver siempre una permutacion
				# valida; la evalua el constructor.
				bestSeq = list(seq)
				bestSeq.append(job)
				best = None

			seq = bestSeq

		if best != None:
			return best

		return self.makeSolution(seq)


	# ------------------------------------------------------------- busqueda

	def tabuSearch(self, solution=None):
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

		name       = self.parameters.get('neighborhood')
		aspiration = self.parameters.get('aspiration')

		# ALLNEIGHS distinto de "ALL" activa el muestreo de FACTORNEIGHS
		factor = None
		if self.parameters.get('allNeighs') != "ALL":
			factor = self.parameters.get('factorNeighs')

		self.tabuList  = {}
		self.tabuQueue = []
		self.tabuSet   = set()
		self.addTabuSolution(current)

		iteration = 0

		while self.isStopCriteria():

			iteration = iteration + 1

			neighs = op.neighborhood(name, current, factor)

			best    = None
			bestMov = None

			for neighbour, move in neighs:

				# Guarda dentro del lote. El vecindario tiene (n-1)^2
				# candidatos; sin esto TS se pasaria del presupuesto hasta en
				# 360 evaluaciones con n=20 y la comparacion contra GA y SA
				# dejaria de ser justa.
				if not self.isStopCriteria():
					break

				problem.evaluate(neighbour)
				problem.counter.incCount()

				forbidden = self.isForbidden(neighbour, move, iteration)

				if forbidden and not (aspiration and self.aspires(neighbour)):
					continue

				if (best == None) or op.isBetter([neighbour, best]):
					best    = neighbour
					bestMov = move

			if best == None:
				# Todo el vecindario prohibido y nada aspira. Se olvida la
				# memoria para no quedar bloqueado sin avanzar.
				self.tabuList  = {}
				self.tabuQueue = []
				self.tabuSet   = set()
				continue

			# Se acepta AUNQUE SEA PEOR que current: asi se escapa del optimo
			# local. La lista tabu es la que impide volver sobre los pasos.
			current = best
			self.addTabu(bestMov, iteration)
			self.addTabuSolution(current)

			if op.isBetter([current, self.status.stateFinal]):
				self.status.stateFinal = copy.deepcopy(current)


	def replaceSolution(self, solution):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		self.status.stateFinal = copy.deepcopy(solution)

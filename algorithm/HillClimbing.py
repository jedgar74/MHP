from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *

import numpy as np
import copy


class HillClimbing (Heuristic):

	"""
	Ascenso de colina, siglas HC. Busqueda local pura: se mueve al vecino que
	mejora y se detiene en cuanto ningun vecino mejora, es decir en un optimo
	local.

	Por si sola es la metaheuristica mas debil de la plataforma, y esta aqui
	por lo que es en realidad: la pieza de explotacion que ILS invoca una y
	otra vez. El fichero DATA/config/ILS/ILSFa.cfg del repositorio ya lo
	declaraba asi, con INCLUDEMETHODS=HC y CONFIGMETHODS=HCF.

	Se distingue de la Busqueda Tabu en que HC NUNCA acepta un vecino peor:
	no tiene memoria con la que evitar volver sobre sus pasos, asi que aceptar
	un empeoramiento solo la haria oscilar. Escapar del optimo local es
	responsabilidad de quien la envuelve, que aqui es ILS.

	:version:
	:author: Jordano Pernia
	"""

	""" ATTRIBUTES
	neighborhood  (implementation)   INSERTION o SWAP
	strategy  (implementation)       BEST (mejor vecino) o FIRST (primero que mejora)
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

		self.shortTerm  = "HC"
		self.objProblem = problem

		self.setParameters(fileConfig)

		self.status.stateInitial = Solution(self.objProblem, "RANDOM")

		if self.status.stateInitial.fitness == None:
			self.objProblem.evaluate(self.status.stateInitial)
			self.objProblem.counter.incCount()

		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)

		if run == True:
			self.hillClimbing()


	def run(self, solution=None):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		if solution == None:
			self.hillClimbing()
		else:
			self.hillClimbing(solution)


	def setParameters(self, fileConfig):
		"""
		Lee el JSON de configuracion y rellena los valores ausentes.

		Los nombres allNeighs y factorNeighs conservan la nomenclatura de los
		ficheros .cfg que el profesor ya tenia en DATA/config/HC/.

		@param String fileConfig :
		@return  :
		@author
		"""

		self.parameters = self.readParameters(fileConfig, self.shortTerm)

		if not 'neighborhood' in self.parameters:
			self.parameters.update(dict(neighborhood="SWAP"))

		if not 'allNeighs' in self.parameters:
			self.parameters.update(dict(allNeighs="ALL"))

		if not 'factorNeighs' in self.parameters:
			self.parameters.update(dict(factorNeighs=2))

		# BEST explora el vecindario entero y toma el mejor; FIRST se queda con
		# el primero que mejora. FIRST gasta menos evaluaciones por paso pero da
		# pasos peores: cual gana depende del problema, por eso es parametro.
		if not 'strategy' in self.parameters:
			self.parameters.update(dict(strategy="BEST"))


	def hillClimbing(self, solution=None):
		"""
		Bucle principal. Termina en un optimo local o al agotarse el
		presupuesto de evaluaciones, lo que ocurra antes.

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

		# Quien llama puede pasar una solucion todavia sin evaluar
		if current.fitness == None:
			problem.evaluate(current)
			problem.counter.incCount()

		name = self.parameters.get('neighborhood')
		first = (self.parameters.get('strategy') == "FIRST")

		# ALLNEIGHS distinto de "ALL" activa el muestreo de FACTORNEIGHS
		factor = None
		if self.parameters.get('allNeighs') != "ALL":
			factor = self.parameters.get('factorNeighs')

		while self.isStopCriteria():

			neighs = op.neighborhood(name, current, factor)

			best = None

			for neighbour, move in neighs:

				# Guarda dentro del lote: el vecindario tiene cientos de
				# candidatos y sin esto HC se pasaria del presupuesto, con lo
				# que la comparacion contra GA y SA dejaria de ser justa.
				if not self.isStopCriteria():
					break

				problem.evaluate(neighbour)
				problem.counter.incCount()

				if (best == None) or op.isBetter([neighbour, best]):
					best = neighbour

				# En modo FIRST no se termina de explorar el vecindario: basta
				# con haber encontrado uno que mejora a la solucion actual.
				if first and op.isBetter([best, current]):
					break

			if best == None:
				break

			# La condicion de parada de HC: si el mejor vecino no mejora, se
			# esta en un optimo local y seguir no aporta nada.
			if not op.isBetter([best, current]):
				break

			current = best

		if op.isBetter([current, self.status.stateFinal]):
			self.status.stateFinal = copy.deepcopy(current)

		return current


	def replaceSolution(self, solution):
		"""
		@param state.Solution solution :
		@return  :
		@author
		"""

		self.status.stateFinal = copy.deepcopy(solution)

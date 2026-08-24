
# from state.Solution import *
from problem.Counter import *

from operators.OperatorsReal import *
from operators.OperatorsInt import *
from operators.OperatorsBin import *
from operators.OperatorsMix import *
from operators.OperatorsPerm import *

import numpy as np 


class Problem(object): 
	""" 
	:version:
	:author:
	"""

	""" ATTRIBUTES 
	nVar  (public) 
	typeState  (public)  
	typeProblem  (public)  
	nameShort  (public) 
	counter  (public) 
	"""
	
	
	def __init__(self):
		"""  
		@param String namInst : 
		@return  :
		@author
		""" 
		self.nVar = 0
		self.typeState = "PERMUTATIONAL" ## "INTEGER" "BINARY" "REAL" "MIX"
		self.typeProblem = "MIN"   ## "MIN" o "MAX"
		self.nameShort = "JHEDG"
		self.counter = Counter(0)
		self.upperlimits = None 
		self.lowerlimits = None
		self.typeVarMix = None
		self.op = None
		# Matriz de costos NxN. Solo la modelan los problemas basados en grafo
		# (TSP, QAP, ...). Ver getCostMatrix().
		self.matA = None

		# Se definen dos variables. La primera corresponde a la precisión de las 
		# operaciones y la segunda para la impresión de los resultados
		self.precision = None	
		self.roundFitness = 1	
		
        
	def evaluate(self, s):
		""" 
		@param state.Solution s : 
		@return  :
		@author
		"""
		pass


	def readInstance(self, ffile):
		"""  
		@param String file : 
		@return  :
		@author
		"""
		pass


	def getCostMatrix(self):
		"""
		Devuelve la matriz de costos NxN si el problema la modela, o None.
		Las metaheuristicas constructivas (ACO) la requieren para calcular la
		visibilidad heuristica; el resto del framework no la necesita.

		Por defecto devuelve None: cada problema basado en grafo debe
		sobrescribirlo. No se devuelve self.matA de forma generica porque en
		varios problemas (ToolSwitching, CarSequencing, RehearsalScheduling)
		ese atributo es una matriz de incidencia rectangular, no de costos.

		@return numpy.ndarray :
		@author
		"""
		return None


	def selOpers(self):
		if self.typeState == 'REAL':
			# print(self.typeState)
			# print(type(self.op))
			self.op = OperatorsReal(self.typeProblem)
			# print(type(self.op))
		elif self.typeState == 'INTEGER': 
			self.op = OperatorsInt(self.typeProblem)
		elif self.typeState == 'BINARY': 
			self.op = OperatorsBin(self.typeProblem)
		elif self.typeState == 'MIX': 
			self.op = OperatorsMix(self.typeProblem)
		elif self.typeState == 'PERMUTATIONAL': 
			self.op = OperatorsPerm(self.typeProblem)

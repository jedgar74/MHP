import numpy as np
import math
import copy

from operators.OperatorsGeneric import *

class OperatorsBin(OperatorsGeneric):

	"""
	:version:
	:author:
	"""

	def __init__(self, typeProblem):
		""" 
		@param String m : 
		@return String :
		@author
		"""
		super().__init__(typeProblem)
		# self.typeProblem = typeProblem
		

	def mutationFlip(self, sol):
		u = copy.deepcopy(sol)  
		
		i = np.random.randint(sol.nVar)
		
		u.vars[i] = u.vars[i]*-1   
		
		# if u.vars[i] > u.upperlimits[i]:
		# 	u.vars[i] = u.upperlimits[i]
		# elif u.vars[i] < u.lowerlimits[i]:
		# 7	u.vars[i] = u.lowerlimits[i]	 
		return u
	
    
	def mutation(self, name, sols):
		if name == 'FLIPPING':
			solx = self.mutationFlip(sols[0]) 
		else: 
			raise ValueError("This mutation method is not defined: "+name)	
		return solx


	def crossoverOnePoint(self, s1, s2):
		i1 = copy.deepcopy(s1)
		i2 = copy.deepcopy(s2) 
		alpha = np.random.randint(i2.nVar) 
		
		for g in range(alpha+1, i2.nVar):  
			i2.setValue(g, s1.getValue(g)) 
			i1.setValue(g, s2.getValue(g))
		
		# s1.prints("s1") 
		# s2.prints("s2") 	
		# i1.prints("i1") 
		# i2.prints("i2")
		return [ i1, i2 ] 


	def crossover(self, name, sols):
		if name == 'ONEPOINT':
			solx = self.crossoverOnePoint(sols[0], sols[1])
		else: 
			raise ValueError("This crossover method is not defined: "+name)		
		return solx
		




		

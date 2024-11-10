import numpy as np
import math
import copy

from operators.OperatorsGeneric import *

class OperatorsReal(OperatorsGeneric):

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
		self.defPrecision('None')
		# self.typeProblem = typeProblem

		
	# 	def randVar(self, i):
	# 		v = np.random.rand()*(u.upperlimits[i]-u.lowerlimits[i])+u.lowerlimits[i]
	# 		return v
 
 
	def defPrecision(self, x):
		if not x == 'None':
			self.precision = x     
		else:
			self.precision = 'None' 
            
            
	def rounds(self, x):    
		if not self.precision == 'None':
		    return round(x, self.precision) 
		else:
		    return x

				
	def mutationSimple(self, sol):
	# 		u=sol
	# 		i=randint(sol.nVar)
	# 		u[i]=self.randVar(i)
	# 		
		return sol



	def mutationSimple2(self, sol):
		u = copy.deepcopy(sol) 
		sigma = 0.01 
		i = np.random.randint(sol.nVar)
		u.vars[i] = u.vars[i]+ 2*(np.random.rand()-0.5)*sigma 
		
		if u.vars[i] > u.upperlimits[i]:
			u.vars[i] = u.upperlimits[i]
		elif u.vars[i] < u.lowerlimits[i]:
			u.vars[i] = u.lowerlimits[i]	 
		return u
	
    
	def mutation(self, name, sols):
		if name == 'BASIC':
			solx = self.mutationSimple(sols[0])
		elif name == 'BASIC2':
			solx = self.mutationSimple2(sols[0])	
		else: 
			# this instruction allows throwing an exception
			raise ValueError("This mutation method is not defined: "+name)
		return solx


	def crossoverSimple(self, s1, s2):
		i1 = copy.deepcopy(s1)
		i2 = copy.deepcopy(s2) 
		alpha = np.random.randint(i2.nVar)
		beta = np.random.rand()
		# print (  str(alpha) + " "+  str(beta))
		i1.setValue(alpha, s1.getValue(alpha) - beta*(s1.getValue(alpha) - s2.getValue(alpha) )) 
		i2.setValue(alpha, s2.getValue(alpha) + beta*(s1.getValue(alpha) - s2.getValue(alpha) )) 
		
		for g in range(alpha+1, i2.nVar):  
			i2.setValue(g, s1.getValue(g)) 
			i1.setValue(g, s2.getValue(g))
		
		# s1.prints("s1") 
		# s2.prints("s2") 	
		# i1.prints("i1") 
		# i2.prints("i2")
		return [ i1, i2 ] 


	def crossover(self, name, sols):
		if name == 'BASIC':
			solx = self.crossoverSimple(sols[0], sols[1])
		else: 
			raise ValueError("This crossover method is not defined: "+name)
		return solx		  




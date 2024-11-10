import numpy as np
import math
import copy

from operators.OperatorsGeneric import *

class OperatorsMix(OperatorsGeneric):

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
		# print("c "+ typeProblem) 
		super().__init__(typeProblem)
		self.defPrecision('None')
		# self.typeProblem = typeProblem
        
 
	def defPrecision(self, x):
		if not x == 'None':
			self.precision = x     
            
            
	def rounds(self, x):    
		if not x == 'None':
		    return round(x, self.precision) 
		else:
		    return x
        
            
	def mutation(self, name, sols ):
		if name == 'POWER':
			solx = self.mutationPower(sols[0]) 
		else: 
			raise ValueError("This mutation method is not defined: "+name)
		return solx  
		
		
	def mutationPower(self, sol):
		# constant to avoid division by zero, in the original paper this constant is not define
		e = 0.0001
		u = copy.deepcopy(sol) 
		
		i = np.random.randint(sol.nVar)
        
		c = np.random.rand( ) 
        
        
		p = 0
		if sol.typeVarMix[i] =="integer":
			p = np.random.randint(3)
		else:
			p = np.random.rand()
                
		s = c**p
        
		t = (sol.vars[i] - sol.lowerlimits[i] + e)/(sol.upperlimits[i] - sol.vars[i] + e)

		if t < c :
			if sol.typeVarMix[i] =="integer":
			    u.vars[i] = int(u.vars[i] - s*(u.vars[i] - u.lowerlimits[i]))
			else :
			    # u.vars[i] = u.vars[i] - s*(u.vars[i] - u.lowerlimits[i])
			    u.vars[i] = self.rounds(u.vars[i] - s*(u.vars[i] - u.lowerlimits[i]) )              
		else :
			if sol.typeVarMix[i] =="integer":
			    u.vars[i] = int(u.vars[i] + s*(u.upperlimits[i] - u.vars[i]))
			else :
			    # u.vars[i] = u.vars[i] + s*(u.upperlimits[i] - u.vars[i])			    
			    u.vars[i] = self.rounds(u.vars[i] + s*(u.upperlimits[i] - u.vars[i])	 ) 
			  
# =============================================================================
# 		if u.vars[i] > u.upperlimits[i]:
# 			u.vars[i] = u.upperlimits[i]
# 		elif u.vars[i] < u.lowerlimits[i]:
# 			u.vars[i] = u.lowerlimits[i]	 
# =============================================================================
		self.insideLimits(u, i)
        
		return u		


	def crossover(self, name, sols):
		if name =='LAPLACE':
			solx = self.crossoverLaplace(sols[0], sols[1])
		else: 
			raise ValueError("This crossover method is not defined: "+name)
		return solx
		
    
	def crossoverLaplace(self, s1, s2):
		i1 = copy.deepcopy(s1);
		i2 = copy.deepcopy(s2); 
        
		for g in range(s1.nVar): 
			a = 0.3            
			b = 0.2
			c = np.random.rand( ) 
			beta = 0
            
			if c > 0.5:
			    beta = a + b* math.log( np.random.rand() )
			else :
			    beta = a - b* math.log( np.random.rand() )	             
        
			if s1.typeVarMix[g] =="integer":
			    beta = int(beta)
            
			# i1.setValue(g, s1.getValue(g) + beta*(s1.getValue(g) - s2.getValue(g)))   
			# i2.setValue(g, s2.getValue(g) + beta*(s1.getValue(g) - s2.getValue(g)))   
			i1.setValue(g, self.rounds(s1.getValue(g) + beta*(s1.getValue(g) - s2.getValue(g))) )
			i2.setValue(g, self.rounds(s2.getValue(g) + beta*(s1.getValue(g) - s2.getValue(g))) ) 
 
			self.insideLimits(s1, g) 
			self.insideLimits(s2, g)            
            
		return [ i1, i2 ]				
						 
 	

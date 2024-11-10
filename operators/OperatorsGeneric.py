import numpy as np
import math
import copy


class OperatorsGeneric(object): 
	"""
	:version:
	:author:
	""" 
    # Chapter 3 Advanced Evolutionary Algorithms
	def __init__(self, typeProblem):
		""" 
		@param String m : 
		@return String :
		@author
		"""
		self.typeProblem = typeProblem

		
	def isWorse(self, sols):
		""" 
		this method returns a value of True if the first solution is worse than 
		the second solution
		@param String m : 
		@return String :
		@author
		"""
		
		if self.typeProblem == 'MIN' :
			if sols[0].fitness > sols[1].fitness:
				return True
			else:
				return False
		else:
			if sols[0].fitness < sols[1].fitness:
				return True
			else:
				return False


	def isBetter(self, sols):
		# this method returns a value of True if the first solution is better than 
		# the second solution
		# print("  "+self.typeProblem) 
		if self.typeProblem == 'MIN' :
			if sols[0].fitness < sols[1].fitness:
				return True
			else:
				return False
		else:
			if sols[0].fitness > sols[1].fitness:
				return True
			else:
				return False
				
    
	def insideLimits(self, sol, i):
		# If the value of a variable is outside the limits, the upper or lower limit 
		# of said variable is assigned.
		if sol.vars[i] > sol.upperlimits[i]:
			sol.vars[i] = sol.upperlimits[i]
		elif sol.vars[i] < sol.lowerlimits[i]:
			sol.vars[i] = sol.lowerlimits[i]	   
			
			      
	def selection(self, name, sols):
		# This method allows choosing a specific selection method
		if name =='TOURNAMENT':
			solx = self.tournament(sols)
		elif name =='ROULETTE':
			solx = self.tournament(sols)		
		elif name =='RANKING': 
			solx = self.ranking(sols)
		elif name =='SUS':
			solx = self.stochasticUniversalSampling(sols)
		else: 
			# this instruction allows throwing an exception
			raise ValueError("This method is not defined: "+name)						
		return solx	
    
    
	def tournament(self, sols): 
		solx = []
		# 	sums = sols.totalFitness() 
		
		# Tournament size. To define a parameter 
		size = 2
		for t in range(2): 
			c = np.random.randint(sols.popSize) 
	
			for j in range(size):
				c1 = np.random.randint(sols.popSize)  
				
				if self.isBetter([sols.getIndividual(c1), sols.getIndividual(c)]): 
					c = c1
		 
			solx.append(sols.getIndividual(c))
		 
		return solx     
 

	def roulette(self, sols): 
		solx = []
	 
		x = 0
		maxx = -1e100
		minx =  1e100 
		for g in range(sols.popSize): 
			t = sols.getIndividual(g).fitness
			x = x + t 
			# x = x + (400 - sols.getIndividual(g).fitness)			
			if t > maxx:
				maxx = t 
			elif t < minx:
				minx = t 			
		x = x + len(sols.popSize)	 
			 
		for s in range(2): 
			y = np.random.rand() * x 
			i = 0
			z = 0
		 
			while (z < y):
				if self.typeProblem == 'MIN' :
					z = z + (maxx - sols.getIndividual(i).fitness) + 1 
				elif self.typeProblem == 'MAX' :
					z = z + sols.getIndividual(i).fitness  + 1 					
				i = i + 1 
				
			q = sols.popSize 
			if i == 0:
				solx.append(sols.getIndividual(0) )
			elif i == q:
				solx.append(sols.getIndividual(q-1))
			else:
				solx.append(sols.getIndividual(i))
			
		# return [ solx[0], solx[1] ]		
		return solx  
             
             
	def ranking(self, sols):  
		solx = [] 
		
		# la poblacion debe ordenarse
		sols.sort()
		
		sumx = 0
		for i in range(sols.popSize):
			sumx = sumx + (1/(i+1))      
		
		np = 2		
		for i in range(np):	 
			c = 0
			r = np.random.rand()*sumx
			for j in range(sols.popSize): 
				c = c + (1/(j+1))
				if (c >= r) :
					solx.append(sols.getIndividual(j)) 
					break 
					
		return solx
		             
             
	def stochasticUniversalSampling(self, sols):  
		solx = []
		np = 2
		x = 0
 
		for g in range(sols.popSize):  
			x = x + sols.getIndividual(g).fitness 
 			 
		interval = x / np
		value = np.random.rand() * interval
		
		for i in range(np): 
			valuex = value + i*interval
			sumx = 0
			index = 0
			while True: 
				sumx = sumx + ( sols.getIndividual(index).fitness / x )
				if  sumx >= valuex  :  
					solx.append(sols.getIndividual(index)) 
					break
				else : 
					index = index + 1 
		
		return solx
		
		
	def indexRandom(self, index, nsol, tsol):
		indices = [] # Z=np.zeros(4)
		indices.append(index) 
	 
		m = []
		for i in range(tsol) :
		    if (i != index): 
		        m.append(i) 

		k = 0 
		while k < nsol:  
		    isol = np.random.randint(len(m))
		    if not isol in indices: 
		        indices.append(isol)
		        m.pop(isol) # m.remove(isol) 
		        k = k + 1
		
		# print(indices)
		 		 
		return indices			


	def select2Random(self, n):
		# 
		t1 = np.random.randint(n)
		t2 = np.random.randint(n)
		
		while (t1 == t2):
			t1 = np.random.randint(n)
			t2 = np.random.randint(n)
		
		if t1 > t2:
			aa = t1
			t1 = t2
			t2 = aa						
		 		 
		return [ t1, t2	]	

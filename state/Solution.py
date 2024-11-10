import numpy as np
#import copy

class Solution(object): 
	
	def __init__(self, problem, init):
		""" 
		@return:
		@author
		""" 
		
		self.fitness = None 
		self.nVar = problem.nVar	
		self.vars = np.zeros(self.nVar)
		self.upperlimits = problem.upperlimits
		self.lowerlimits = problem.lowerlimits
		self.typeVarMix = problem.typeVarMix
		# 	print (str (problem.typeState) + " :::"+str (init) )
		
		
		if problem.typeState  ==  "PERMUTATIONAL"  :  
# =============================================================================
# 			print ("-------")             
# 			print (problem.typeVarMix) 
# 			print (problem.perm)
# 			print ("-------")  			
# =============================================================================
			if init == "RANDOM" and problem.typeVarMix == "INTEGER":
				self.vars = self.initRandomizePerArray(problem.perm) 
			elif init == "RANDOM" :
				self.vars = self.initRandomizePer( ) 
				
		elif problem.typeState  ==  "BINARY"  : 
			if init  ==  "RANDOM"  :
				self.vars = self.initRandomizeBin( )  
		elif problem.typeState  ==  "REAL"   : 
			# self.upperlimits = problem.upperlimits 
			# self.lowerlimits = problem.lowerlimits
			if init  ==  "RANDOM"  :
				self.vars = self.initRandomizeRea( )   
		elif problem.typeState  ==  "MIX"   : 
			# self.upperlimits = problem.upperlimits 
			# self.lowerlimits = problem.lowerlimits
			# self.typeVarMix = problem.lowerlimits
			if init  ==  "RANDOM"  :
				self.vars = self.initRandomizeMix() 
				
		self.roundFitness = problem.roundFitness						
		
        
	def evaluate(self, problem):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		 
		self.fitness = problem.evaluate()	
	
			
	def initRandomizePer(self ):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		# 	u = np.zeros(self.nVar)
		# 	v = np.zeros(self.nVar)
		# 	for i in range(self.nVar): 
		# 		v[i] = i  
				
		# 	j=0 
		# 	while(len(v) > 0):
		# 		y = np.random.randint(len(v)) 
		# 		u[j] = y  
		# 		v.remove(y) 
		# 		j=j+1   
		# # # u = np.random.choice(a, self.nVar, replace=False)	 
		u = np.random.permutation(self.nVar)
		return u	
		
		
	def initRandomizePerArray(self, perm ):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		# 	u = np.zeros(self.nVar)
		# 	v = np.zeros(self.nVar)
		# 	for i in range(self.nVar): 
		# 		v[i] = i  
				
		# 	j=0 
		# 	while(len(v) > 0):
		# 		y = np.random.randint(len(v)) 
		# 		u[j] = y  
		# 		v.remove(y) 
		# 		j=j+1   
		# # # u = np.random.choice(a, self.nVar, replace=False)	
			
		u = np.random.permutation(perm)
		# u = perm
		return u		
		
			
	def initRandomizeRea(self):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		u = np.zeros(self.nVar)
		
		for i in range(self.nVar): 
			u[i] = np.random.rand()*(self.upperlimits[i] - self.lowerlimits[i]) + self.lowerlimits[i]
				
		return u
		
			
	def initRandomizeMix(self):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		u = np.zeros(self.nVar)
		
		for i in range(self.nVar): 
			if self.typeVarMix[i] == "integer":
				u[i] = np.random.randint(self.upperlimits[i] - self.lowerlimits[i] + 1 ) + self.lowerlimits[i] 
			else : 	
				u[i] = np.random.rand()*(self.upperlimits[i] - self.lowerlimits[i]) + self.lowerlimits[i]
                
		return u				
				
    
	def initRandomizeBin(self ):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		u = np.zeros(self.nVar)
 		 
		for i in range(self.nVar): 
			if np.random.randint(2) == 1:
				u[i] = 1  
			# The binary minimum value is defined as -1	
			else :
				u[i] = -1	
		# print(u)							
		return u	
	
	
	def getValue(self, u ):	
		return self.vars[u ]
	
    
	def setValue(self, i, u ):	
		self.vars[i] = u
	
    
	def setValues(self, u ):	
		self.vars = u
		
		    
	def setFitness(self, fit):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		 
		self.fitness = fit	
		
		
	def prints(self, name= ""):
		"""  
		@return  :
		@author
		"""
		print ( name + " ", end = "")
		for i in range(self.nVar):  
			# 	print (  str(self.getValue(i)) + " ", end = "") %.1
			print (  str(round(self.getValue(i), self.roundFitness)) + " ", end = "")
		try:
			print ( " ::: " +  str(round(self.fitness, self.roundFitness)) ) 
		except :    
			print ( " ::: None "  ) 
		# 	print ( self.vars )
		
		
	def isEquals(self, sol):	
		isEquals = True
		for i in range(self.nVar):
			if self.vars[i] != sol.getValue(i) :
				isEquals = False
				break 	
		return isEquals

# =============================================================================
# 	def copy(self, sol): 	
# 		self = copy.deepcopy(sol)     
# =============================================================================

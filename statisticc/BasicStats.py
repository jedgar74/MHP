import math 

class BasicStats(object):

	""" 
	:version:
	:author:
	"""

	""" ATTRIBUTES
	solutions  (public)
	label  (implementation)  
	op  (implementation) 
	"""

	def __init__(self, typeProblem):
		""" 
		@return:
		@author
		"""
		self.solutions = []
		self.label = None
		self.typeProblem = typeProblem

	def removeAllSolutions(self):
		""" 
		@return  :
		@author
		"""
		pass

 
	def contains(self, s):
		""" 
		@param state.Solution s : 
		@return boolean :
		@author
		"""
		pass


	def getInitSolution(self):
		""" 

		@return state.Solution :
		@author
		"""
		pass


	def getSolution(self, i):
		"""
		 

		@param int i : 
		@return double :
		@author
		"""
		return self.solutions[i]


	def getSolutionComplete(self, i = None):
		""" 
		@param int i : 
		@return state.Solution :
		@author
		""" 
     
		if (i == None) :
			b = self.better()
			return self.solutions[b]
            
		else : 
			return self.solutions[i]
            
		


	def nSolutions(self):
		""" 
		@return int :
		@author
		"""
		return len(self.solutions)

	
	def getLabel(self):
		"""  
		@return String :
		@author
		"""
		return self.label 

	
	def setLabel(self, label):
		""" 
		@param String label : 
		@return  :
		@author
		"""
		self.label  = label 

	
	def add(self, s):
		""" 
		@param state.Solution s : 
		@return  :
		@author
		"""
		self.solutions.append(s)

	
	def getBetter(self):
		""" 
		@return double :
		@author
		"""
		b = self.better()
		return self.solutions[b].fitness


	def getNBetter(self):
		""" 
		@return double :
		@author
		"""
		q = self.solutions[0].fitness
		k = 1 
		for i in range(1, len(self.solutions)):   
			if (self.solutions[i].fitness < q):
				k = 1
				q = self.solutions[i].fitness
			elif (self.solutions[i].fitness == q):
				k = k + 1
                
		return k


	def prints(self):
		"""  
		@return  :
		@author
		"""
		print(":: Metaheuristic :: " + self.label + "  ")
		print(":: N. Experiment.:: " + str(len(self.solutions))) 
		print("-----------------------------------") 
		q = self.better()
		print(":: Better fitness :: "+ str(round(self.solutions[q].fitness, 3))  ) 
		ave = self.average()
		print(":: Average        :: "+ str(round(ave, 3)) ) 
		print(":: St. Deviation  :: "+ str(round(self.stDeviat(ave), 3)) ) 
		print(":: Better Solution in the experiment :: "+str(q+1)) 
		print(":: N. Better Solution :: "+str(self.nBetter(self.solutions[q].fitness))) 

		self.solutions[q].prints() 
		
		

	def toString(self):
		"""
		 

		@return String :
		@author
		"""
		pass


	def printAllSolutions(self):
		"""
		 

		@return  :
		@author
		"""
		for i in range(len(self.solutions)):  
			self.solutions[i].prints()


	def printAllInfoSolution(self):
		"""
		 

		@return  :
		@author
		"""
		pass


	def better(self):
		""" 
		@return int :
		@author
		"""
		q = self.solutions[0].fitness  
		k = 0 
		for i in range(1, len(self.solutions)):  
			if self.typeProblem == "MIN":
				if self.solutions[i].fitness < q :
					k = i 
					q = self.solutions[i].fitness 
			else:
				if self.solutions[i].fitness > q :
					k = i 
					q = self.solutions[i].fitness 		
	 
		return k


	def average(self):
		""" 
		@return double :
		@author
		"""
		q=0
		for i in range(len(self.solutions)): 
			# self.solutions[i].prints()
			# print(self.solutions[i].fitness )
			q = q + self.solutions[i].fitness 
		return q/len(self.solutions) 


	def stDeviat(self, media):
		""" 
		@param double media : 
		@return double :
		@author
		"""
		q=0 
		for i in range(len(self.solutions)):  
			q= q + (self.solutions[i].fitness - media)**2 
		 	
		return math.sqrt(q /len(self.solutions)) 


	def nBetter(self, b):
		""" 
		@param double media : 
		@return double :
		@author
		"""
		q = 0 
		for i in range(len(self.solutions)): 
			if self.solutions[i].fitness == b:
				q = q + 1  
		 	
		return q 

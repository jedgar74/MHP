from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np 

class TravelingSalesmanProblem (Problem):

	""" 
	Define the classic problem termed N-Queens problems
	:version:
	:author: Jhon Amaya
	"""

	def __init__(self, namInst=None):
		""" 
		@param String namInst : 
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "TSP"   
		# print(self.typeState)
		self.selOpers()
		# print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst) 
	  

	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@
        
		"""
 
   
		with open('./DATA/instances/TSP/'+namFile, 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n') 
            
		for j in range(len(lines)): 
			if (len(lines[j]) < 2):   
			   lines.pop(j) 
       
		self.nVar = len(lines) 
		self.matA = np.zeros(shape=(self.nVar, self.nVar))  
	 
		for j in range(len(lines)): 
			r = lines[j].split()  
			for d in range(len(r)):  
				self.matA[j][d] = float(r[d])  
		print(self.matA)    

            

	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""  
        
		value = 0  
		
		for j in range(self.nVar - 1):   
			value = value + self.matA[s.vars[j+1]][s.vars[j]]
		 
		value = value + self.matA[s.vars[self.nVar-1]][s.vars[0]]
		s.setFitness(value)
        

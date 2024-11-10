from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np

class LowAutocorrelationBinarySequenceProblem(Problem):

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
		self.nameShort = "LABS"  
		self.typeState = "BINARY"        
        
		# print(self.typeState)
		self.selOpers()
		# print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst) 
	  

	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@author
		"""
		self.nVar =  namFile 


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
        
        
		fitness = 0
		tmp = np.zeros(self.nVar - 1) 
		# Compute the coefficients
 
		
		for k in range(self.nVar - 1):
			for i in range(self.nVar - k- 1):
				tmp[k] = tmp[k] +  s.vars[i]*s.vars[i+k+1]  
			 
		for k in range(self.nVar - 1):
			fitness = fitness + (tmp[k]*tmp[k]) 

		s.setFitness( fitness) 

		# Low autocorrelation binary sequences: Number theory-based 
		# analysis for minimum energy level, Barker codes

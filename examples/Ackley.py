from problem.Problem import *

import numpy as np
from scipy.integrate import odeint
import math  

import json

class Ackley(Problem):

	""" 
	Define the classic problem termed N-Queens problems
	:version:
	:author: Jhon Amaya
	"""


	# def __init__(self, nVar):
	# 	"""  
	# 	@param int nVar : 
	# 	@return  :
	# 	@author
	# 	"""
	# 	super().__init__()
	# 	self.nameShort = "LV"  
	# 	self.nVar =  nVar 
		 
	
	def __init__(self, namInst=None):
		""" 
		@param String namInst : 
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "Ackley"  
		self.typeState =  "REAL" 
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
		with open('./DATA/instances/Ackley/'+namFile) as file:
			data = json.load(file)
		
		self.A  = data['A']
		self.B  = data['B']
		self.C  = data['C']

		self.nVar = data['N'] 
		
		self.upperlimits = data['upperlimits']
		self.lowerlimits = data['lowerlimits']
		# self.nVar = data['nVar']



	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		
		sum1 = 0
		sum2 = 0   
		

		for i in range(self.nVar): 
			tmp = s.vars[i]
			sum1 = sum1+ tmp**2 
			sum2 = sum2+ math.cos(self.C*tmp) 
		 

		fit = self.A + math.exp(1)- self.A*math.exp(-self.B*math.sqrt( sum1/self.nVar))-math.exp( sum2/self.nVar)		
	
 
		s.setFitness(fit ) 

 


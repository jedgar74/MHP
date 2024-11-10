from problem.Problem import *

import numpy as np
from scipy.integrate import odeint
import math 

import json

class WeaponTargetAssignment(Problem):

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
		self.nameShort = "WTA"  
		# print(self.typeState)
		self.selOpers()
		print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst) 
		

	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@author
		"""
		with open('./DATA/instances/WTA/'+namFile) as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n') 
            
		vFile = []
		linetFile = []
		h=0        
		for j in range(len(lines)): 
			if '#' in lines[j]:
				h=h+1            
			else :
				if h==1 and len(lines[j])>1:
					vFile.append(lines[j])            
				elif h==2 and len(lines[j])>1:       
					tmp = lines[j].replace(",", ".") 
					linetFile.append(tmp)
             
			
		#  Second step. Process line
		self.nVar = len(linetFile) 
		self.nTargets = len(vFile) 
		self.vTarg = np.zeros(self.nTargets) 
 
		for i in range(self.nTargets): 
			self.vTarg[i] = int(vFile[i])
			
		    
		self.matA = np.zeros(shape=(self.nVar, self.nTargets))     
 
		for i in range(self.nVar):
			 
			r = linetFile[i].split()  
			for d in range(len(r)):  
				self.matA[i][d]=float(r[d])

		         
		print(self.matA) 
 



	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		e = np.zeros(self.nTargets)   

		for t in range(self.nTargets): 
			e[t]=1	 

		z=0
		# computing the E(.) values
		for t in range(self.nVar): 
			# revisar
			# z = v[t]	+
			z = s.vars[t]            
            
			e[z] = e[z] * (1- self.matA[t][z])* self.vTarg[z]	 
			pass

		total=0
		for t in range(self.nTargets): 
			total= total + e[t]	 

		s.setFitness( total )




















 
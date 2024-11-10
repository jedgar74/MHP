#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 20 16:39:50 2020

@author: tauger
"""
from problem.Problem import *

class UnitCommitmentProblem (Problem):

	""" 
	Define the problem termed Unit Commitment Problem 
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
		self.nameShort = "UCP"   
		self.typeState = "BINARY"  
		# print(self.typeState)
		self.selOpers()
		# self.op.defPrecision(1)
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
		Se utilizó el artículo de Botero para calcular el fitness. Sin embargo se usa 
		una representación de la solución diferente, dónde en lugar de binario se utilizó 
		de tipo real
		
		@param state.Solution s : 
		@return  :
		@author
		"""
		pl = 80 * s.nVar
		sumP = 0
		p_i = 100
		pen = 110
		
		## we guess the values -1 and 1
		for k in range( s.nVar ): 
			temp = s.vars[k] ## ((BinaryN) s.getVar().allvar[k]).getValue()
			sumP = sumP + p_i*(temp+1)/2
        
		fitness = 0 
		for k in range(s.nVar): 
			aux=((1.0*k)/(s.nVar - 1))
			temp = s.vars[k] ##  ((BinaryN) s.getVar().allvar[k]).getValue()
			fitness = fitness + (p_i*(30+70*aux))*(temp+1)/2
	  
		## System.out.print ("  F "+ fitness)
		if  sumP < pl:
			fitness = fitness +(pen*(pl-sumP))
		## System.out.println("  G "+ fit)
		## printMat(A, SP, N, M) 
		
		s.setFitness(round(fitness, 2))


	def optimum(self):
		""" 
		@param String namFile : 
		@return  :
		@author
		"""  
		val = round(2400*self.nVar + 560*self.nVar*((4*self.nVar - 5)/(self.nVar - 1)) , 2)
		print("Optimum value ("+str(self.nVar)+"): "+str(val)) 
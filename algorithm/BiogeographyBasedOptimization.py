#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  3 11:21:59 2020

@author: tauger
""" 

from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import * 

import numpy as np
import math 
import copy

class BiogeographyBasedOptimization(Heuristic):	   
    """
	:version:
	:author:
	"""

    """ ATTRIBUTES
	shortTerm  (public)
	individuals  (implementation)
	see selection method
	operSelection  (implementation)
	nIndividualsTournament  (implementation)
	see crossover method
	operCrossover  (implementation)
	see mutation method
	operMutation  (implementation)
	or GENERATIONAL --- before geneticType
	version  (implementation)
	probCrossover  (implementation)
	probMutation  (implementation)
	lambda  (implementation)
	population  (implementation)
	nMutations  (implementation)
	nCrossovers  (implementation)
	initialSolution  (implementation)
	""" 


    def __init__(self, problem, fileConfig, run=True):
    	""" 
		@param problem.Problem problem : 
		@param String _fileConfig : 
		@return  :
		@author
		"""
    	super().__init__()
		
    	self.shortTerm  = "BBO"
    	self.objProblem = problem  
        
    	self.setParameters(fileConfig)
    	self.popul = Population(self.parameters.get('habitats'), self.objProblem, self.parameters.get('initialTypeSolution'))
    	self.popul.sort()
    	self.objProblem.counter.incCount(self.parameters.get('habitats'))
		
    	self.status.stateInitial = self.popul.getBetterSort()
    	self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        
        # Sólo están implementadas las versiones tipo bin  quedaría por definir 
        # las variables tipo exp 
    	if  run == True :
			# if  self.parameters.get('version') == "STEADY" :
			# 	self.geneticAlgorithm(self.status.stateFinal)
			# else:
			# 	self.geneticAlgorithmGen(self.status.stateFinal)
    		self.biogeographyBasedOptimization(self.status.stateFinal)
	    
        
    def run(self, sol = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		# Este código debe ser revisado y corregido
# =============================================================================
#     	if  self.parameters.get('version') == "STEADY" :
#     		if sol == None :
#     			self.geneticAlgorithm()
#     		else :
#     			self.geneticAlgorithm(sol)
#     	else:
#     		if sol == None :
#     			self.geneticAlgorithmGen()
#     		else :
#     			self.geneticAlgorithmGen(sol)
# =============================================================================
    	pass		
    			
    
    def setParameters(self, fileConfig):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
  
    	self.parameters = self.readParameters(fileConfig, self.shortTerm)
		# print(self.parameters)
    	for i in range(7): # (int i = 0 i < nameParameters.size() i++) {

    		if not 'initialTypeSolution' in self.parameters : 
    			self.parameters.update(dict(initialTypeSolution="RANDOM"))	
							
    		if not 'habitats' in self.parameters :  # 'individuals'
    			self.parameters.update(dict(habitats=10))
				
    		if not 'version' in self.parameters :
    			self.parameters.update(dict(version="BASIC"))  
								
# =============================================================================
#     		if not 'hmcr' in self.parameters :  # crossoverfactor
#     			self.parameters.update(dict(hmcr=0.9))
# 					
#     		if not 'par' in self.parameters :  # weightfactor
#     			self.parameters.update(dict(par=0.8)) 
#                 
#     		if not 'bw' in self.parameters :  # crossoverfactor
#     			self.parameters.update(dict(bw=0.9))
# 					
#     		if not 'ni' in self.parameters :  # weightfactor
#     			self.parameters.update(dict(ni=0.8)) 	 	 
# =============================================================================
    	# print(self.parameters) 
		  
          
    def biogeographyBasedOptimization(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
    	if solution != None :
    		self.popul.addSort(solution)		
        
    	self.popul.printFitness("POP(INI)")    
        
    	self.vmu = np.zeros(self.parameters.get('habitats'))
    	self.vlambda = np.zeros(self.parameters.get('habitats'))
    	habplus1 = self.parameters.get('habitats')+1
    
    	for i in range(self.parameters.get('habitats')):
    		self.vmu[i] = (habplus1 -  i ) / (habplus1)
    		self.vlambda[i] = 1 - self.vmu[i]
    
    	while self.isStopCriteria():  
    		for i in range(self.parameters.get('habitats') ): 
    		    nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution'));
                
    		    for j in range(nextState.nVar):
    		        # nextState
    		        if np.random.rand() <= self.parameters.get('hmcr'):
    		            nextState.setValue(j, self.getHMemory(j)) 
    		            if np.random.rand() <= self.parameters.get('par'):
    		                nextState.setValue(j, self.getPitchAdjusting(j, nextState))  
    		        else :
    		            nextState.setValue(j, self.getRandom(j, nextState))  
                        
    		    self.objProblem.evaluate(nextState)
    		    self.objProblem.counter.incCount()
				# nextState.prints("+++") 
				# self.popul.getIndividual(i).prints("---")    
				# print(self.objProblem.typeProblem) 
    		    if self.objProblem.op.isBetter([nextState, self.popul.getIndividual(i) ]):  
    		    	# popTemp.addSort(nextState )  
    		        self.popul.addSort(nextState )
			 							 
				#popTemp.printFitness("POP a") 			
			       
    		# self.popul = copy.deepcopy(popTemp)
			# self.popul.printFitness("POP(FIN)")
    		# popTemp.removeAll()   
			# popTemp.printFitness("POP c") 
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)") 
     
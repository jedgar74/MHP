#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 10:43:28 2020

@author: tauger
"""

from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import * 

import numpy as np
import math 
import copy


class HarmonySearch(Heuristic):	
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
		
    	self.shortTerm  = "HS"
    	self.objProblem = problem  
        
    	self.setParameters(fileConfig)
    	self.popul = Population(self.parameters.get('harmonies'), self.objProblem, self.parameters.get('initialTypeSolution'))
    	self.popul.sort()
    	self.objProblem.counter.incCount(self.parameters.get('harmonies'))
		
    	self.status.stateInitial = self.popul.getBetterSort()
    	self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        
        # Sólo están implementadas las versiones tipo bin  quedaría por definir 
        # las variables tipo exp 
    	if  run == True :
			# if  self.parameters.get('version') == "STEADY" :
			# 	self.geneticAlgorithm(self.status.stateFinal)
			# else:
			# 	self.geneticAlgorithmGen(self.status.stateFinal)
    		self.harmonySearch(self.status.stateFinal)
	    
        
    def run(self, sol = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		# Este código debe ser revisado y corregido
    	if  sol == None :
    		self.harmonySearch()
    	else :
    		self.harmonySearch(sol)

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
							
    		if not 'harmonies' in self.parameters :  # 'individuals'
    			self.parameters.update(dict(harmonies=10))
				
    		if not 'version' in self.parameters :
    			self.parameters.update(dict(version="BASIC"))  
								
    		if not 'hmcr' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(hmcr=0.9))
					
    		if not 'par' in self.parameters :  # weightfactor
    			self.parameters.update(dict(par=0.8)) 
                
    		if not 'bw' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(bw=0.9))
					
    		if not 'ni' in self.parameters :  # weightfactor
    			self.parameters.update(dict(ni=0.8)) 	 	 
    	# print(self.parameters) 
		
		
    def harmonySearch(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
    	if solution != None :
    		self.popul.addSort(solution)		
        
    	self.popul.printFitness("POP(INI)")    
 
    	while self.isStopCriteria():  
    		for i in range(self.parameters.get('harmonies') ): 
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
     
        
    # Podrían colocarse estos métodos en las clases asociadas a los 
    # operadores 
    def getHMemory(self,  j):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
 
    	h = np.random.randint(self.parameters.get('harmonies') ) 
       
    	return self.popul.getIndividual(h).getValue(j)    
        
    
    def getPitchAdjusting(self, j, nextState):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	r = np.random.rand()*self.parameters.get('bw')
        
    	if nextState.typeVarMix[j] == "integer":
            rr = int(nextState.getValue(j) + r )
    	else :
            rr = nextState.getValue(j) + r  
        
    	if rr > nextState.upperlimits[j]:
            rr = nextState.upperlimits[j]
    	elif rr < nextState.lowerlimits[j]:
            rr = nextState.lowerlimits[j]
            
    	return rr          
    
    
    def getRandom(self, j, nextState):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
  
    	r = np.random.rand() 
        # REVISAR EL SIGNO MENOS-----------
    	if nextState.typeVarMix[j] =="integer":
            rr = int(nextState.lowerlimits[j] - r*(nextState.upperlimits[j] - nextState.lowerlimits[j]))
    	else :
            rr = nextState.lowerlimits[j] - r*(nextState.upperlimits[j] - nextState.lowerlimits[j])
        
    	return rr        
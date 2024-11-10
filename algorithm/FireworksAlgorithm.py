#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:20:33 2020

@author: tauger
"""

from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import * 

import numpy as np
import math 
import copy

class FireworksAlgorithm(Heuristic):	    
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
		
    	self.shortTerm  = "FWA"
    	self.objProblem = problem  
        
    	self.setParameters(fileConfig)
    	self.popul = Population(self.parameters.get('fireworks'), self.objProblem, self.parameters.get('initialTypeSolution'))
    	self.popul.sort()
    	self.objProblem.counter.incCount(self.parameters.get('fireworks'))
		
    	self.status.stateInitial = self.popul.getBetterSort()
    	self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        
        # Sólo están implementadas las versiones tipo bin  quedaría por definir 
        # las variables tipo exp 
    	if  run == True :
			# if  self.parameters.get('version') == "STEADY" :
			# 	self.geneticAlgorithm(self.status.stateFinal)
			# else:
			# 	self.geneticAlgorithmGen(self.status.stateFinal)
    		
    		if  self.parameters.get('version') == "BASIC" :
    		    if  self.objProblem.typeState == "PERMUTATIONAL" :
    		        self.fireworksAlgorithmPerm(self.status.stateFinal)
    		    else :
    		        self.fireworksAlgorithm(self.status.stateFinal)	    
        
    def run(self, sol = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		# Este código debe ser revisado y corregido
    	if  self.parameters.get('version') == "STEADY" :
    		if sol == None :
    			self.geneticAlgorithm()
    		else :
    			self.geneticAlgorithm(sol)
    	else:
    		if sol == None :
    			self.geneticAlgorithmGen()
    		else :
    			self.geneticAlgorithmGen(sol)
            

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
							
    		if not 'fireworks' in self.parameters :  # 'individuals'
    			self.parameters.update(dict(fireworks=10))
				
    		if not 'version' in self.parameters :
    			self.parameters.update(dict(version="BASIC"))  
								
    		if not 'm' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(m=4))
					
    		if not 'a' in self.parameters :  # weightfactor
    			self.parameters.update(dict(a=0.3)) 
                
    		if not 'b' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(b=0.7))
					
    		if not 'aprime' in self.parameters :  # weightfactor
    			self.parameters.update(dict(aprime=3)) 	 	 
    	# print(self.parameters) 
		
        
    def fireworksAlgorithm(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
    	if solution != None :
    		self.popul.addSort(solution)		
        
    	self.popul.printFitness("POP(INI)")  
    	popTx = Population(0, self.objProblem)
 
    	while self.isStopCriteria():  
    		s = self.nSparks() 
    		# print(s )
    		a = self.amplitudes() 
    		# print(a )            
    		sparks = self.displacement(s, a)
    		self.gaussianMutation(sparks)
    		popTx.addSort(sparks.getIndividual(0), True)
            
    		popTx = self.selectionStrategy(sparks, popTx)
    		# print()      
    		# print(sparks.popSize)            
    		# print(popTx.popSize) 
    		# print(self.popul.popSize)             
    		self.popul = copy.deepcopy(popTx)
    		popTx.removeAll()
			# sparks.removeAll() 
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)") 		
    	self.popul.prints()        
        
    # Podrían colocarse estos métodos en las clases asociadas a los 
    # operadores 
    def nSparks(self ):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	s = np.zeros(self.popul.popSize ) 
    	e = 0.001 
        
    	worst = self.popul.getIndividual(self.popul.popSize - 1).fitness
    	sumx = 0
    	for j in range(self.popul.popSize):
    	    sumx = sumx + math.fabs(worst - self.popul.getIndividual(j).fitness)
    	sumx = sumx + e
    	# print(sumx)         
    	for j in range(self.popul.popSize):   
            tmp = self.parameters.get('m')*(math.fabs(worst - self.popul.getIndividual(j).fitness) + e)/sumx
            if tmp  < self.parameters.get('m')*self.parameters.get('a'):
                val = round(self.parameters.get('m')*self.parameters.get('a')) 
            elif tmp > self.parameters.get('m')*self.parameters.get('b') and self.parameters.get('a') < self.parameters.get('b') and self.parameters.get('b') < 1:
                val = round(self.parameters.get('m')*self.parameters.get('b'))     
            else:
                # no tiene mucho sentido as defined by Tan_2015_Fireworks_Algorithm
                # val = round(self.parameters.get('m')*self.parameters.get('a')) 
                val = tmp
            s[j] = int(val)    
    	return s      


    def amplitudes(self ):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	a = np.zeros(self.popul.popSize )     
    	e = 0.001 
        
    	better = self.popul.getIndividual(0).fitness
    	sumx = 0
    	for j in range(self.popul.popSize):
            sumx = sumx + math.fabs(better - self.popul.getIndividual(j).fitness)
    	sumx = sumx + e
        
    	for j in range(self.popul.popSize):   
            a[j] = self.parameters.get('aprime')*(math.fabs(better - self.popul.getIndividual(j).fitness) + e)/sumx
              
    	return a      


    def displacement (self, s, a):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	popTemp = Population(0, self.objProblem)  
    	# print(s ) 
        
    	for i in range(self.popul.popSize):  
    	    for j in range(int(s[i])):
                nextState = copy.deepcopy(self.popul.getIndividual(i)) 
                dimension = np.random.randint(self.objProblem.nVar )
                for k in range(dimension): 
                    rr = nextState.getValue(k) + (np.random.rand()*2*a[i] -  a[i])
                    
                    if self.objProblem.typeState == "MIX" and nextState.typeVarMix[k] =="integer":
                        rr = int(rr)  

                    if rr > nextState.upperlimits[k]:
                        rr = nextState.upperlimits[k]
                    elif rr < nextState.lowerlimits[k]:
                        rr = nextState.lowerlimits[k]
              
                    nextState.setValue(k, rr)    
                self.objProblem.evaluate(nextState)
                self.objProblem.counter.incCount()
                # verificar si esta solución ya está dentro de la población    
                popTemp.addSort(nextState, True)
    	return popTemp          
    
    
    def gaussianMutation(self, popTemp):
        # definir como parametro
    	self.gaussian = int(self.popul.popSize*0.5) 
    	for i in range(self.gaussian):
            d = np.random.randint(self.popul.popSize)
            nextState = copy.deepcopy(self.popul.getIndividual(d)) 
            dimension = np.random.randint(self.objProblem.nVar )
            for k in range(dimension): 
                rr = nextState.getValue(k) * np.random.rand() 
                if rr > nextState.upperlimits[k]:
                    rr = nextState.upperlimits[k]
                elif rr < nextState.lowerlimits[k]:
                    rr = nextState.lowerlimits[k]
                if self.objProblem.typeState == "MIX" and nextState.typeVarMix[k] =="integer":
                    rr = int(rr)    
                nextState.setValue(k, rr)    
            self.objProblem.evaluate(nextState)
            self.objProblem.counter.incCount()
            # verificar si esta solución ya está dentro de la población    
            popTemp.addSort(nextState, True)     
        
      
    
    # no es identica al original, solo selecciona los mejores
    def selectionStrategy2(self, popTemp, popTx):      
        for i in range(self.popul.popSize - 1):
            popTx.addSort(popTemp.getIndividual(i), True) 
            
        for i in range(self.popul.popSize):
            popTx.addSort(self.popul.getIndividual(i))   
            
        return popTx 
    
    
    def selectionStrategy(self, sparks, popTx):    
    
    	# this parameter avoids the division by zero
        e = 0.001 

        # tipo roulette  
        for i in range(self.popul.popSize):
            sparks.addSort(self.popul.getIndividual(i), True)  
        sparks.removeIndividual(0)
        
    	# print(sparks.popSize)            
    	# print(popTx.popSize) 
        prob = np.zeros(sparks.popSize )  
        total = 0 
        
        worst = sparks.getIndividual(sparks.popSize - 1).fitness
        sumx = 0
        for j in range(sparks.popSize):
    	    sumx = sumx + math.fabs(worst - sparks.getIndividual(j).fitness)
        sumx = sumx + e
        
        for j in range(sparks.popSize): 
        	prob[j]  = (math.fabs(worst - sparks.getIndividual(j).fitness) + e)/sumx 
        	total = total + prob[j]  
     
        while popTx.popSize < self.popul.popSize :
            sumx = 0 
            rnd = np.random.rand()*total 
            
            for s in range(sparks.popSize): 
            	if sumx > rnd :
            		popTx.addSort(sparks.getIndividual(s), True)   
            		break 
            	sumx = sumx + prob[s]  
            
        return popTx 
    
    
    def fireworksAlgorithmPerm(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
    	if solution != None :
    		self.popul.addSort(solution)		
        
    	self.popul.printFitness("POP(INI)")  
    	popTx = Population(0, self.objProblem)
 
    	while self.isStopCriteria():  
    		s = self.nSparksPerm() 
    		# print(s )
    		a = self.amplitudesPerm() 
    		# print(a )            
    		sparks = self.displacementPerm(s, a)
    		self.gaussianMutationPerm(sparks)
    		popTx.addSort(sparks.getIndividual(0), True)
    		# print()      
    		# print(sparks.popSize)            
    		# print(popTx.popSize) 
    		# print(self.popul.popSize)              
    		popTx = self.selectionStrategyPerm(sparks, popTx)
           
    		self.popul = copy.deepcopy(popTx)
    		popTx.removeAll()
			# sparks.removeAll() 
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)")  

        
    def nSparksPerm(self ):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	s = np.zeros(self.popul.popSize ) 
    	# this parameter avoids the division by zero
    	e = 0.001 
        
    	worst = self.popul.getIndividual(self.popul.popSize - 1).fitness
    	sumx = 0
    	for j in range(self.popul.popSize):
    	    sumx = sumx + math.fabs(worst - self.popul.getIndividual(j).fitness)
    	sumx = sumx + e
    	# print(sumx)         
    	for j in range(self.popul.popSize):   
            tmp = self.parameters.get('m')*(math.fabs(worst - self.popul.getIndividual(j).fitness) + e)/sumx
            if tmp  < self.parameters.get('m')*self.parameters.get('a'):
                val = round(self.parameters.get('m')*self.parameters.get('a')) 
            elif tmp > self.parameters.get('m')*self.parameters.get('a') and self.parameters.get('a') < self.parameters.get('b') and self.parameters.get('b') < 1:
                val = round(self.parameters.get('m')*self.parameters.get('b'))     
            else:
                # no tiene mucho sentido as defined by Tan_2015_Fireworks_Algorithm
                # val = round(self.parameters.get('m')*self.parameters.get('a')) 
                val = tmp               
            s[j] = int(val)    
    	return s          
    
    
    def amplitudesPerm(self ):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	a = np.zeros(self.popul.popSize )     
    	e = 0.001 
        
    	better = self.popul.getIndividual(0).fitness
    	sumx = 0
    	for j in range(self.popul.popSize):
            sumx = sumx + math.fabs(better - self.popul.getIndividual(j).fitness)
    	sumx = sumx + e
        
    	for j in range(self.popul.popSize):   
            a[j] = self.parameters.get('aprime')*(math.fabs(better - self.popul.getIndividual(j).fitness) + e)/sumx
              
    	return a     
    
    
    def displacementPerm (self, s, a):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	sparks = Population(0, self.objProblem)  
    	# print(s ) 
        
    	for i in range(self.popul.popSize):  
    	    for j in range(int(s[i])):
                nextState = copy.deepcopy(self.popul.getIndividual(i)) 
                for j in range(int(a[i])):
                    nextState = self.objProblem.op.mutation('SWAPPING', [nextState])  
                    
                self.objProblem.evaluate(nextState)
                self.objProblem.counter.incCount()
                # verificar si esta solución ya está dentro de la población    
                sparks.addSort(nextState, True)
    	return sparks       
    
    
    
    def gaussianMutationPerm(self, sparks):
        # definir como parametro
    	self.gaussian = int(self.popul.popSize*0.5) 
    	for i in range(self.gaussian):
            d = np.random.randint(self.popul.popSize)
            nextState = copy.deepcopy(self.popul.getIndividual(d)) 
            nextState = self.objProblem.op.mutation('SWAPPING', [nextState])
            # deberia ser blocking
            # nextState = self.objProblem.op.mutation('SWAPPING', [nextState])  
            
            self.objProblem.evaluate(nextState)
            self.objProblem.counter.incCount()
            # verificar si esta solución ya está dentro de la población    
            sparks.addSort(nextState, True)     
        
      
    # no es identica al original, solo selecciona los mejores
# =============================================================================
#     def selectionStrategyPerm(self, popTemp, popTx):      
#         for i in range(self.popul.popSize - 1):
#             popTx.addSort(popTemp.getIndividual(i), True) 
#             
#         for i in range(self.popul.popSize):
#             popTx.addSort(self.popul.getIndividual(i))   
#             
#         return popTx         
# =============================================================================
    
    
    def selectionStrategyPerm(self, sparks, popTx):      
    	# this parameter avoids the division by zero
    	e = 0.001 

        # tipo roulette  
    	for i in range(self.popul.popSize):
            sparks.addSort(self.popul.getIndividual(i), True)  
    	sparks.removeIndividual(0)
        
    	# print(sparks.popSize)            
    	# print(popTx.popSize) 
    	prob = np.zeros(sparks.popSize )  
    	total = 0 
        
    	worst = sparks.getIndividual(sparks.popSize - 1).fitness
    	sumx = 0
    	for j in range(sparks.popSize):
    	    sumx = sumx + math.fabs(worst - sparks.getIndividual(j).fitness)
    	sumx = sumx + e
        
    	for j in range(sparks.popSize): 
    		prob[j]  = (math.fabs(worst - sparks.getIndividual(j).fitness) + e)/sumx 
    		total = total + prob[j]  
     
    	while popTx.popSize < self.popul.popSize :
    	    sumx = 0 
    	    rnd = np.random.rand()*total 
            
    	    for s in range(sparks.popSize): 
    	    	if sumx > rnd :
    	    		popTx.addSort(sparks.getIndividual(s), True)   
    	    		break 
    	    	sumx = sumx + prob[s]  
            
    	return popTx  
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 14:04:18 2020

@author: tauger
"""

from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import * 

import numpy as np
import math 
import copy


class CrossEntropy(Heuristic):	    
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
		
    	self.shortTerm  = "CE"
    	self.objProblem = problem  
        
    	self.setParameters(fileConfig)
# =============================================================================
#     	self.popul = Population(self.parameters.get('samples'), self.objProblem, self.parameters.get('initialTypeSolution'))
#     	self.popul.sort()
#     	self.objProblem.counter.incCount(self.parameters.get('samples'))
# =============================================================================
		
# =============================================================================
#     	self.status.stateInitial = self.popul.getBetterSort()
#     	self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
# =============================================================================
        
        # Sólo están implementadas las versiones tipo bin  quedaría por definir 
        # las variables tipo exp 
    	if  run == True :
			# if  self.parameters.get('version') == "STEADY" :
			# 	self.geneticAlgorithm(self.status.stateFinal)
			# else:
			# 	self.geneticAlgorithmGen(self.status.stateFinal)
    		if  self.parameters.get('version') == "BASIC" :
    		    if  self.objProblem.typeState == "PERMUTATIONAL" :
    		        self.crossEntropyPerm(self.status.stateFinal)
    		    elif  self.objProblem.typeState == "BINARY" :
    		        self.crossEntropyBin(self.status.stateFinal)    
    		    else :
    		        self.crossEntropy(self.status.stateFinal)                     
    		elif  self.parameters.get('version') == "MULTIPLE" :
    		    if  self.objProblem.typeState == "PERMUTATIONAL" :
    		        self.crossEntropyMultiplePerm(self.status.stateFinal)
    		    elif  self.objProblem.typeState == "BINARY" :
    		        self.crossEntropyMultipleBin(self.status.stateFinal)      		        
    		    else :
    		        # self.crossEntropyMultiple(self.status.stateFinal)	  
    		        pass
        
        
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
    	for i in range(8): # (int i = 0 i < nameParameters.size() i++) :

    		if not 'initialTypeSolution' in self.parameters : 
    			self.parameters.update(dict(initialTypeSolution="RANDOM"))	
							
    		if not 'samples' in self.parameters :  # 'individuals'
    			self.parameters.update(dict(samples=60))
				
    		if not 'version' in self.parameters :
    			self.parameters.update(dict(version="BASIC"))  
								
    		if not 'rho' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(rho=0.01))
					
    		if not 'alpha' in self.parameters :  # weightfactor
    			self.parameters.update(dict(alpha=1)) 
                
    		if not 'fpop' in self.parameters :  # crossoverfactor
     			self.parameters.update(dict(fpop=2))
 					
    		if not 'nmulti' in self.parameters :  # weightfactor
     			self.parameters.update(dict(nmulti=4)) 	 
 					
    		if not 'typemulti' in self.parameters :  # weightfactor
     			self.parameters.update(dict(typemulti="DISJOINT")) 	                  
            # typeMultiple = "DISJOINT"  // Options=DISJOINT,ELITISM    
    	print(self.parameters)   
		
		
    def crossEntropy(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
# =============================================================================
#     	if solution != None :
#     		self.popul.addSort(solution)		
# =============================================================================
        
    	# self.popul.printFitness("POP(INI)")    
        
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('rho'))
    	prob = self.getMatrix() 
    	print(self.elite)         
# =============================================================================
#     	m = -2 + 4*np.random.randint(self.objProblem.nVar)
#     	mlast = m 
#     	problast = prob
#     	t = 1
#     	q = 6
# =============================================================================
        
    	while self.isStopCriteria():  
            # print("---------------")             
# =============================================================================
#             m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
#             bmod = beta - beta*(1 - 1/t)**q 
# =============================================================================
            self.popul = self.getPopulation(prob) # se debe ordenar
            self.popul.sort()
            prob = self.updateProb(prob)  
            # print(prob)            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)") 
             
        
    def crossEntropyMultiple(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
# =============================================================================
#     	if solution != None :
#     		self.popul.addSort(solution)		
# =============================================================================
        
    	# self.popul.printFitness("POP(INI)")    
        
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('rho'))
    	prob = self.getMatrix() 
        
 
    	while self.isStopCriteria():  
            
            self.popul = self.getPopulation(prob) # se debe ordenar
            self.popul.sort()
            prob = self.updateProb(prob)  
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)") 
    	self.popul.prints( ) 
                     
        
    def getMatrix(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
        
        #  means variances 
    	prob = np.zeros( (2, self.objProblem.nVar) )
    
    	for i in range(self.objProblem.nVar):  
    		media = self.objProblem.lowerlimits[i] +(self.objProblem.upperlimits[i] - self.objProblem.lowerlimits[i])/2
    		prob[0][i] = media + np.random.rand() * (self.objProblem.upperlimits[i] - self.objProblem.lowerlimits[i])/4    
    		prob[1][i] = np.random.rand() * (prob[0][i] - media)**2    
#  este código está asociado a la versión permutacional o combinatoria
# =============================================================================
#     	prob = np.zeros( (self.objProblem.nVar, self.objProblem.nVar) )
#     
#     	for i in range(self.objProblem.nVar): 
#     		for j in range(self.objProblem.nVar):
#     			if (not i == j):
#     				 prob[i][j] = 1 / (self.objProblem.nVar - 1)  
# =============================================================================
       
    	return prob         
             
        
    def getPopulation(self, prob):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
       
    	popTemp = Population(0, self.objProblem)  

    	for j in range(self.popSize): 
    		nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    		for i in range(nextState.nVar): 
    			ss = np.random.normal(prob[0][i], prob[1][i], 1) 
 
    			rr = self.objProblem.op.rounds(ss[0])   
    			#print(rr)                
                
    			if self.objProblem.typeState == "MIX" and nextState.typeVarMix[i] == "integer":
    				rr = int(rr) 
				# else :
				# 	rr = nextState.lowerlimits[j] - r*(nextState.upperlimits[j] - nextState.lowerlimits[j])
    			if rr > nextState.upperlimits[i]:
    				rr = nextState.upperlimits[i]
    			elif rr < nextState.lowerlimits[i]:
    				rr = nextState.lowerlimits[i]
                 
    			nextState.setValue(i, rr) 
                
    		self.objProblem.evaluate(nextState)
    		self.objProblem.counter.incCount()	
    		popTemp.addSort(nextState, True)	
            
#  este código está asociado a la versión permutacional o combinatoria            
# =============================================================================
#             nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
#             self.objProblem.evaluate(nextState)
#             self.objProblem.counter.incCount()
#  
#             popTemp.addSort(nextState, True)
# =============================================================================
		 
    	return popTemp	
    

    def updateProb(self, prob):
		
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	probtemp = np.zeros( (2, self.objProblem.nVar) )
    	temp = np.zeros( (2, self.objProblem.nVar) )
		# m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
		# bmod = beta - beta*(1 - 1/t)**q     	
		
    	nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    	
    	for i in range(nextState.nVar): 
    		sumx  = 0
    		for j in range( self.elite ): 
    			sumx = sumx  + self.popul.getIndividual(j).getValue(i)
    		temp[0][i] = sumx / self.elite 
			
    		sumx  = 0
    		for j in range( self.elite ): 
    			sumx = sumx  + (self.popul.getIndividual(j).getValue(i)- temp[0][i] )**2
    		temp[1][i] = sumx / self.elite
    		# print(temp[1][i])
    		# print(prob[1][i])
    		# print(self.elite)
    		# print(self.parameters.get('alpha'))
    		probtemp[0][i] = self.parameters.get('alpha')*temp[0][i]  + (1 - self.parameters.get('alpha'))*prob[0][i]
    		probtemp[1][i] = self.parameters.get('alpha')*temp[1][i]  + (1 - self.parameters.get('alpha'))*prob[1][i]	
    		# print(probtemp[1][i])  
    	# print(probtemp) 
    	# print(".......")    
    	return probtemp	
    
    
    def updateProbBin(self, prob):
		
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	npdf = 1
    	if  self.parameters.get('version') == "MULTIPLE" :
    		npdf = self.parameters.get('nmulti')
    	# popTemp = Population(0, self.objProblem)
    	
    	probtemp = np.zeros( (npdf, self.objProblem.nVar) )
    	#temp = np.zeros( (npdf, self.objProblem.nVar) )
		# m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
		# bmod = beta - beta*(1 - 1/t)**q     	
    	# print(probtemp)
    	# print(prob)    	
    	# self.popul.prints() 
    	nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
 
    	for v in range(npdf): 
    		for i in range(nextState.nVar): 
    			sumx  = 0
    			for j in range( self.elite ): 
    				if (self.popul.getIndividual(j).getValue(i) == 1):
    					sumx = sumx  +  1
    			temp = sumx / self.elite
    			# print(temp[1][i])
    			# print(prob[1][i])
    			# print(self.elite)
    			# print(self.parameters.get('alpha'))
    			probtemp[v][i] = prob[v][i]*self.parameters.get('alpha') + (temp*(1-self.parameters.get('alpha')))
    			 
    			# print(probtemp[1][i])  
    	# print(probtemp) 
    	# print(".......")    
    	return probtemp	
    	    	
    
    def crossEntropyPerm(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
# =============================================================================
#     	if solution != None :
#     		self.popul.addSort(solution)		
# =============================================================================
        
    	# self.popul.printFitness("POP(INI)")    
        
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('rho'))
    	prob = self.getMatrixPerm() 
        
    	while self.isStopCriteria():  
# =============================================================================
#             m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
#             bmod = beta - beta*(1 - 1/t)**q 
# =============================================================================
            self.popul = self.getPopulationPerm(prob) # se debe ordenar
            self.popul.sort()
            prob = self.updateProb(prob)  
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)") 
             
             
    def crossEntropyBin(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
        
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('rho'))
    	prob = self.getMatrixBin() 
    	print(prob)
    	print(self.elite)   	
    	while self.isStopCriteria(): 
            print("-----------A-") 
            self.popul = self.getPopulationBin(prob) # se debe ordenar
            # print("-----------G-")
            self.popul.sort()
            # print("-----------R-")
            print(prob)
            prob = self.updateProbBin(prob) 
            print(prob)
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)")    
    	# self.popul.prints()     	          
                     
        
    def getMatrixPerm(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
        
        #  means variances 
    	prob = np.zeros( (self.objProblem.nVar, self.objProblem.nVar) )
        
    	for i in range(self.objProblem.nVar): 
    		for j in range(self.objProblem.nVar):
    			if (not i == j):
    				 prob[i][j] = 1 / (self.objProblem.nVar - 1)      
    	 
    	return prob                  	
    	
    	
    def getMatrixBin(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	npdf = 1
    	if  self.parameters.get('version') == "MULTIPLE" :
    		npdf = self.parameters.get('nmulti')
        #  means variances 
    	prob = np.zeros( (npdf, self.objProblem.nVar) )
        
    	for i in range(npdf): 
    		for j in range(self.objProblem.nVar):
    			# if (not i == j):
    			# 	 prob[i][j] = 1 / (self.objProblem.nVar - 1    
    			prob[i][j] = 0.5    	 
    	return prob    	


    def getPopulationPerm(self, prob):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
       
    	popTemp = Population(0, self.objProblem)  
    	
    	for i in range(self.popSize):  
    		vSolution = np.zeros( self.objProblem.nVar )
    		init = np.random.randint(self.objProblem.nVar)
    		vSolution[0] = init 
			
    		S = np.zeros( self.objProblem.nVar )
    		S[init]= 1 
    		t = 1
    		v = init 

    		while(t < self.objProblem.nVar): #  n -1
    			sumx = 0  	
    			for z in range(self.objProblem.nVar):  
    				sumx = sumx + (1 - S[z])*prob[v][z] 

    			norm = sumx 		
    			u = np.random.rand()*norm 		
    			sumx = 0.0 
    			k = -1 

    			while (sumx < u and k < (self.objProblem.nVar - 1)):
    				k = k + 1
    				if (S[k]==0):
    					sumx = sumx + prob[v][k]  

    			if (norm == 0.0): 
    				for ycs in range(self.objProblem.nVar):   
    					if (S[ycs] == 0):
    						k = ycs 
    						break  

    			if (k != -1):
    				vSolution[t] = k 
    				S[k] = 1 
    				v = k 
    				t = t + 1  
	 
    		nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    		nextState.setValues(vSolution)
    		self.objProblem.evaluate(nextState)
    		self.objProblem.counter.incCount()
 
    		popTemp.addSort(nextState, True)
            
    	return popTemp   
    
    
	# Revisar el número máximo di soluciones por cada
    def getPopulationBin(self, prob):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	r = 0
    	npdf = 1
    	if  self.parameters.get('version') == "MULTIPLE" :
    		npdf = self.parameters.get('nmulti')  
    	vpdf = np.zeros(npdf)	     
    	for y in range(npdf):   
    		vpdf[y] = self.popSize//npdf
    		
    		r = r + vpdf[y] 
    	if (r < self.popSize):
    		vpdf[0]= vpdf[0] + (self.popSize - r)
    	
    	# Crea una población aleatoria de tamaño self.popSize
    	popTemp = Population(self.popSize, self.objProblem)  
    	for h in range(len(vpdf)):   
    		i = 0 
    		# print(i)  
    		# print(h )  
    		while(i < vpdf[h]):    		     	
    	
    			vSolution = np.zeros( self.objProblem.nVar ) 
    			init = 0
    			for g in range(self.objProblem.nVar):
                    
    				init = np.random.rand()
    				if (init >= prob[npdf-1][g]):
    					vSolution[g] = -1
    				else:
    					vSolution[g] = 1 

	 
    			nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    			nextState.setValues(vSolution)
    			self.objProblem.evaluate(nextState)
    			self.objProblem.counter.incCount()
 
    			popTemp.addSort(nextState, True)
    			i = i + 1 
# =============================================================================
#     			if (not popTemp.contains(nextState)):
#     				popTemp.addSort(nextState) 
#     				i = i + 1 
# =============================================================================
    	return popTemp    
    

    def updateProbPerm(self, prob):
		
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	probtemp = np.zeros( (self.objProblem.nVar, self.objProblem.nVar) )
    	
    	for j in range( self.elite ):   
    		for z in range(self.objProblem.nVar - 1): 
    			one = self.popul.getIndividual(j).getValue(z)  
    			two = self.popul.getIndividual(j).getValue(z+1)  
    			probtemp[one][two] = probtemp[one][two] + (1/self.elite);
				 
    		thr = self.popul.getIndividual(j).getValue(self.objProblem.nVar - 1) 
			
    		for y in range(self.objProblem.nVar): 	  
    			if (thr != y): 
    				probtemp[thr][y] = probtemp[thr][y] + (1/(self.elite*(self.objProblem.nVar - 1))) 
 
    	return probtemp	
    	
    	
    def crossEntropyMultiplePerm(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	print("zzz")            				
# =============================================================================
#     	if solution != None :
#     		self.popul.addSort(solution)		
# =============================================================================
        
    	# self.popul.printFitness("POP(INI)")    
        
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('rho'))
    	# print("ddd")
    	prob = self.getMatrixMultiplePerm() 
        
    	while self.isStopCriteria():  
            # print(prob )            
# =============================================================================
#             m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
#             bmod = beta - beta*(1 - 1/t)**q 
# =============================================================================
            self.popul = self.getPopulationMultiplePerm(prob) # se debe ordenar
            # print("ccc")
            self.popul.sort()
            # print("vvv")
            prob = self.updateProbMultiplePerm(prob)  
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)") 
                     
                     
    def crossEntropyMultipleBin(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
        
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('rho'))
    	# print("ddd")
    	prob = self.getMatrixBin() 
    	# print(prob)
    	print(self.elite)  
    	print(self.popSize)    	
    	while self.isStopCriteria():  
            self.popul = self.getPopulationBin(prob) # se debe ordenar
            # print("ccc")
            self.popul.sort()
            # print("vvv")
            prob = self.updateProbBin(prob)  
            
    	self.status.stateFinal = self.popul.getIndividual(0)  
    	self.popul.printFitness("POP(FIN)")                      
                     
        
    def getMatrixMultiplePerm(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
        
        #  means variances 
    	prob = np.zeros( (self.parameters.get('nmulti'), self.objProblem.nVar, self.objProblem.nVar) )
    	for h in range(self.parameters.get('nmulti')):        
    		for i in range(self.objProblem.nVar): 
    			for j in range(self.objProblem.nVar):
    				if (not i == j):
    					prob[h][i][j] = 1 / (self.objProblem.nVar - 1)      
    	 
    	return prob     


    def getPopulationMultiplePerm(self, prob):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
       
    	popTemp = Population(0, self.objProblem)  
        
    	r = 0 
    	g = np.zeros( self.parameters.get('nmulti') )
    	for y in range(self.parameters.get('nmulti')):   
    		g[y] = self.popSize//self.parameters.get('nmulti')
    		r = r + g[y] 
    	if (r < self.popSize):
    		g[0]= g[0] + (self.popSize - r) 
    	# print(g)            
    	for h in range(self.parameters.get('nmulti')):   
    		i = 0 
    		# print(i)  
    		# print(h )            
    		while(i < g[h]):	 
    			# print(h)  
    			vSolution = np.zeros( self.objProblem.nVar )
    			init = np.random.randint(self.objProblem.nVar )
                 
    			vSolution[0] = init 
			
    			S = np.zeros( self.objProblem.nVar )
    			S[init]= 1 
    			t = 1
    			v = init 

    			while(t < self.objProblem.nVar): #  n -1
    				sumx = 0  	
    				for z in range(self.objProblem.nVar):  
    					sumx = sumx + (1 - S[z])*prob[h][v][z] 

    				dnorm = sumx 		
    				u = np.random.rand()*dnorm 		
    				sumx = 0.0 
    				k = -1 

    				while (sumx < u and k < (self.objProblem.nVar - 1)):
    					k = k + 1
    					if (S[k]==0):
    						sumx = sumx + prob[h][v][k]  

    				if (dnorm == 0.0): 
    					for ycs in range(self.objProblem.nVar):   
    						if (S[ycs] == 0):
    							k = ycs 
    							break  

    				if (k != -1):
    					vSolution[t] = k 
    					S[k] = 1 
    					v = k 
    					t = t + 1  
	 
    			nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    			nextState.setValues(vSolution)
    			self.objProblem.evaluate(nextState)
    			self.objProblem.counter.incCount()
                # verificar si esta solución ya está dentro de la población    
    			popTemp.addSort(nextState, True)
    			i = i + 1  
    	return popTemp   
    
    
    def updateProbMultiplePerm(self, prob):
		
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	probtemp = np.zeros( (self.parameters.get('nmulti'), self.objProblem.nVar, self.objProblem.nVar) )
    	
    	for h in range(self.parameters.get('nmulti')): 
    		for j in range( self.elite ):   
    			for z in range(self.objProblem.nVar - 1): 
    				if  self.parameters.get('typemulti') == "DISJOINT" :
    					one = int(self.popul.getIndividual(self.parameters.get('nmulti')*j+h).getValue(z) ) 
    					two = int(self.popul.getIndividual(self.parameters.get('nmulti')*j+h).getValue(z+1) ) 
    				else : 
    					one = int(self.popul.getIndividual(j*(h+1)).getValue(z) ) 
    					two = int(self.popul.getIndividual(j*(h+1)).getValue(z+1) )  
					
    				probtemp[h][one][two] = probtemp[h][one][two] + (1/self.elite);
				 
    			thr = int(self.popul.getIndividual(j).getValue(self.objProblem.nVar - 1) )
			
    			for y in range(self.objProblem.nVar): 	  
    				if (thr != y):
    					probtemp[h][thr][y] = probtemp[h][thr][y] + (1/(self.elite*(self.objProblem.nVar - 1))) 
 
    	return probtemp	
    	
    	
    
    	

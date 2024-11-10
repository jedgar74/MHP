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

class CooperativeCrossEntropy(Heuristic):	    
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
		
    	self.shortTerm  = "CCE"
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
    		        # self.cooperativeCrossEntropyPerm(self.status.stateFinal)
    		        pass
    		    elif  self.objProblem.typeState == "BINARY" :
    		        print("BINARY")  
    		        self.cooperativeCrossEntropyBin(self.status.stateFinal)    
    		    else :
    		        # self.cooperativeCrossEntropy(self.status.stateFinal)   
    		         pass
#    		elif  self.parameters.get('version') == "MULTIPLE" :
#    		    if  self.objProblem.typeState == "PERMUTATIONAL" :
#    		        self.cooperativeCrossEntropyMultiplePerm(self.status.stateFinal)
#    		    elif  self.objProblem.typeState == "BINARY" :
#    		        self.cooperativeCrossEntropyMultipleBin(self.status.stateFinal)      		        
#    		    else :
#    		        # self.cooperativeCrossEntropyMultiple(self.status.stateFinal)	  
#    		        pass
        
        
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
#    	else:
#    		if sol == None :
#    			self.geneticAlgorithmGen()
#    		else :
#    			self.geneticAlgorithmGen(sol)
            

    def setParameters(self, fileConfig):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
  
    	self.parameters = self.readParameters(fileConfig, self.shortTerm)
		# print(self.parameters)
    	for i in range(9): # (int i = 0 i < nameParameters.size() i++) :

    		if not 'initialTypeSolution' in self.parameters : 
    			self.parameters.update(dict(initialTypeSolution="RANDOM"))	
							
    		# if not 'samples' in self.parameters :  # 'individuals'
    		# 	self.parameters.update(dict(samples=60))
				
    		if not 'version' in self.parameters :
    			self.parameters.update(dict(version="BASIC"))  
								
    		if not 'minrho' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(minrho=0.01))
                
    		if not 'maxrho' in self.parameters :  # crossoverfactor
    			self.parameters.update(dict(maxrho=0.02))                
					
    		if not 'alpha' in self.parameters :  # weightfactor
    			self.parameters.update(dict(alpha=0.6)) 
                
    		if not 'fpop' in self.parameters :  # crossoverfactor
     			self.parameters.update(dict(fpop=2))
                
    		if not 'ratioExchange' in self.parameters :  # crossoverfactor
     			self.parameters.update(dict(ratioExchange=0))
                 
    		if not 'instances' in self.parameters :
     			self.parameters.update(dict(instances=3))
#             if not 'nmulti' in self.parameters :  # weightfactor
#     			self.parameters.update(dict(nmulti=4)) 	 
# 					
#    		if not 'typemulti' in self.parameters :  # weightfactor
#     			self.parameters.update(dict(typemulti="DISJOINT")) 	                  
#            # typeMultiple = "DISJOINT"  // Options=DISJOINT,ELITISM    
    	print(self.parameters)   
		
		
#    def crossEntropy(self, solution = None):
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		""" 
#				
## =============================================================================
##     	if solution != None :
##     		self.popul.addSort(solution)		
## =============================================================================
#        
#    	# self.popul.printFitness("POP(INI)")    
#        
#    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
#    	self.elite = int(self.popSize*self.parameters.get('rho'))
#    	prob = self.getMatrix() 
## =============================================================================
##     	m = -2 + 4*np.random.randint(self.objProblem.nVar)
##     	mlast = m 
##     	problast = prob
##     	t = 1
##     	q = 6
## =============================================================================
#        
#    	while self.isStopCriteria():  
#            print("---------------")             
## =============================================================================
##             m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
##             bmod = beta - beta*(1 - 1/t)**q 
## =============================================================================
#            self.popul = self.getPopulation(prob) # se debe ordenar
#            self.popul.sort()
#            prob = self.updateProb(prob)  
#            # print(prob)            
#    	self.status.stateFinal = self.popul.getIndividual(0)  
#    	self.popul.printFitness("POP(FIN)") 
             
        

                     
        
#    def getMatrix(self):
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		""" 
#        
#        #  means variances 
#    	prob = np.zeros( (2, self.objProblem.nVar) )
#    
#    	for i in range(self.objProblem.nVar):  
#    		media = self.objProblem.lowerlimits[i] +(self.objProblem.upperlimits[i] - self.objProblem.lowerlimits[i])/2
#    		prob[0][i] = media + np.random.rand() * (self.objProblem.upperlimits[i] - self.objProblem.lowerlimits[i])/4    
#    		prob[1][i] = np.random.rand() * (prob[0][i] - media)**2    
##  este código está asociado a la versión permutacional o combinatoria
## =============================================================================
##     	prob = np.zeros( (self.objProblem.nVar, self.objProblem.nVar) )
##     
##     	for i in range(self.objProblem.nVar): 
##     		for j in range(self.objProblem.nVar):
##     			if (not i == j):
##     				 prob[i][j] = 1 / (self.objProblem.nVar - 1)  
## =============================================================================
#       
#    	return prob         
             
        
#    def getPopulation(self, prob):
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		"""  
#       
#    	popTemp = Population(0, self.objProblem)  
#
#    	for j in range(self.popSize): 
#    		nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
#    		for i in range(nextState.nVar): 
#    			ss = np.random.normal(prob[0][i], prob[1][i], 1) 
# 
#    			rr = self.objProblem.op.rounds(ss[0])   
#    			print(rr)                
#                
#    			if nextState.typeVarMix[i] == "integer":
#    				rr = int(rr) 
#				# else :
#				# 	rr = nextState.lowerlimits[j] - r*(nextState.upperlimits[j] - nextState.lowerlimits[j])
#    			if rr > nextState.upperlimits[i]:
#    				rr = nextState.upperlimits[i]
#    			elif rr < nextState.lowerlimits[i]:
#    				rr = nextState.lowerlimits[i]
#                 
#    			nextState.setValue(i, rr) 
#                
#    		self.objProblem.evaluate(nextState)
#    		self.objProblem.counter.incCount()	
#    		popTemp.addSort(nextState, True)	
#            
##  este código está asociado a la versión permutacional o combinatoria            
## =============================================================================
##             nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
##             self.objProblem.evaluate(nextState)
##             self.objProblem.counter.incCount()
##  
##             popTemp.addSort(nextState, True)
## =============================================================================
#		 
#    	return popTemp	
    

#    def updateProb(self, prob):
#		
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		""" 
#    	probtemp = np.zeros( (2, self.objProblem.nVar) )
#    	temp = np.zeros( (2, self.objProblem.nVar) )
#		# m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
#		# bmod = beta - beta*(1 - 1/t)**q     	
#		
#    	nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
#    	
#    	for i in range(nextState.nVar): 
#    		sumx  = 0
#    		for j in range( self.elite ): 
#    			sumx = sumx  + self.popul.getIndividual(j).getValue(i)
#    		temp[0][i] = sumx / self.elite 
#			
#    		sumx  = 0
#    		for j in range( self.elite ): 
#    			sumx = sumx  + (self.popul.getIndividual(j).getValue(i)- temp[0][i] )**2
#    		temp[1][i] = sumx / self.elite
#    		# print(temp[1][i])
#    		# print(prob[1][i])
#    		# print(self.elite)
#    		# print(self.parameters.get('alpha'))
#    		probtemp[0][i] = self.parameters.get('alpha')*temp[0][i]  + (1 - self.parameters.get('alpha'))*prob[0][i]
#    		probtemp[1][i] = self.parameters.get('alpha')*temp[1][i]  + (1 - self.parameters.get('alpha'))*prob[1][i]	
#    		# print(probtemp[1][i])  
#    	# print(probtemp) 
#    	# print(".......")    
#    	return probtemp	
#    	

    	    	
#    def crossEntropyPerm(self, solution = None):
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		""" 
#				
## =============================================================================
##     	if solution != None :
##     		self.popul.addSort(solution)		
## =============================================================================
#        
#    	# self.popul.printFitness("POP(INI)")    
#        
#    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
#    	self.elite = int(self.popSize*self.parameters.get('rho'))
#    	prob = self.getMatrixPerm() 
#        
#    	while self.isStopCriteria():  
## =============================================================================
##             m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
##             bmod = beta - beta*(1 - 1/t)**q 
## =============================================================================
#            self.popul = self.getPopulationPerm(prob) # se debe ordenar
#            self.popul.sort()
#            prob = self.updateProb(prob)  
#            
#    	self.status.stateFinal = self.popul.getIndividual(0)  
#    	self.popul.printFitness("POP(FIN)") 
             
             

    	      
        
#    def getMatrixPerm(self):
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		""" 
#        
#        #  means variances 
#    	prob = np.zeros( (self.objProblem.nVar, self.objProblem.nVar) )
#        
#    	for i in range(self.objProblem.nVar): 
#    		for j in range(self.objProblem.nVar):
#    			if (not i == j):
#    				 prob[i][j] = 1 / (self.objProblem.nVar - 1)      
#    	 
#    	return prob                  	
    	
    	

#    def getPopulationPerm(self, prob):
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		"""  
#       
#    	popTemp = Population(0, self.objProblem)  
#    	
#    	for i in range(self.popSize):  
#    		vSolution = np.zeros( self.objProblem.nVar )
#    		init = np.random.randint(self.objProblem.nVar)
#    		vSolution[0] = init 
#			
#    		S = np.zeros( self.objProblem.nVar )
#    		S[init]= 1 
#    		t = 1
#    		v = init 
#
#    		while(t < self.objProblem.nVar): #  n -1
#    			sumx = 0  	
#    			for z in range(self.objProblem.nVar):  
#    				sumx = sumx + (1 - S[z])*prob[v][z] 
#
#    			norm = sumx 		
#    			u = np.random.rand()*norm 		
#    			sumx = 0.0 
#    			k = -1 
#
#    			while (sumx < u and k < (self.objProblem.nVar - 1)):
#    				k = k + 1
#    				if (S[k]==0):
#    					sumx = sumx + prob[v][k]  
#
#    			if (norm == 0.0): 
#    				for ycs in range(self.objProblem.nVar):   
#    					if (S[ycs] == 0):
#    						k = ycs 
#    						break  
#
#    			if (k != -1):
#    				vSolution[t] = k 
#    				S[k] = 1 
#    				v = k 
#    				t = t + 1  
#	 
#    		nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
#    		nextState.setValues(vSolution)
#    		self.objProblem.evaluate(nextState)
#    		self.objProblem.counter.incCount()
# 
#    		popTemp.addSort(nextState, True)
#            
#    	return popTemp   
    

#    def updateProbPerm(self, prob):
#		
#    	""" 
#		@param problem.Problem _problem : 
#		@return  :
#		@author
#		""" 
#    	probtemp = np.zeros( (self.objProblem.nVar, self.objProblem.nVar) )
#    	
#    	for j in range( self.elite ):   
#    		for z in range(self.objProblem.nVar - 1): 
#    			one = self.popul.getIndividual(j).getValue(z)  
#    			two = self.popul.getIndividual(j).getValue(z+1)  
#    			probtemp[one][two] = probtemp[one][two] + (1/self.elite)
#				 
#    		thr = self.popul.getIndividual(j).getValue(self.objProblem.nVar - 1) 
#			
#    		for y in range(self.objProblem.nVar): 	  
#    			if (thr != y): 
#    				probtemp[thr][y] = probtemp[thr][y] + (1/(self.elite*(self.objProblem.nVar - 1))) 
# 
#    	return probtemp	
    	
    	
    def vRho(self):  
    	self.vrhos = np.zeros(self.parameters.get('instances') )
    	self.vrhos[0] = self.parameters.get('minrho')

    	for t in range(1, self.parameters.get('instances')): 
    		self.vrhos[t] = self.vrhos[t-1] + ((self.parameters.get('maxrho') - self.parameters.get('minrho'))/(self.parameters.get('instances')  -1))
		
				
		

				
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
                                                            
    def cooperativeCrossEntropyBin(self, solution = None):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 

    	self.vRho() 
    	# print(self.vrhos)    	        
		
    	self.popSize = int(self.parameters.get('fpop')*(self.objProblem.nVar**2))
    	self.elite = int(self.popSize*self.parameters.get('minrho'))
    	prob = self.getMatrixBin() 
    	# print(prob)
    	# print(self.elite)   	
        
    	while self.isStopCriteria(): 
            # print("-----------A-") 
            # self.popul = 
            self.getPopulationBin(prob) # se debe ordenar
            # print("-----------G-")
            # self.popul.sort()
            # print("-----------R-")
            # print(prob)
            self.exchange() 
            self.sorted()
            # self.printr()
            self.status.stateFinal = self.getBetterSolution()
            prob = self.updateProbBin(prob) 
            # print(prob)
            
    	self.status.stateFinal = self.getBetterSolution()  
    	# self.popul.printFitness("POP(FIN)")    
    	# self.popul.prints()     	          
      
        
    def getMatrixBin(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	
        #  means variances 
    	prob = np.zeros( (self.parameters.get('instances'), self.objProblem.nVar) )
        
    	for i in range(self.parameters.get('instances')): 
    		for j in range(self.objProblem.nVar):
    			# if (not i == j):
    			# 	 prob[i][j] = 1 / (self.objProblem.nVar - 1    
    			prob[i][j] = 0.5    	 
    	return prob    	


	# Revisar el número máximo di soluciones por cada
    def getPopulationBin(self, prob):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""  
    	# fixed = int(self.popSize * self.parameters.get('ratioExchange') )
    	fixed = int(self.popSize * 1 )
    	self.vpop = []	     
   
    	
    	# Crea una población aleatoria de tamaño self.popSize
    	 
    	for h in range(self.parameters.get('instances')):   

    		popTemp = Population(fixed, self.objProblem) 
    		# print(i)  
    		# print(h )  
    		i = 0             
    		while(i < fixed):    		     	
    	# for i in range(self.popSize):  
    			vSolution = np.zeros( self.objProblem.nVar )
    			
#    			vSolution[0] = init 
    			for g in range(self.objProblem.nVar):
    				init = np.random.rand()
    				if (init >= prob[h][g]):
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
    		self.vpop.append(popTemp) 
    	#return popTemp   
     
        
    def exchange(self) :
        
    	sizes = np.zeros(self.parameters.get('instances') ) 
    	exchanges = np.zeros(self.parameters.get('instances') ) 
		#Random rr = new Random()
    	total = 0 
    	for t in range( self.parameters.get('instances')):
    		sizes[t] = int(self.vrhos[t]*self.popSize) 
    		exchanges[t] = int(sizes[t]*self.parameters.get('ratioExchange'))
    		total = total + exchanges[t]
    	# print("---"+ str(total)  ) 
    	# print(sizes)    	
    	# print(exchanges)       	
    	dd = np.zeros(int(total))  
    	pp = []
		
    	f = 0
    	for t in range(self.parameters.get('instances')):
    		for z in range(int(exchanges[t])):
    			num = exchanges[t]//2
    			if (num <1):
    				num = 1 
    			e = np.random.randint(num)
				
    			pp.append(copy.deepcopy(self.vpop[t].getIndividual(e)))
    			dd[f] = t
    			f = f + 1 
	
    	for t in range(int(total)):
    		e = 0
    		while (True):
    			e = np.random.randint(self.parameters.get('instances'))
    			if (e != dd[t]):
    				break 
    				
    		if self.objProblem.op.isBetter([pp[t], self.vpop[e].getIndividual(int(sizes[e])-1)]):  
    			self.vpop[e].addSort(pp[t])			
    			#print("*** "+str(pp[t].fitness)+" "+str(self.vpop[e].getIndividual(int(sizes[e])-1).fitness)+" ***")
    		#if (pp.get(t).getFitnessOne() < pop.get(e).get(sizes[e]-1).getFitnessOne()):
    			#pop.get(e).addSort(pp.get(t))
				# System.out.println(" chg ::: t = "+t+" "+pp.get(t).getFitnessOne() +" z = "+sizes[e]  +" "+pop.get(e).get(sizes[e]-1).getFitnessOne())
			 
        
    def sorted(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	for v in range(self.parameters.get('instances')): 
    		self.vpop[v].sort()   

            
    def printr(self):
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
    	for v in range(self.parameters.get('instances')): 
    		print("*** "+str(v)+" "+str(self.vpop[v].getIndividual(0).fitness)+" ***")   
    	  
            
    def updateProbBin(self, prob):
		
    	""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
#    	npdf = 1
#    	if  self.parameters.get('version') == "MULTIPLE" :
#    		npdf = self.parameters.get('nmulti')
    	# popTemp = Population(0, self.objProblem)
    	
    	probtemp = np.zeros( (self.parameters.get('instances'), self.objProblem.nVar) )
    	#temp = np.zeros( (npdf, self.objProblem.nVar) )
		# m = self.parameters.get('alpha')*m  + (1-self.parameters.get('alpha'))*mlast
		# bmod = beta - beta*(1 - 1/t)**q     	
    	# print(probtemp)
    	# print(prob)    	
    	# self.popul.prints() 
    	nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    	# print('rhos') 
    	# print(self.vrhos)  
    	# print(self.popSize)       
        
    	for v in range(self.parameters.get('instances')): 
    		elite = int(self.popSize * self.vrhos[v]) 
    		if (elite == 0 ):
    			elite = 1
    		# print(elite)
    		for i in range(nextState.nVar): 
    			sumx  = 0 
    			for j in range( elite ): 
    				if (self.vpop[v].getIndividual(j).getValue(i) == 1):
    					sumx = sumx  +  1
    			temp = sumx / elite
    			# print(temp[1][i])
    			# print(prob[1][i])
    			# print(self.elite)
    			# print(self.parameters.get('alpha'))
    			probtemp[v][i] = prob[v][i]*self.parameters.get('alpha') + (temp*(1-self.parameters.get('alpha')))
    			
    			
    			# print(probtemp[1][i])  
    	# print(probtemp) 
    	# print(".......")    
    	return probtemp	    
    	
	    
    def getBetterSolution(self) :
        
    	nextState = Solution(self.objProblem, self.parameters.get('initialTypeSolution')) 
    	nextState = copy.deepcopy(self.vpop[0].getIndividual(0)) 
    	# self.vpop[0].printFitness("POP(FIN) 0")  
    	for v in range(1, self.parameters.get('instances')): 
    		if self.objProblem.op.isBetter([self.vpop[v].getIndividual(0), nextState]):  
    			nextState = copy.deepcopy(self.vpop[v].getIndividual(0))   
    		# self.vpop[v].printFitness("POP(FIN) "+str(v))   
    	return nextState	
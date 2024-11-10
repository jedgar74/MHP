# coding=UTF-8
from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import * 

import numpy as np
import math 
import copy
 

class DifferentialEvolution (Heuristic):

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

    # Hay que probar cada versión de forma individual
	def __init__(self, problem, fileConfig, run=True):
		""" 
		@param problem.Problem problem : 
		@param String _fileConfig : 
		@return  :
		@author
		"""
		super().__init__()
		
		self.shortTerm  = "DE"
		self.objProblem = problem 
		self.pairs = 1 
		self.kind = "BEST"  # "RAND"
        
		self.setParameters(fileConfig)
		self.popul = Population(self.parameters.get('individuals'), self.objProblem, self.parameters.get('initialTypeSolution'))
		self.popul.sort()
		self.objProblem.counter.incCount(self.parameters.get('individuals'))
		
		self.status.stateInitial = self.popul.getBetterSort()
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        
        # Sólo están implementadas las versiones tipo bin  quedaría por definir 
        # las variables tipo exp 
		if  run == True :
			# if  self.parameters.get('version') == "STEADY" :
			# 	self.geneticAlgorithm(self.status.stateFinal)
			# else:
			# 	self.geneticAlgorithmGen(self.status.stateFinal)
			print('VERSION: '+ self.parameters.get('version'))
			
				
			if  self.parameters.get('version') == "DE/BEST/1" or self.parameters.get('version') == "DE/BEST/2":
				if self.parameters.get('version') == "DE/BEST/2":  
					self.pairs = 2	  
				self.differentialEvolutionBest(self.status.stateFinal)      
				
			elif  self.parameters.get('version') == "DE/CUR-TO-BEST/1" or  self.parameters.get('version') == "DE/CUR-TO-BEST/2" :
				if self.parameters.get('version') == "DE/CUR-TO-BEST/2":  
					self.pairs = 2	   
				self.differentialEvolutionCurrentBest(self.status.stateFinal)   
				    
			elif  self.parameters.get('version') == "DE/CUR-TO-RAND/1" or self.parameters.get('version') == "DE/CUR-TO-RAND/2" :
				self.kind = "RAND"		
				if self.parameters.get('version') == "DE/CUR-TO-RAND/2":  
					self.pairs = 2		
				self.differentialEvolutionCurrentRandom(self.status.stateFinal)     
			elif  self.parameters.get('version') == "DE/RAND/2" or self.parameters.get('version') == "DE/RAND/1" :
				if self.parameters.get('version') == "DE/RAND/2":  
					self.pairs = 2	  
				self.kind = "RAND"	 
				if  self.objProblem.typeState == "BINARY" :
					self.differentialEvolutionBin(self.status.stateFinal)
				else : 
					self.differentialEvolution(self.status.stateFinal)                    
			else: 
				# this instruction allows throwing an exception
				raise ValueError("This version is not defined: "+self.parameters.get('version'))
				
                 


	def run(self, sol = None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		# Este código debe ser revisado y corregido
# =============================================================================
# 		if  self.parameters.get('version') == "STEADY" :
# 			if sol == None :
# 				self.geneticAlgorithm()
# 			else :
# 				self.geneticAlgorithm(sol)
# 		else:
# 			if sol == None :
# 				self.geneticAlgorithmGen()
# 			else :
# 				self.geneticAlgorithmGen(sol)
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
		for i in range(5): # (int i = 0 i < nameParameters.size() i++) {

			if not 'initialTypeSolution' in self.parameters : 
				self.parameters.update(dict(initialTypeSolution="RANDOM"))	
							
			if not 'individuals' in self.parameters :
				self.parameters.update(dict(individuals=10))
				
			if not 'version' in self.parameters :
				self.parameters.update(dict(version="DE/RAND/1"))  
								
			if not 'cr' in self.parameters :  # crossoverfactor
				self.parameters.update(dict(cr=0.9))
					
			if not 'fr' in self.parameters :  # weightfactor
				self.parameters.update(dict(fr=0.8)) 
	 	 
		# print(self.parameters) 
		
		
	def differentialEvolution(self, solution = None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
		if solution != None :
			self.popul.addSort(solution)		
        
		self.popul.printFitness("POP(INI)")    
		popTemp = Population(0, self.objProblem)
		nsolr = 1 + 2*self.pairs
 
		while self.isStopCriteria():  
			for i in range(self.parameters.get('individuals') ):  
				nextState = self.differential(i, nsolr)
				self.objProblem.evaluate(nextState)
				self.objProblem.counter.incCount()
				# nextState.prints("+++") 
				# self.popul.getIndividual(i).prints("---")    
				# print(self.objProblem.typeProblem) 
				if self.objProblem.op.isBetter([nextState, self.popul.getIndividual(i) ]):  
					popTemp.addSort(nextState, True)  
				else: 
					popTemp.addSort(self.popul.getIndividual(i), True)  							 
				#popTemp.printFitness("POP a") 			
			       
			self.popul = copy.deepcopy(popTemp)
			# self.popul.printFitness("POP(FIN)")
			popTemp.removeAll()   
			# popTemp.printFitness("POP c") 
            
		self.status.stateFinal = self.popul.getIndividual(0)  
		self.popul.printFitness("POP(FIN)") 
 

	def differential(self, index, nsolr, best = None):
		# indices = self.selection(index, 3) 
		indices = self.objProblem.op.indexRandom(index, nsolr, self.parameters.get('individuals'))        
		# corte = np.random.randint(self.objProblem.nVar)
		nextState = copy.deepcopy(self.popul.getIndividual(index))
		# nextState.prints()
		cut = np.random.randint(self.objProblem.nVar) 
		if best == None:
			inz = indices[1]	
		else: 
			inz = best	
			        
		for i in range(self.objProblem.nVar) :  
			# if corte == i and Rand[0, 1) < self.parameters.get('crossoverfactor'):  
		    if np.random.rand() < self.parameters.get('cr') or cut == i:    
		    		    	
		    	if self.objProblem.typeState == "MIX" and nextState.typeVarMix[i] == "integer":
		    		tmx = 0	
		    		for j in range(self.pairs) : 	    	                        
		    			tmx = tmx + self.popul.getIndividual(indices[2*(j+1)]).getValue(i) - self.popul.getIndividual(indices[2*(j+1)+1]).getValue(i)

		    		tmr = self.popul.getIndividual(inz).getValue(i) + self.parameters.get('fr')* tmx 
		    		nextState.setValue(i, int(tmr))  
		    	else:  
		    		tmx = 0	
		    		for j in range(self.pairs) : 	    	                        
		    			tmx = tmx + self.popul.getIndividual(indices[2*(j+1)]).getValue(i) - self.popul.getIndividual(indices[2*(j+1)+1]).getValue(i)

		    		tmx = self.popul.getIndividual(inz).getValue(i) + self.parameters.get('fr')* tmx                     
		    		nextState.setValue(i, tmx)     
		    	self.objProblem.op.insideLimits(nextState, i)
                
		return nextState	 
		

	def differentialEvolutionBest(self, solution = None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
		if solution != None :
			self.popul.addSort(solution)		
        
		self.popul.printFitness("POP(INI)")    
		popTemp = Population(0, self.objProblem)
		nsolr = 1 + 2*self.pairs 
 
		while self.isStopCriteria():   
			
			indexPop = popTemp.indexBetter() 
			for i in range(self.parameters.get('individuals') ):  
				R = self.differential(indexPop, nsolr)
				self.objProblem.evaluate(R)
				self.objProblem.counter.incCount()
				# R.prints("+++") 
				# self.popul.getIndividual(i).prints("---")    
				# print(self.objProblem.typeProblem) 
				if self.objProblem.op.isBetter([R, self.popul.getIndividual(i) ]):  
					popTemp.addSort(R, True)  
				else: 
					popTemp.addSort(self.popul.getIndividual(i), True)  							 
				#popTemp.printFitness("POP a") 			
			       
			self.popul = copy.deepcopy(popTemp)
			# self.popul.printFitness("POP(FIN)")
			popTemp.removeAll()   
			# popTemp.printFitness("POP c") 
            
		self.status.stateFinal = self.popul.getIndividual(0)  
		self.popul.printFitness("POP(FIN)") 
		

	def differentialEvolutionCurrent(self, solution = None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
		if solution != None :
			self.popul.addSort(solution)		
        
		self.popul.printFitness("POP(INI)")    
		popTemp = Population(0, self.objProblem)
		nsolr = 1 + 2*self.pairs 
 
		while self.isStopCriteria():   
			
			indexPop = popTemp.indexBetter() 
			for i in range(self.parameters.get('individuals')):  
				if self.kind == "BEST":
					R = self.differentialCurrent(i, nsolr, indexPop)
				else:
					R = self.differentialCurrent(i, nsolr)                    
				self.objProblem.evaluate(R)
				self.objProblem.counter.incCount()
				# R.prints("+++") 
				# self.popul.getIndividual(i).prints("---")    
				# print(self.objProblem.typeProblem) 
				if self.objProblem.op.isBetter([R, self.popul.getIndividual(i)]):  
					popTemp.addSort(R, True)  
				else: 
					popTemp.addSort(self.popul.getIndividual(i), True)  							 
				#popTemp.printFitness("POP a") 			
			       
			self.popul = copy.deepcopy(popTemp)
			# self.popul.printFitness("POP(FIN)")
			popTemp.removeAll()   
			# popTemp.printFitness("POP c") 
            
		self.status.stateFinal = self.popul.getIndividual(0)  
		self.popul.printFitness("POP(FIN)") 
		
		
	def differentialCurrent(self, index, nsolr, best = None):
		# indices = self.selection(index, 3) 
		indices = self.objProblem.op.indexRandom(index, nsolr, self.parameters.get('individuals'))        
		nextState = copy.deepcopy(self.popul.getIndividual(index))
		# nextState.prints()
		cut = np.random.randint(self.objProblem.nVar) 
		k = self.parameters.get('fr')
		if best == None:
			inz = indices[1]	
		else: 
			inz = best					
        
		for i in range(self.objProblem.nVar) :  
		   if nextState.typeVarMix[i] == "integer":
		    	tmx = 0	
		    	for j in range(self.pairs) : 	    	                        
		    		tmx = tmx + self.popul.getIndividual(indices[2*(j+1)]).getValue(i) - self.popul.getIndividual(indices[2*(j+1)+1]).getValue(i)

		    	tmr = self.popul.getIndividual(index).getValue(i) + k * (self.popul.getIndividual(inz).getValue(i) - self.popul.getIndividual(index)) + self.parameters.get('fr')* tmx                     
		    	nextState.setValue(i, int(tmr))  
		   else:  
		    	tmx = 0	
		    	for j in range(self.pairs) : 	    	                        
		    		tmx = tmx + self.popul.getIndividual(indices[2*(j+1)]).getValue(i) - self.popul.getIndividual(indices[2*(j+1)+1]).getValue(i)

		    	tmx = self.popul.getIndividual(index).getValue(i) + k * (self.popul.getIndividual(inz).getValue(i) - self.popul.getIndividual(index)) + self.parameters.get('fr')* tmx                     
		    	nextState.setValue(i, tmx)     
		   self.objProblem.op.insideLimits(nextState, i)
                
		return nextState
		
	def differentialEvolutionBin(self, solution = None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
				
		if solution != None :
			self.popul.addSort(solution)		
        
		self.popul.printFitness("POP(INI)")    
		popTemp = Population(0, self.objProblem)
		nsolr = 1 + 2*self.pairs
 
		while self.isStopCriteria():  
			for i in range(self.parameters.get('individuals') ):  
				nextState = self.differentialBin(i, nsolr)
				self.objProblem.evaluate(nextState)
				self.objProblem.counter.incCount()
				# nextState.prints("+++") 
				# self.popul.getIndividual(i).prints("---")    
				# print(self.objProblem.typeProblem) 
				if self.objProblem.op.isBetter([nextState, self.popul.getIndividual(i) ]):  
					popTemp.addSort(nextState, True)  
				else: 
					popTemp.addSort(self.popul.getIndividual(i), True)  							 
				#popTemp.printFitness("POP a") 			
			       
			self.popul = copy.deepcopy(popTemp)
			# self.popul.printFitness("POP(FIN)")
			popTemp.removeAll()   
			# popTemp.printFitness("POP c") 
            
		self.status.stateFinal = self.popul.getIndividual(0)  
		self.popul.printFitness("POP(FIN)") 


	def differentialBin(self, index, nsolr, best = None):
		# Wang et al._2010_A Modified Binary Differential Evolution Algorithm.pdf
        # indices = self.selection(index, 3) 
		indices = self.objProblem.op.indexRandom(index, nsolr, self.parameters.get('individuals'))        
		# corte = np.random.randint(self.objProblem.nVar)
		nextState = copy.deepcopy(self.popul.getIndividual(index))
		# nextState.prints()
		cut = np.random.randint(self.objProblem.nVar) 
		if best == None:
			inz = indices[1]	
		else: 
			inz = best	
		bc = 6
		 	        
		for i in range(self.objProblem.nVar) :  
			# if corte == i and Rand[0, 1) < self.parameters.get('crossoverfactor'):  
		    
			if np.random.rand() < self.parameters.get('cr') or cut == i:    
		    		    	
		    	
				tmx = 0	
				tmr = 0	
				for j in range(self.pairs) : 	    	                        
					tmx = tmx + self.popul.getIndividual(indices[2*(j+1)]).getValue(i) - self.popul.getIndividual(indices[2*(j+1)+1]).getValue(i)

				tmr = self.popul.getIndividual(inz).getValue(i) + self.parameters.get('fr')* tmx - 0.5
				tmc = 2*bc*tmr# /(1-2∗self.parameters.get('fr'))
		    	
				tmr = 1 /(math.exp(-tmc)+1)
				tmrb = 0	
				if np.random.rand() <= tmr:
					tmrb = 1
				else: 
					tmrb = -1	
				nextState.setValue(i, tmrb)  
		    	    
		    	# self.objProblem.op.insideLimits(nextState, i)
                
		return nextState	 
		




		  
# =============================================================================
# 	def selection(self, index, nsol):
# 		indices = [] # Z=np.zeros(4)
# 		indices.append(index) 
# 	 
# 		m = []
# 		for i in range(self.parameters.get('individuals')) :
# 		    if (i != index): 
# 		        m.append(i) 
#  
# 		for k in range(nsol) :
# 		    isol = np.random.randint(len(m))
# 		    indices.append(isol)
# 		    m.pop(isol) # m.remove(isol) 
# 		
# 		## print(indices	)
# 		 		 
# 		return indices	
# =============================================================================

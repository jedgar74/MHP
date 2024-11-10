# coding=UTF-8
from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import *

import math 
import copy

class MemeticAlgorithm (Heuristic):

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
		
		self.shortTerm  = "MA"
		self.objProblem = problem 
		 
		self.setParameters(fileConfig)
		self.popul = Population(self.parameters.get('individuals'), self.objProblem, self.parameters.get('initialTypeSolution'))
		self.popul.sort()
		self.objProblem.counter.incCount(self.parameters.get('individuals'))
		
		self.status.stateInitial = self.popul.getBetterSort()
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial)
        
		if  run==True :
			if  self.parameters.get('version') == "STEADY" :
				self.memeticAlgorithm(self.status.stateFinal)
			else:
				self.memeticAlgorithmGen(self.status.stateFinal)


	def run(self, sol=None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
		if  self.parameters.get('version') == "STEADY" :
			if sol==None :
				self.memeticAlgorithm()
			else :
				self.memeticAlgorithm(sol)
		else:
			if sol==None :
				self.memeticAlgorithmGen()
			else :
				self.memeticAlgorithmGen(sol)
            

	def setParameters(self, fileConfig):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
  
		self.parameters = self.readParameters(fileConfig, self.shortTerm)
		# print(self.parameters)
		for i in range(9): # (int i = 0 i < nameParameters.size() i++) {

			if not 'individuals' in self.parameters :
				self.parameters.update(dict(individuals=10))
				
			if not 'probcrossover' in self.parameters :
				self.parameters.update(dict(probcrossover=1))
					
			if not 'probmutation' in self.parameters :
				self.parameters.update(dict(probmutation=0.15))
				# ARITHMETIC
				
			if not 'version' in self.parameters :
				self.parameters.update(dict(version="STEADY")) 
				
			if not 'mutationoper' in self.parameters : 
				self.parameters.update(dict(mutationoper="BASIC2"))	
				 
			if not 'crossoveroper' in self.parameters : 
				self.parameters.update(dict(crossoveroper="BASIC"))	
                
			if not 'selectionoper' in self.parameters : 
				self.parameters.update(dict(selectionoper="ROULETTE"))	
					
			if not 'percElitism' in self.parameters : 
				self.parameters.update(dict(percElitism=0))	
					
			if not 'initialTypeSolution' in self.parameters : 
				self.parameters.update(dict(initialTypeSolution="RANDOM"))		 	 
		# print(self.parameters) 
		
		
	def memeticAlgorithm(self, solution=None):
		""" 
		@param state.Solution solution : 
		@return  :
		@author
		"""
        
		if solution!=None :
			self.popul.addSort(solution)  
            
		self.popul.printFitness("POP(INI)") #  before printTempoV(String)  
		samples = 1  
		
		while self.isStopCriteria():  
			i = 0    
			while  i < samples  : 
				notCrossover = 0
				par = self.objProblem.op.selection(self.parameters.get('selectionoper'), self.popul) 
				tempSol = par[0] 

				if  np.random.rand() < self.parameters.get('probcrossover'): 
					temp = self.objProblem.op.crossover(self.parameters.get('crossoveroper'), par) 
					tempSol = temp[0]
                	## disp(i1) disp(i2) 
				else :
					notCrossover = 1 
					
				if  notCrossover == 0 and np.random.rand() < self.parameters.get('probmutation'):	 
					tempSol = self.objProblem.op.mutation(self.parameters.get('mutationoper'), [tempSol]) 
		   
				if  notCrossover == 0 and not self.popul.contains(tempSol) : 
					self.objProblem.evaluate(tempSol)
					self.objProblem.counter.incCount()  
					self.popul.addSort(tempSol)  
					i = i + 1 
					# 	print(self.objProblem.counter.count)
		self.status.stateFinal = self.popul.getIndividual(0)  
		self.popul.printFitness("POP(FIN)") 
		# self.popul.prints( )        


	def memeticAlgorithmGen(self, solution=None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		""" 
		
		if solution!=None :
			self.popul.addSort(solution)		
        
		self.popul.printFitness("POP(INI)")    
		popTemp = Population(0, self.objProblem)
		#  self.popul.getIndividual(0).prints()
		pp = 1 
		while self.isStopCriteria():  
			# print("-------------")
			# print(str(self.popul.popSize) )
			elite = math.floor(self.parameters.get('individuals')*self.parameters.get('percElitism'))
			if  elite % 2 ==1:
				elite = elite+1
			popTemp.addPop(self.popul, elite )
			# popTemp.printFitness(str (len(popTemp.popul)) )
			# print(str(popTemp.popSize) )
			for i in range((self.parameters.get('individuals') - elite )//2 ):  
				
				par = self.objProblem.op.selection(self.parameters.get('selectionoper'), self.popul) 
				if np.random.rand() < self.parameters.get('probcrossover'):
					ch = self.objProblem.op.crossover(self.parameters.get('crossoveroper'), par)  
                	## disp(i1)disp(i2)
					self.objProblem.evaluate(ch[0])
					self.objProblem.counter.incCount()
					popTemp.addSort(ch[0], True)  
					self.objProblem.evaluate(ch[1])
					self.objProblem.counter.incCount()
					popTemp.addSort(ch[1], True) 
					# print("*****" ) 
					# ch[0].prints() 
					# ch[1].prints() 
				else:
					# print("*eee*" ) 
					popTemp.addSort(par[0], True)  
					popTemp.addSort(par[1], True)  
				 
			# print(str(popTemp.popSize)+ "-" + str(i)+ "-" +str(self.popul.popSize))	
			# print("!!!!!!!!!")
			# self.popul.copy(popTemp) 
			self.popul = copy.deepcopy(popTemp)
			popTemp.removeAll() 
			# print(str(popTemp.popSize)+ "-" + str(self.popul.popSize))	
			for i in range(elite):
				if np.random.rand() < self.parameters.get('probmutation'):
					paq = self.objProblem.op.mutation(self.parameters.get('mutationoper'), [self.popul.getIndividual(i)]) 
					self.objProblem.evaluate(paq)
					self.objProblem.counter.incCount()
					self.popul.addSort(paq)  
			 
			# self.popul.printFitness(str (pp) )
			pp = pp +1
			
		self.status.stateFinal = self.popul.getIndividual(0)  
		self.popul.printFitness("POP(FIN)") 
		# self.popul.prints( )  
        
        
	def replaceSolution(self, solution):
		"""
		@return  :
		@author
		"""
     
		self.popul.addSort(solution)        
		 

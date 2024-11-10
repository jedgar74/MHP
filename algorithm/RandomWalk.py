
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *
import math 
import copy


class RandomWalk (Heuristic):

	"""
	:version:
	:author:
	"""


	""" ATTRIBUTES   
	shortTerm  (public)
	initTemperature  (implementation)
	finalTemperature  (implementation)
	can be GEOMETRIC or ARITHMETIC
	coolingScheme  (implementation)
	omega  (implementation)
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
		
		self.shortTerm  = "RW"
		self.objProblem = problem 
		 
		self.setParameters(fileConfig)
		
		self.status.stateInitial = Solution(self.objProblem, self.parameters.get('initialTypeSolution'));
		self.objProblem.evaluate(self.status.stateInitial);
		self.objProblem.counter.incCount();
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        
		self.solutions=[]
        
		if run==True :
			self.randomWalk()


	def run(self, solution=None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
		if solution==None :
			self.randomWalk()
		else :
			self.randomWalk(solution)


	def setParameters(self, fileConfig):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
		self.parameters = self.readParameters(fileConfig, self.shortTerm)
		# print(self.parameters)
		for i in range(6): # (int i = 0; i < nameParameters.size(); i++) {
 
					
			if not 'initialTypeSolution' in self.parameters : 
				self.parameters.update(dict(initialTypeSolution="RANDOM"))
				
			if not 'mutationoper' in self.parameters : 
				self.parameters.update(dict(mutationoper="BASIC2"))	
				 
		# print(self.parameters) 


	def randomWalk(self, solution=None):
        
        # http://iao.hfuu.edu.cn/images/teaching/lectures/metaheuristic_optimization/06_random_walk.pdf
		if solution==None :
			nextState = copy.deepcopy(self.status.stateFinal)      
		else :
			nextState = copy.deepcopy(solution)   
            
		self.solutions.append(copy.deepcopy(nextState) )    
		nextState.prints("............")
		
 
		# print(self.parameters.get('mutationoper'))
		# System.out.println(" SA CoolingScheme=" + self.coolingScheme
		# 		+ " Omega=" + omega + " Tf=" + self.finalTemperature + "  To="
		# 		+ self.initTemperature);*/

		while self.isStopCriteria(): 
 
			nextState = self.objProblem.op.mutation(self.parameters.get('mutationoper'), [nextState]) 
			self.objProblem.evaluate(nextState);
			self.objProblem.counter.incCount();
            
			self.solutions.append(copy.deepcopy(nextState) )
	 
			if self.objProblem.op.isBetter([nextState, self.status.stateFinal]): 
				self.status.stateFinal = nextState  
				 

 
		# System.out.println(" : "+self.objProblem.evaluationCounter);
		# self.internalState.setLabel("Final");
	  
	 
    
	def replaceSolution(self, solution):
		"""
		@return  :
		@author
		"""
     
		self.status.stateFinal = copy.deepcopy(solution) 	
	
	
	
	

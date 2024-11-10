
from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *
import math 
import copy


class SimulatingAnnealing (Heuristic):

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
		
		self.shortTerm  = "SA"
		self.objProblem = problem 
		 
		self.setParameters(fileConfig)
		
		self.status.stateInitial = Solution(self.objProblem, self.parameters.get('initialTypeSolution'));
		self.objProblem.evaluate(self.status.stateInitial);
		self.objProblem.counter.incCount();
		self.status.stateFinal = copy.deepcopy(self.status.stateInitial) 
        
		if run==True :
			self.simulatingAnnealing()


	def run(self, solution=None):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
		if solution==None :
			self.simulatingAnnealing()
		else :
			self.simulatingAnnealing(solution)


	def setParameters(self, fileConfig):
		""" 
		@param problem.Problem _problem : 
		@return  :
		@author
		"""
		
		self.parameters = self.readParameters(fileConfig, self.shortTerm)
		# print(self.parameters)
		for i in range(6): # (int i = 0; i < nameParameters.size(); i++) {

			if not 'initTemperature' in self.parameters :
				self.parameters.update(dict(initTemperature=0))
				
			if not 'finalTemperature' in self.parameters :
				self.parameters.update(dict(finalTemperature=0))
					
			if not 'coolingScheme' in self.parameters :
				self.parameters.update(dict(coolingScheme="GEOMETRIC"))
				# ARITHMETIC
				
			if not 'omega' in self.parameters :
				self.parameters.update(dict(omega=-1))
					
			if not 'initialTypeSolution' in self.parameters : 
				self.parameters.update(dict(initialTypeSolution="RANDOM"))
				
			if not 'mutationoper' in self.parameters : 
				self.parameters.update(dict(mutationoper="BASIC2"))	
				 
		# print(self.parameters) 


	def simulatingAnnealing(self, solution=None):
		if solution==None :
			nextState = copy.deepcopy(self.status.stateFinal)      
		else :
			nextState = copy.deepcopy(solution)        
		nextState.prints("............")
		
		temperature = self.initialTemperature() 
		# print(self.parameters.get('mutationoper'))
		# System.out.println(" SA CoolingScheme=" + self.coolingScheme
		# 		+ " Omega=" + omega + " Tf=" + self.finalTemperature + "  To="
		# 		+ self.initTemperature);*/

		while self.isStopCriteria(): 
 
			nextState = self.objProblem.op.mutation(self.parameters.get('mutationoper'), [nextState]) 
			self.objProblem.evaluate(nextState);
			self.objProblem.counter.incCount();
	 
			if self.objProblem.op.isBetter([nextState, self.status.stateFinal]): 
				self.status.stateFinal = nextState  
				
			elif  self.isAccept(temperature, nextState, self.status.stateFinal):
				self.status.stateFinal = nextState  

			temperature = self.updateTemperature(temperature)  
		# System.out.println(" : "+self.objProblem.evaluationCounter);
		# self.internalState.setLabel("Final");
	 
	 
	def isAccept(self, temp, nextState, internalState) :
		ic = 50 * np.random.rand()  

		if ic < self.probabilityFunction(temp, nextState.fitness, internalState.fitness) :
			return True 
		else  :
			return False 
 
 
	def probabilityFunction(self, t, nf,  af) : 
		return math.exp((af - nf) / t);
	 
	 
	# this method is needed to review because the initial temperature not modified in the body
	def initialTemperature(self) : 
		""" 
		This method implements the initial temperature by Kilpatrick
		 
		"""
		if  self.parameters.get('omega') == -1 :
			if  self.parameters.get('coolingScheme') == "ARITHMETIC" :
				self.parameters.update(dict(omega=self.parameters.get('initTemperature')/ objProblem.counter.limit)) 
				self.parameters.update(dict(finalTemperature=0)) 
			else :
				self.parameters.update(dict(finalTemperature=1e-6 /self.parameters.get('initTemperature')))
				timer = 1 / self.objProblem.counter.limit 
				self.parameters.update(dict(omega=self.parameters.get('finalTemperature')**timer))  
 
		return self.parameters.get('initTemperature');
 
 
	def updateTemperature(self, temperature) :  

		if self.parameters.get('coolingScheme') == "ARITHMETIC" :
			return self.parameters.get('omega') - temperature  
		else :
			return self.parameters.get('omega') * temperature 
 
    
	def replaceSolution(self, solution):
		"""
		@return  :
		@author
		"""
     
		self.status.stateFinal = copy.deepcopy(solution) 	
	
	
	
	

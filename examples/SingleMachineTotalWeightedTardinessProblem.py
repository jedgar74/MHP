from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np 

class SingleMachineTotalWeightedTardinessProblem (Problem):

	""" 
	Define the classic problem termed N-Queens problems
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
		self.nameShort = "SMTWTP"   
		# print(self.typeState)
		self.selOpers()
		# print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst) 
	  

	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@author
		"""
   
		instancer = 1  
		self.nVar = int(namFile[1])
		self.jobsTardiness = []
		with open('./DATA/instances/SMTWTP/'+namFile[0], 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n')  
 
		# Second step. Process line 
		stringTemp = [] 
	 
		# Each cycle is a instance
		for j in range(len(lines)): 
		    auxili = lines[j] 
		    print(auxili)
		    r = auxili.split()  
		    # print(r)
		    for d in range(len(r)):  
		        # print(r[d])
		        stringTemp.append( int(r[d]) )  
			
		contr = self.nVar*3
        
		print(len(stringTemp)) 
		for j in range(len(stringTemp)//contr):  
		    dt = DataTardiness(self.nVar)	

		    for g in range(contr): 
	        	dr = stringTemp[g + contr*j]    
	        	if g in range(self.nVar, 2*self.nVar): 
	        	    dt.addWeights(dr, g - self.nVar)                    
	        	elif g in range(2*self.nVar, 3*self.nVar):  
	        	    dt.addDueDates(dr, g - (2*self.nVar))	        	
	        	else:  
	        	    dt.addProcessingTime(dr, g)
      	
		    # dt.print()	 
		    self.jobsTardiness.append(dt) 
 
		nExTardiness = len(self.jobsTardiness)
		self.nowDataTardiness = DataTardiness(self.nVar)
		self.nowDataTardiness = self.jobsTardiness[instancer-1] 
 


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		total = 0
		time = 0
		tardiness = 0 
		
		for j in range(self.nVar): 
			tardiness = time +  self.nowDataTardiness.getProcessingTimeElementAt(s.vars[j] ) -  self.nowDataTardiness.getDueDatesElementAt(s.vars[j] )
			if (tardiness > 0):
				# tardiness = 0
				total = total + (tardiness *  self.nowDataTardiness.getWeightsElementAt(s.vars[j] ))

			time = time + self.nowDataTardiness.getProcessingTimeElementAt(s.vars[j])
             
		 
		s.setFitness(total)     

 


class DataTardiness ():	
 
	def __init__(self, jobs):    
		self.processingTimes = np.zeros(jobs)
		self.weights = np.zeros(jobs)
		self.dueDates = np.zeros(jobs) 
	
	
	def print(self):
 		print("------------------------------")
# =============================================================================
# 		System.out.print("p[")
# 		for (int g = 0 g < this.processingTimes.length g++)
#     		System.out.print(this.processingTimes[g]+",")
#     	
# 		System.out.println("]")
# 		
# 		System.out.print("w[")
# 		for (int g = 0 g < this.weights.length g++)
#     		System.out.print(this.weights[g]+",")
#     	
# 		System.out.println("]")
# 		
# 		System.out.print("d[")
# 		for (int g = 0 g < this.dueDates.length g++)
#     		System.out.print(this.dueDates[g]+",")
#     	
# 		System.out.println("]")
# =============================================================================
	
	
	def addProcessingTime(self, _value, pos):
		self.processingTimes[pos]= _value
	
	
	def addWeights(self, _value, pos) :
		self.weights[pos]= _value
	
	
	def addDueDates(self, _value, pos):
		self.dueDates[pos]= _value 
	
	
	def getProcessingTimeElementAt(self, _position):
		return self.processingTimes[_position]
	
	
	def getWeightsElementAt(self, _position):
		return self.weights[_position]
	
	
	def getDueDatesElementAt(self, _position):
		return self.dueDates[_position]
	
	
 
	


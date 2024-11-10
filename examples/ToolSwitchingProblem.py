from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np 

class ToolSwitchingProblem (Problem):

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
		self.nameShort = "ToSP"   
		# print(self.typeState)
		self.selOpers()
		# print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst) 
	  

	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@
        
		"""
        
		fileData = namFile[0] 
		fileData = fileData.replace("matrix_", "")
		fileData = fileData.replace("j_", " ")
		fileData = fileData.replace("to_", " ")
		# fileData = fileData.replace("C_NSS_", " ")
		fileData = fileData.replace("NSS_", " ")
        
		r = fileData.split()  
		# print(fileData)
		for d in range(len(r)):  
			# print(r[d])
			if (d == 0):
				self.nVar = int(r[d])
			elif (d == 1):
				self.nTools = int(r[d] )
			# elif (d == 2):
			# 	self.nMagazine = int(r[d] ) 
 
		self.nMagazine = namFile[1]
		with open('./DATA/instances/ToSP/'+namFile[0], 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n') 
       
        # Remember args[2] is the name of file in self format: matrix_?j_?to_NSS_?.txt
		# where NSS means that file no contain jobs subset any others
  
		_tools  = [] 
		self.matA = np.zeros(shape=(self.nTools, self.nVar))                  
                
		for j in range(len(lines)):    
            
			if (len(lines[j]) >= 2): 
				linn=lines[j].replace(":", " ")                 
				linn=linn.replace(",", " ")                
				linn=linn.replace("#", " ")   
                 
				# self.nJobs = self.nJobs+1  
                
				# Determine the number of tools 
				r = linn.split()  
				for d in range(len(r)):  
				    if (d >= 1):
				        g = int(r[d] ) 	
				        self.matA[g][j] = 1 
# =============================================================================
#                         if (not g in _tools)
#     						_tools.append(g) 
#                             
# 		self.nTools = len(_tools)   
# =============================================================================
		print(self.matA) 
   


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		""" 
        
		# computing fitness by means KTNS 
		nSeq = 0

		# copy original matrix 
		matrixA = np.zeros(shape=(self.nTools, self.nVar)) 
		 
		np.copyto(matrixA, self.matA) 

		# __int control = 1
		# In Zhou J(i,n), here jin
		jin  = [] 
		jin = self.minJXToools(matrixA, nSeq, s)

		while (nSeq < self.nVar) : 
			# int tools = toolsForJob(v[n], matrixA, nTools)
			tools = self.toolsForJob(s.vars[nSeq], matrixA, self.nTools) 
			if (tools == self.nMagazine) :
				nSeq = nSeq + 1	
				jin = self.minJXToools(matrixA, nSeq, s)				
			else :			
				maxNS = 1000
				minNS = 0 
				if (nSeq != 0):
					for i in range(self.nTools): 
						tmp =  jin[i]  
						# if ((matrixA.getElement(i, v[n-1]) > 0) && (tmp < maxNS) )
						if  matrixA[i][s.vars[nSeq-1]] > 0  and  tmp < maxNS: 
							minNS = i
							maxNS = tmp 	
						
				else :
					for i in range(self.nTools): 
						tmp = jin[i]  
						if (tmp < maxNS) :
							minNS = i
							maxNS = tmp 		
					
				
				# matrixA.setElement(minNS, v[n], 1) 
				matrixA[minNS][s.vars[nSeq]] =  1  
				# jin.set(minNS, ""+(nVar+2))			
				jin[minNS] =  self.nVar + 2 		
		 
		# printMat(A, SP, N, M)
		# self.fitnessOne =  getNumberSwitches(AA)	
		# print(matrixA)
		s.setFitness(self.getNumberSwitches(matrixA, s)) 



	def getNumberSwitches(self, matA, s ):
		nSwitches = 0

		for k in range(self.nVar - 1): 
			for l in range(self.nTools): 
				# if (_mat.getElement(l, v[k]) == 0 && _mat.getElement(l, v[k+1]) == 1)
				if (matA[l][s.vars[k]] == 0 and matA[l][s.vars[k+1]] == 1) :
					nSwitches = nSwitches + 1 
		
		return nSwitches
	 


	def minJXToools(self, matA, nSeq, s):
		minTools  = [] 

		for t in range(self.nTools):  
			sumTools = 0
			for i in range(nSeq + 1, self.nVar):  
				# int rr = (int) A.getElement(t, v[i] ) 
				toolXJob =  matA[t][s.vars[i]] 
				if (toolXJob == 0): 
					sumTools = sumTools+ 1
				else : 
					break 
			
			minTools.append(sumTools)
		
		return minTools
	


	def toolsForJob(self, job,  matA, nTools) : 
		toolsXJob = 0

		for i in range(nTools):  
			toolsXJob = toolsXJob + matA[i][job]   

		return toolsXJob
	

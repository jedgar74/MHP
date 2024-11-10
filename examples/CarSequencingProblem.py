from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np 

class CarSequencingProblem (Problem):

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
		self.nameShort = "CSP"   
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
        http://www.csplib.org/Problems/prob001/
		"""
        
		with open('./DATA/instances/CSP/'+namFile, 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n')   
        
		self.Hi = []
		self.Ni = []        
		self.D = [] 
		self.Nb = []
		self.Dv = []   
        
		# Each cycle is a instance
		for j in range(len(lines)): 
			# auxili = lines[j]
			r = lines[j].split()  
			if (j==0):
				
				for d in range(len(r)):  
					if (d==0):
						self.nVar = int(r[d]) 
					elif (d==1):
						self.options=int(r[d]) 
					elif (d==2):
						self.models=int(r[d])  
					
			elif (j==1): 
				for d in range(len(r)): 
					self.Hi.append(int(r[d]))
					
			elif (j==2): 
				for d in range(len(r)): 
					self.Ni.append(int(r[d]))
					 
				self.matA = np.zeros(shape=(self.models, self.options))  
			else :   
				ind = -1
				for d in range(len(r)):  
					if (d==0):
						ind = int(r[d])  
					elif (d==1):
						self.D.append(int(r[d]))
					else  :
						self.matA[ind][d-2] = int(r[d]) 
						 
					
		print(self.options) 				
		print(self.models) 
		print(self.matA)
		print(self.D)
        
		# Define nb by each option
		for i in range(self.options):
			nbi=0
			for j in range(self.models):
				nbi=self.matA[j][i]*self.D[j]	
				
			self.Nb.append(nbi)
			 

		# difficulty of class v ---models 
		for i in range(self.models):
			DV=0
			for f in range(self.options):
				DV = DV + ((self.matA[i][f]*self.Nb[f])*self.Ni[f])/(self.Hi[f]*self.nVar) 
				 
			self.Dv.append(DV)
			 


		self.pos = np.zeros(self.nVar) 
		m=0
		for i in range(len(self.D)):
			g = self.D[i]
			for f in range(g):
				self.pos[m]= i
				m=m+1
			# System.out.print(""+ m+ "["+i+"] " )
  
   


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		""" 
		count = 0  

		for i in range(self.options): 
			HH = self.Hi[i] 
			NN = self.Ni[i]  
			f = []# np.zeros(self.nVar)   
			for g in range(self.nVar):   
				posCar = int(self.pos[s.vars[g]])
				# print("________")   
				# print(int(self.pos[s.vars[g]]))
				# print(i)
				# print(g)                
				if (self.matA[posCar][i] == 1):
					f.append(1)
				else :
					f.append(0)
				
 
			for v in range(self.nVar- NN):  
				tmp=0
				for c in range(NN): 
					if (f[v+c] == 1 ):
						tmp=tmp+1  
				if (tmp>HH):
					count=count+1  
		
		s.setFitness(count)
        
        
   
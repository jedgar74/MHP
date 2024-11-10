from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *
import numpy as np 

class RehearsalSchedulingProblem (Problem):

	""" 
	Define the classic problem termed RehearsalSchedulingProblem problems
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
		self.nameShort = "RSP"   
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
  
		self.D = []
		self.nPlayers =  0
		self.nVar =  0
        
		with open('./DATA/instances/RSP/'+namFile, 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n') 
 
		for j in range(len(lines)):    
            # read first line
			if (j==0):
				r = lines[j].split() 
				h=0
				for d in range(len(r)):    
				   h=1 + h
				   if (h==1) :
				       self.nVar=int(r[d] )   
				   elif (h==2):
				       self.nPlayers=int(r[d] )  
				print( self.nPlayers  )
				print( self.nVar  )
				self.matA = np.zeros(shape=(self.nPlayers, self.nVar))	 

			elif  (j==1):	 
				r = lines[j].split()  
				for d in range(len(r)):   
				   self.D.append(float(r[d] ))  
					  
			else  :  
				# fill the Matrix 
			 
				r = lines[j].split()  
				for d in range(len(r)):   
				   self.matA[j-2][d] =  int(r[d] ) 
        
 
						
		 

			# System.out.println("MUS/npla: "+nPlayers+" PIE/nvar:"+nVar )  

			# matA.printlnAllInt()
			
			# for (int i=0i< D.size() i++)
				
				# System.out.print(" "+D.get(i) )  
	
  


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		value = 0 
		for j in range(self.nPlayers): 
			value = value + self.wtp(s, j) 
		 
		s.setFitness(value)     


	def wtp(self, s, j):
		""" 
		@param state.Solution s : 
		@param int j : 
		@return int :
		@author
		""" 
		count=0 
		rehearse = False 
		np=0 

		for k in range(self.nVar):  
			if (self.matA[j][s.vars[k]] ==1) :
				 np=np+1 	 
		 
		nn=0
		for k in range(self.nVar):		
			g = s.vars[k] 
		 
			if (nn==np):
				rehearse = False 
			
			if (self.matA[j][g] ==1 ):
				if (rehearse == False):
					rehearse = True 
				 
				if (rehearse==True)	: 
				    nn = nn + 1   
			
			if (self.matA[j][g]==0 and rehearse==True  ):
				count = count + self.D[g] 
	 
		return count
 

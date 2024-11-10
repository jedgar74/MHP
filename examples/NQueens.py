from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

class NQueens (Problem):

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
		self.nameShort = "NQs"   
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
		self.nVar =  namFile 


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		nCollitions = 0;

		for i in range(s.nVar): 
			qbef = 0; 
			## qupd = ((OnlyInteger) s.getVar().allvar[i]).getValue();			
			qupd = s.getValue(i);	
			col = i;
			k = 0;
			
			while (col > 0) : 
				k = i - col + 1 
				qbef = s.getValue(i-k) 
								
				## diagonal inferior
				if (qupd - k >= 0 and qupd == qbef + k): 
					nCollitions = nCollitions + 1 
					
				## diagonal superior
				if (qupd + k < s.nVar and qupd == qbef - k): 
					nCollitions = nCollitions + 1 
				 
				col = col - 1 
		 
		s.setFitness(nCollitions)     




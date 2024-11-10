from problem.Problem import *

import numpy as np
from scipy.integrate import odeint
import math 

import json

class LotkaVolterra(Problem):

	""" 
	Define the classic problem termed N-Queens problems
	:version:
	:author: Jhon Amaya
	"""


	# def __init__(self, nVar):
	# 	"""  
	# 	@param int nVar : 
	# 	@return  :
	# 	@author
	# 	"""
	# 	super().__init__()
	# 	self.nameShort = "LV"  
	# 	self.nVar =  nVar 
		 
	
	def __init__(self, namInst=None):
		""" 
		@param String namInst : 
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "LV"  
		self.typeState =  "REAL" 
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
		with open('./DATA/instances/LV/'+namFile) as file:
			data = json.load(file)
		
		self.pr  = data['pr']
		self.dr  = data['dr']
		self.lin = data['samples']
		self.nVar = data['nVar']
		self.initConditions = data['initConditions'] 
		
		self.upperlimits = data['upperlimits']
		self.lowerlimits = data['lowerlimits']


	def evaluate(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		"""
		
		alpha = s.getValue(0)
		beta  = s.getValue(1)
		gamma = s.getValue(2)
		delta = s.getValue(3)
		
		## tspan=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20  ] 
		t = np.linspace(0, self.lin-1, self.lin) 
		
	
		## [t,f]=ode45(@lotkaVolterra2pD,tspan,x0,[],y);
		z = odeint(self.model, self.initConditions, t, args=(alpha,beta,gamma,delta))
	 
		## disp(f);
		## print(z[:,0])
		## print(z[:,1]) 

		dp = z[:,0]
		dd = z[:,1]

		## calculate fitness 
		fit = 0;
		for i in range(len(self.pr)):
			fit = fit + (self.pr[i]-dp[i])**2  + (self.dr[i]-dd[i])**2;
			## disp(z);
	 
		fit = math.sqrt(fit/2)  
		s.setFitness(fit ) 


	def model(self,x,t,alpha,beta,gamma,delta):  
		
		dpdt =  alpha*x[0] - beta*x[0]*x[1] 
		dddt = -gamma*x[1] + delta*x[0]*x[1] 
		
		return [dpdt, dddt]


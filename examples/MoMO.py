#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 14:14:38 2020

@author: tauger
"""

from problem.Problem import *

import numpy as np
from scipy.integrate import odeint
import math 

import json
import pandas as pd
import matplotlib.pyplot as plt


class MoMO(Problem):

	""" 
	Define the problem termed MoMO problem. The main objective of 
    this class is to calibrate the parameters of the carbon 
    absorption model proposed by Valerio.
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
        The problem is real type, ie, the parameters are real 
        type. The solution is represented as the number of 
        parameters to calculate. In this case 7 parameters
        
		@param String namInst : 
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "MoMO"  
		self.typeState =  "REAL" 
		# print(self.typeState)
		self.selOpers()
		# self.op.defPrecision(5)
		# print(type(self.op))
		if (not namInst == None): 
			self.readInstance(namInst)  
		

	def readInstance(self, namFile):
		""" 
        The problem instance file is read, which includes all the 
        corresponding parameters, including the limits of the 
        parameters. The additional Excel file contains the data 
        to carry out the comparison.
        
		@param String namFile : 
		@return  :
		@author
		"""
		with open('./DATA/instances/MoMO/'+namFile) as file:
			data = json.load(file)
		
		self.pr  = data['pr']
		self.dr  = data['dr']
		self.lin = data['samples']
		self.nVar = data['nVar']
		self.initConditions = data['initConditions'] 
		
		self.upperlimits = data['upperlimits']
		self.lowerlimits = data['lowerlimits']
		self.roundFitness = 6
        
		## 
		ipath = 'MOMOS.xls' 
		df = pd.read_excel(ipath, header=0)
		df.head()
		
		labels = df.columns.tolist()
		print( df.columns.tolist() )

		matrixV = df.values
		print( df.values ) 
        
		self.tc  = matrixV[:,0] 
		print(self.tc)
         
		self.cbm  = matrixV[:,1]
		print(self.cbm)
        
		self.ra  = matrixV[:,2]
		print(self.ra)
        
        ## initial conditions
		self.Fs = 0.00002 
		self.Necromasa = 2140 
		self.Co = 55.40 
		self.Ci = 50.04 
		self.HLo = 2250
		self.HSo = 19150
        ## x[0] is CBM.  
		## x[1] is VS
		## x[2] is VL
		## x[3] is HS
		## x[4] is HL
		## x[5] is RA
		self.x0 = [self.Ci, self.Fs*self.Necromasa, (1 - self.Fs)*self.Necromasa, self.HSo, self.HLo, 0 ] 
   

	def evaluate(self, sol):  
		""" 
        the objective function is calculated as the difference 
        between the value obtained by the model with the estimated
        parameters with respect to the data supplied by the Excel 
        file. In addition, there are several ways to avoid the 
        problem of the different scales of the two main parameters
        carbon and respiration. For now, the maximum difference is
        calculated for each case and all values are normalized 
        with respect to these values.
		"""
		## ResAcum  = [ 118.52	512.245	840.725	1396.19	1895.14625	2195.29625	2509,59625	2892.02125	3147.39625	3203.66125] 

		## x0 = [CBM[0], VS[0], VL[0] , HS[0], HL[0], CTTL[0] ] 
		## tspan = [0, 1, 2, 3, 4, 5, 8, 11, 18, 25, 30 ] 
		## t = np.linspace(0,20,21) 
        
		kvs = sol.vars[0] 
		kmb = sol.vars[1]
		khl = sol.vars[2]
		khs = sol.vars[3]
		khls = sol.vars[4]
		kresp = sol.vars[5]
		kvl = sol.vars[6]
		#print(tspan)        
		## [t,f]=ode45(@lotkaVolterra2pD,tspan,x0,[],y)
		z = odeint(self.model,self.x0,self.tc,args=(kvs,kmb,khl,khs,khls,kresp,kvl))
	 
		## disp(f)
		## print(z[:,0])
		## print(z[:,1]) 
		## print("---------" ) 
       
		dCBM = z[:,0]
		dVS = z[:,1] 
		dVL = z[:,2]  
		dHS = z[:,3] 
		dHL = z[:,4] 
		dRa = z[:,5]  
	 
		## calculate fitness 
# =============================================================================
# 		fit = 0
# 		for i in range(len(self.cbm)):
# 			fit = fit + (self.cbm[i] - dCBM[i])**2 + (self.ra[i] - dRa[i])**2  
# 		## disp(z)
# 		## print(fit) 
# 		fit = math.sqrt(fit) 
# 		sol.setFitness(fit )
# =============================================================================
        
        
		## calculate fitness 
 
		fit = 0
		mdCBM = sum(self.cbm)/(len(self.cbm))
		mdRa = sum(self.ra)/(len(self.ra))
		xmdCBM = max(self.cbm) 
		xmdRa = max(self.ra) 
		x3 = 0.00001 
         
		for i in range(len(self.cbm)):
		    ## fit = fit + ((self.cbm[i] - dCBM[i])/xmdCBM)**2 + ((self.ra[i] - dRa[i])/xmdRa)**2 
			## fit = fit + ((self.cbm[i] - dCBM[i])**2)/mdCBM + ((self.ra[i] - dRa[i])**2)/mdRa 
			## fit = fit + ((self.cbm[i] - dCBM[i])/mdCBM)**2 + ((self.ra[i] - dRa[i])/mdRa)**2
 			fit = fit + (self.cbm[i] - dCBM[i])**2 + (0.05*(self.ra[i] - dRa[i]))**2  
 			## fit = fit + ((self.cbm[i] - dCBM[i]+x3)/(self.cbm[i]+x3))**2 + 2*((self.ra[i] - dRa[i]+x3)/(self.ra[i]+x3))**2			
		## disp(z)
		## print(fit) 
		fit = math.sqrt(fit) 
		sol.setFitness(fit )        
           

	def evaluate2(self, sol, printd=False):  
		## ResAcum  = [ 118.52	512.245	840.725	1396.19	1895.14625	2195.29625	2509,59625	2892.02125	3147.39625	3203.66125] 

		## initial conditions
		 
		
		## x0 = [CBM[0], VS[0], VL[0] , HS[0], HL[0], CTTL[0] ] 
		## tspan=[0,1,2,3,4,5,8,11,18,25,30  ] 
		tspan = np.linspace(0,30,31)
		kvs = sol.vars[0] 
		kmb = sol.vars[1]
		khl = sol.vars[2]
		khs = sol.vars[3]
		khls = sol.vars[4]
		kresp = sol.vars[5]
		kvl = sol.vars[6]
		## [t,f]=ode45(@lotkaVolterra2pD,tspan,x0,[],y)
		z = odeint(self.model,self.x0,tspan,args=(kvs,kmb,khl,khs,khls,kresp,kvl))
	  
		dCBM = z[:,0]
		dVS = z[:,1] 
		dVL = z[:,2]  
		dHS = z[:,3] 
		dHL = z[:,4] 
		dRa = z[:,5]   
		if printd == True:
			lab=["dCBM","dVS","dVL","dHS","dHL","dRa"]
			print("t", self.tc)             
			for j in range(6):       
				tmp = z[:,j]
				tm2 = np.zeros(len(self.tc))    
				for k in range(len(self.tc)):  
				    tm3 = int(self.tc[k])       
				    tm2[k] = tmp[tm3]
            
				print(lab[j], tm2)    
            
#		print(z)	
		return [tspan, dCBM, dVS, dVL, dHS, dHL, dRa]


	def model(self,x,t,kvs,kmb,khl,khs,khls,kresp,kvl):  
		## x[0] is CBM.  
		## x[1] is VS
		## x[2] is VL
		## x[3] is HS
		## x[4] is HL
		## x[5] is RA 
	
		## variable parameters
		## kvs=y[0]
		## kmb=y[1]
		## khl=y[2] 
		## khs=y[3]
		## khls=y[4]
		## kresp=y[5]
		## kvl=y[6]
	
		## fixed parameters
		## Q10=z[0] %2.2
		## Cbmo=z[1]%0.0107
		## Tb=z[2]%28
		## Wcc=z[3]%0.3782  
	
		## soil conditions
		## Ts=z[4]28.3905
		## Ws=z[5]0.2981 
 
		Fvs   = x[1]*kvs ## x[1] is VS
		Fvl   = x[2]*kvl ## x[2] is VL 
		Fmor  = x[0]*kmb ## x[0] is CBM.
		Fhl   = x[4]*khl ## x[4] is HL
		Fhs   = x[3]*khs ## x[3] is HS
		Fhls  = x[4]*khls ## x[4] is HL
		Resp  = (x[0]**2)*kresp/self.Co    ## x[0] is CBM.
 
	
		dCBMdt  = - Resp - Fmor + Fvs   + Fvl   + Fhs  + Fhl
		dVSdt   = - Fvs  
		dVLdt   = - Fvl 
		dHSdt   = - Fhs  + Fhls 
		dHLdt   = Fmor  - Fhl - Fhls 
		## dCTTLdt = x[0]    + x[1]   + x[2]   + x[3]   + x[4] 
		dRA     = Resp
        
		return [dCBMdt, dVSdt, dVLdt, dHSdt, dHLdt, dRA]


	def prints(self, nam ):
		nam.prints()
        
# =============================================================================
# 		k = 0
# 		g = 1000000.0
# 		for i in range(len(nam)): 
# 			c = self.evaluate(nam[k]) 
# 			if  c < g: 
# 				g = c
# 				k = i
# 		v = self.evaluate2( nam[k]) 
# =============================================================================
		v = self.evaluate2(nam) 
		fig, axs = plt.subplots(2, 3)
		(ax1, ax2, ax3), (ax4, ax5, ax6) = axs
		ax1.plot(v[0], v[1], "bo", self.tc, self.cbm, "go")	
		ax1.set_title('CBM')
	
		ax2.plot(v[0], v[2], "bo")	
		ax2.set_title('VS')
	
		# plt.legend(('dCBM', 'dVS', 'dVL', 'dVS', 'dVL', 'dVL'),
		# plt.prop = {'size':10}, loc = 'upper right')

		ax3.plot(v[0], v[3], "bo")	
		ax3.set_title('VL')
		
		ax4.plot(v[0], v[4], "bo")	
		ax4.set_title('HS')
		
		ax5.plot(v[0], v[5], "bo")	
		ax5.set_title('HL')
			
		ax6.plot(v[0], v[6], "bo", self.tc, self.ra, "go")		
		ax6.set_title('RA')
		
		plt.show()

 

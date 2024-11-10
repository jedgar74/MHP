#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 14:56:17 2020

@author: tauger
"""
from problem.Problem import *
from statisticc.BasicStats import BasicStats 


import math 
import numpy as np


class Landscape ():
    
	def __init__(self, problem, fileConfig):
		""" 
		@param problem.Problem problem : 
		@param String _fileConfig : 
		@return  :
		@author
		"""
		super().__init__()
		self.stats = BasicStats(problem.typeProblem)
		self.typeState = problem.typeState
		#self.shortTerm  = "MA"
		#self.objProblem = problem 
		#self.setParameters(fileConfig)        
        
	def fla(self, s=None):
		self.calcCorrR1()
		self.calcLength()
		self.corrLandscape(1)
		self.autoLandscape()
		self.epsilon()
		self.infoLandscape(self.eps)
		if (s  != None):
		    print(" ")
		    self.rhoLandscape(self.distance(s))      
        
        
	def distance(self, s):
		y  = []      
        
		for i in range(self.m):
		    y.append(self.dis(self.stats.getSolution(i), s))
		     
		return y
    
    
	def dis(self, s, o): 
		y  = s.nVar
		if (self.typeState == "PERMUTATIONAL"):
		    for i in range(s.nVar): 
		       if (s.vars[i] == o.vars[i]):	
		           y  = y  - 1  
		    if ((y % 2) == 1):	
		       y  = y +1       
                   
		return y //2   
    
    
	def arrayToStats(self, a):
		self.f  = []      
		for i in range(len(a)):
		    # a[i].prints( )
		    self.stats.add(a[i])
		    self.f.append(a[i].fitness)
		self.m = self.stats.nSolutions()
		print(self.m)
		self.media = self.stats.average()
		self.sigma = self.stats.stDeviat(self.media)  
		self.better = self.stats.solutions[self.stats.better()]         
       
        
	def calcCorrR1(self): 
	
		sumf=0
		for i in range(self.m-1): 
			sumf=sumf + ((self.stats.getSolution(i+1).fitness-self.media)*(self.stats.getSolution(i).fitness-self.media))
		
		self.corrR1=(1/(self.sigma*self.sigma*(self.m-1)))*sumf 
		print(":: R1             :: "+ str(round(self.corrR1, 3)) ) 
	

	#The lower the correlation length the more rugged the landscape. 
	def calcLength(self):
		if (self.corrR1==0):
			self.corrLength=0
		else :
			self.corrLength = -1/(math.log(abs(self.corrR1)))
		print(":: Length         :: "+ str(round(self.corrLength, 3)) ) 		    
	
    # Sea X la secuencia aleatoria de fitness    
	def corrLandscape(self,  s):
	# def corrLanscape(self, X, s): 
		# Calculate the mean 
		# MEDIA=np.mean(X) 
        
		# disp(s)
		NUM = 0
		# for i in range(len(X) - s):  
		# NUM = NUM + (X(i)-MEDIA)*(X(i+s)-MEDIA)
		for i in range(self.m - s):   
			NUM = NUM + ((self.stats.getSolution(i+s).fitness-self.media)*(self.stats.getSolution(i).fitness-self.media))
		
		DEN = 0
		# for i in range(len(X)):  
		# 	DEN=DEN + (X(i)-MEDIA)**2 
		for i in range(self.m):  
			DEN=DEN + (self.stats.getSolution(i).fitness-self.media)**2 
            
		self.r=NUM/DEN
		print(":: r              :: "+ str(round(self.r, 3)) ) 	
	
    # Sea X la secuencia aleatoria de fitness    
	def autoLandscape(self):
		# Calculate the mean 
		# self.corrLandscape(1)
		self.tau= -1/(math.log(self.r))
		print(":: tau            :: "+ str(round(self.tau, 3)) )		
        
    # Sea X la secuencia aleatoria de fitness    
	def rhoLandscape(self, Y):
		# Calculate the mean   
		MEDIAX=np.mean(self.f) 
		MEDIAY=np.mean(Y) 
 
		# Calculate the covariance
		COV = 0
		for i in range(len(Y)): 
			COV = COV + (self.f[i]-MEDIAX)*(Y[i]-MEDIAY) 

		COV = COV /len(Y)

		self.rho = COV/(np.std(self.f)*np.std(Y))   
		print(":: rho            :: "+ str(round(self.rho, 3)) )
		
	def epsilon(self) :	 
		minm = 1e40 
		maxm = 1e-40 
      
		for i in range(self.m):
			if   (self.stats.getSolution(i).fitness  < minm):
				minm = self.stats.getSolution(i).fitness
			elif (self.stats.getSolution(i).fitness  > maxm):
				maxm = self.stats.getSolution(i).fitness      
 
		self.eps = (maxm - minm)/6 # + minm
		print(":: epsilon        :: "+ str(round(self.eps, 3)) ) 
        
    # sea X la secuencia de aleatoria de fitness 
    # X =[0,0.01,0.05,0.2,0.21,0.9]
    # eps = 0.68		
	def infoLandscape(self, eps) :	 
 
		XLEN = self.m - 1
		Y = np.zeros(XLEN)
		print(" ") 
		for i in range(XLEN):  
# =============================================================================
# 			if ((X(i+1) - X(i)) < -eps):
# 				Y[i] = -1
# 			elif (abs(X(i+1) - X(i)) <= eps):
# 				Y[i] = 0 
# 			elif ((X(i+1) - X(i)) > -eps):
# 				Y[i] = 1  
# =============================================================================
			dff = self.stats.getSolution(i+1).fitness - self.stats.getSolution(i).fitness 
			# print(dff) 			
			if (dff < eps*-1):
				Y[i] = -1
			elif (abs(dff) <= eps):
				Y[i] = 0 
			elif (dff > eps*-1):
				Y[i] = 1  


		# disp(Y)
		# calculate prob 01 y 10
# =============================================================================
# 		YTMP = Y
# 		YTMP[len(Y)+1]=0
# 		YLEN = len(YTMP)  
# =============================================================================
		# print(" ")  
		YTMP = np.zeros(self.m)
		for i in range(XLEN):   
			YTMP[i]=Y[i]          
		YLEN = len(YTMP)

		P01 = 0
		P0U = 0
		P10 = 0
		P1U = 0
		PU0 = 0
		PU1 = 0
        
		for i in range(1,YLEN):
		# for i=2:YLEN
			# print(YTMP[i-1]) 
			# print(YTMP[i-1] +" "+YTMP[i])             
			if (YTMP[i-1] == 0 and YTMP[i] == 1):
				P01 = P01 +1
			elif (YTMP[i-1] == 0 and YTMP[i] == -1):
				P0U = P0U +1
			elif (YTMP[i-1] == 1 and YTMP[i] == 0):
				P10 = P10 +1
			elif (YTMP[i-1] == 1 and YTMP[i] == -1):
				P1U = P1U +1
			elif (YTMP[i-1] == -1 and YTMP[i] == 0):
				PU0 = PU0 +1
			elif (YTMP[i-1] == -1 and YTMP[i] == 1):
				PU1 = PU1 +1
	 

		P01 = P01/(YLEN-1)
		P0U = P0U/(YLEN-1)
		P10 = P10/(YLEN-1)
		P1U = P1U/(YLEN-1)
		PU0 = PU0/(YLEN-1)
		PU1 = PU1/(YLEN-1)
 
		print(" ")     
		print(":: P01            :: "+ str(round(P01, 3)) )
		print(":: P0U            :: "+ str(round(P0U, 3)) )        
		print(":: P10            :: "+ str(round(P10, 3)) )        
		print(":: P1U            :: "+ str(round(P1U, 3)) )        
		print(":: PU0            :: "+ str(round(PU0, 3)) )        
		print(":: PU1            :: "+ str(round(PU1, 3)) )

        
		# calculate log6(T)
		# G = log10(T)/log10(6)  
		LOGP01 = -1*P01*math.log10(P01)/math.log10(6)
		# LOGP0U = -P0U*log10(P0U)/log10(6)
		LOGP10 = -1*P10*math.log10(P10)/math.log10(6)
		# LOGP1U = -P1U*log10(P1U)/log10(6)
		# LOGPU0 = -PU0*log10(PU0)/log10(6)
		# LOGPU1 = -PU1*log10(PU1)/log10(6)
		# Information Content

		# str=sprintf('Probabilities O1-10 are %d - %d', P01, P10)
		# disp(str)

 
		print(" ") 
		H = LOGP01 + LOGP10 #  + LOGP0U + LOGP1U + LOGPU0 + LOGPU1   
		print(":: H              :: "+ str(round(H, 3)) )
        
        
		K=0
		J=0
		for i in range(YLEN): 
		 	if (J == 0 and YTMP[i] != 0):
		 		J=i 
		 		K=K+1
		 	elif (J > 0 and YTMP[i] != 0 and YTMP[i] != YTMP[J] ): 
		 		J=i 
		 		K=K+1  


		# Partial Information Content

		M = K/(YLEN-1)
		print(":: M              :: "+ str(round(M, 3)) ) 
		# str=sprintf('Inf.Cont (H) and Part.Inf.Cont (M) are %d - %d', H, M)
		# disp(str) 
		
		
		
		
		     

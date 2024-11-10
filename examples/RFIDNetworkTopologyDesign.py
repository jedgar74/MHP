#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 19:15:17 2020

@author: tauger
"""

from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import matplotlib.pyplot as plt 
import numpy as np
import math 

class RFIDNetworkTopologyDesign (Problem):

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
		self.nameShort = "RFIDNTD"   
		self.typeState = "MIX" 
		self.typeProblem = "MAX" 
		# print(self.typeState)
		self.selOpers()
		self.op.defPrecision(1)
		# print(type(self.op)) 
		if (not namInst == None): 
			self.readInstance(namInst)    
        
		 
	  

	def readInstance(self, namFile):
		""" 
		@param String namFile : 
		@return  :
		@author
		"""
		self.rfid = []
		self.readers = 0
		self.gridx = 0 
		self.gridy = 0
		self.w = []
        
		self.upperlimits = []
		self.lowerlimits = []        
		self.typeVarMix = []
        
		with open('./DATA/instances/RFIDNTD/'+namFile, 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n') 
 
		for i in range(len(lines)):     
		    if ('readers' in lines[i] ) : 
		        r = lines[i].split() 
		        self.readers = int(r[1] )
		        # print(self.readers)  
		    elif ('grid' in lines[i] ) :
		        r = lines[i].split()
		        self.gridx = int(r[1] ) 
		        self.gridy = int(r[2] )
		    elif ('weightf' in lines[i] ) :
		        r = lines[i].split()
		        for d in range(1, len(r)):  
		            self.w.append(float(r[d] ))
		    else   : 
		        r = lines[i].split()  
		        s = []
		        if (len(r) == 2) :   
		            s.append(float(r[0] ))  	  
		            s.append(float(r[1] ))  	
		            self.rfid.append(s)      
		            # print(r )
  
		self.nVar = 3 * self.readers
        
		## print(self.nVar)     
        # We define the limits of variables
		for i in range( self.nVar ):
		    if (i % 3 == 0) : 
		        self.upperlimits.append(7)
		        self.lowerlimits.append(0)
		        self.typeVarMix.append("integer")
		    else : 
		        self.upperlimits.append(self.gridy)
		        self.lowerlimits.append(0)
		        self.typeVarMix.append("real")               
                
 
	def evaluate(self, s):
		"""  
		Se utilizó el artículo de Botero para calcular el fitness. Sin embargo se usa 
		una representación de la solución diferente, dónde en lugar de binario se utilizó 
		de tipo real
		
		@param state.Solution s : 
		@return  :
		@author
		"""
		# s = [6, 12, 5, 8, 6, 9, 6, 7.5, 15]         
		## print("---------------------") 		 
        
		fitness = 0 
		f = []
		v = []
		cover = []
		overlap = []
		redundant = []
		outdeployment = []
		area = []

		for c in range(s.nVar//3):
		    q = [] 
		    if ( (s.vars[c*3+1] - s.vars[c*3]) < 0 or (s.vars[c*3+1] + s.vars[c*3]) > self.gridx or (s.vars[c*3+2] - s.vars[c*3]) < 0 or (s.vars[c*3+2] + s.vars[c*3]) > self.gridy) :
		        outdeployment.append(c)
		    for i in range(len(self.rfid)): 
		        r = self.rfid[i]
		        es = (r[0]-s.vars[c*3+1])**2 + (r[1]-s.vars[c*3+2])**2
		        # print(str(es) + " " + str(s[c*3]**2))                
		        if (es  <= s.vars[c*3]**2) :   
		            q.append(i)
                    
		    v.append(q )     
		## print(v)
                   
        
		for c in range(s.nVar//3):
		    q = v[c]            
		    for i in range(len(v[c])): 
		        r = v[c][i]                
		        if (not v[c][i] in cover) :   
		            cover.append(v[c][i])
                  
                       
		for c in range(s.nVar//3 - 1):
		    qv = v[c]     
      
		    for j in range(len(qv)): 
		        rv = qv[j]            
		        for i in range(c + 1, s.nVar//3 ): 
		            qc = v[i]   
		            if (rv in qc) :   
		                overlap.append(rv)  
		                if (not c in redundant) : 
		                    redundant.append(c) 
		                if (not i in redundant) : 
		                    redundant.append(i) 
		                  
                            
		for c in range(s.nVar//3):
		    area.append(math.pi*(s.vars[c*3] ** 2 ) )
		    xn = s.vars[c*3+1] - s.vars[c*3] 
		    xp = s.vars[c*3+1] + s.vars[c*3] 
		    yn = s.vars[c*3+2] - s.vars[c*3] 
		    yp = s.vars[c*3+2] + s.vars[c*3]    
            
		    if  xn < 0 :
		         pass
		    elif xp > self.gridx : 
		         pass            
		    elif yn < 0  :
		         pass            
		    elif yp  > self.gridy  :
		         pass		       
                
        # está sobredimensionado el cálculo de la intercepción                                            
		    
	        
		overlaparea = 0    
		for c in range(s.nVar//3 - 1):			
		    for i in range(c + 1, s.nVar//3 ): 
		         rm = s.vars[c*3]    
		         cd = 0
		         if  rm < s.vars[i*3] :    
		             rm = s.vars[i*3]
		             cd = 1 
		         dm = math.sqrt(s.vars[i*3]**2 + s.vars[c*3]**2)   
		         if  rm <= dm :
		             if  cd == 0 :
		                 overlaparea = overlaparea + math.pi*(s.vars[i*3] ** 2 )
		             else :    
		                 overlaparea = overlaparea + math.pi*(s.vars[c*3] ** 2 )  
		         else :   
		             if  cd == 0 :
		                 overlaparea = overlaparea +  2*(s.vars[c*3] ** 2 + s.vars[c*3]*s.vars[i*3] - dm)
		             else :    
		                 overlaparea = overlaparea +  2*(s.vars[i*3] ** 2 + s.vars[c*3]*s.vars[i*3] - dm)
                     
		                             
		## print(cover)                    
		## print(overlap)   
		## print(redundant)
		## print(outdeployment)        
		## print(overlaparea)                 
        # Overlapping of the reading area
        # Revisar para implementar la interferencia, por ahora, 
        # sólo maximizar el área
# =============================================================================
# 		e = 0
# 		f1 = 1/(1+e**2) 
# 		f.append(f1) 
# =============================================================================
		ee = 0.0
	
		g = sum(area)
		if g == 0:
			g = 0.00001  
		## print("..." +str(e) + " " +str(overlaparea))
		## print(area)
		## print(g)        
		## print(overlaparea)        
		# for c in range(s.nVar//3):      
		#     e = e - area[c]  
		# e = e - overlaparea
		ee =  overlaparea / g  
		f1 = 1/(1+ee**2) 

		f.append(round(f1, 4))
        
        # ** Number of useless readers 
		e = 0
		for c in range(s.nVar//3):        
		    if (len(v[c]) == 0) :
		        e = e + 1 
		f2 = 1/(1+e**2) 
		# print(e)   
		f.append(round(f2, 4))        
        
        # ** Number of tags covered
		# e = len(self.rfid) - len(cover)       
		e = (len(self.rfid) - len(cover) )/len(self.rfid)
		f3 = 1/(1+e**2) 
		# print(e)
		f.append(round(f3, 4))   
        
        # Number of readers located out of the deployment area
		e = len(outdeployment) 
		f4 = 1/(1+e**2) 
		f.append(round(f4, 4))   
        
        # ** Number of redundant readers
		e = len(redundant)
		f5 = 1/(1+e**2) 
		f.append(round(f5, 4))    
        
        # ** Number of tags located in overlapped reading areas
		e = len(overlap)
		f6 = 1/(1+e**2) 
		f.append(round(f6, 4))        
        
        
        #         
		for c in range(6):
		    fitness = fitness + self.w[c]*f[c] 
            
		print(f ) 	
		## print(self.w ) 	
		## print(fitness ) 
        
		s.setFitness(fitness)     

	def evaluate2(self, s):
		"""  
		Se utilizó el artículo de  ...
		
		@param state.Solution s : 
		@return  :
		@author
		"""
		# s = [6, 12, 5, 8, 6, 9, 6, 7.5, 15]         
		## print("---------------------") 		 
        
		fitness = 0 
		f = []
		v = []
		cover = []
		overlap = []
		redundant = []
		outdeployment = []
		area = []

		for c in range(s.nVar//3):
		    q = [] 
		    if ( (s.vars[c*3+1] - s.vars[c*3]) < 0 or (s.vars[c*3+1] + s.vars[c*3]) > self.gridx or (s.vars[c*3+2] - s.vars[c*3]) < 0 or (s.vars[c*3+2] + s.vars[c*3]) > self.gridy) :
		        outdeployment.append(c)
		    for i in range(len(self.rfid)): 
		        r = self.rfid[i]
		        es = (r[0]-s.vars[c*3+1])**2 + (r[1]-s.vars[c*3+2])**2
		        # print(str(es) + " " + str(s[c*3]**2))                
		        if (es  <= s.vars[c*3]**2) :   
		            q.append(i)
                    
		    v.append(q )     
		## print(v)
                   
        
		for c in range(s.nVar//3):
		    q = v[c]            
		    for i in range(len(v[c])): 
		        r = v[c][i]                
		        if (not v[c][i] in cover) :   
		            cover.append(v[c][i])
                  
                       
		for c in range(s.nVar//3 - 1):
		    qv = v[c]     
      
		    for j in range(len(qv)): 
		        rv = qv[j]            
		        for i in range(c + 1, s.nVar//3 ): 
		            qc = v[i]   
		            if (rv in qc) :   
		                overlap.append(rv)  
		                if (not c in redundant) : 
		                    redundant.append(c) 
		                if (not i in redundant) : 
		                    redundant.append(i) 
		                  
                            
		for c in range(s.nVar//3):
		    area.append(math.pi*(s.vars[c*3] ** 2 ) )
		    xn = s.vars[c*3+1] - s.vars[c*3] 
		    xp = s.vars[c*3+1] + s.vars[c*3] 
		    yn = s.vars[c*3+2] - s.vars[c*3] 
		    yp = s.vars[c*3+2] + s.vars[c*3]    
            
		    if  xn < 0 :
		         pass
		    elif xp > self.gridx : 
		         pass            
		    elif yn < 0  :
		         pass            
		    elif yp  > self.gridy  :
		         pass		       
                
        # está sobredimensionado el cálculo de la intercepción                                            
		    
	        
		overlaparea = 0    
		for c in range(s.nVar//3 - 1):			
		    for i in range(c + 1, s.nVar//3 ): 
		         rm = s.vars[c*3]    
		         cd = 0
		         if  rm < s.vars[i*3] :    
		             rm = s.vars[i*3]
		             cd = 1 
		         dm = math.sqrt(s.vars[i*3]**2 + s.vars[c*3]**2)   
		         if  rm <= dm :
		             if  cd == 0 :
		                 overlaparea = overlaparea + math.pi*(s.vars[i*3] ** 2 )
		             else :    
		                 overlaparea = overlaparea + math.pi*(s.vars[c*3] ** 2 )  
		         else :   
		             if  cd == 0 :
		                 overlaparea = overlaparea +  2*(s.vars[c*3] ** 2 + s.vars[c*3]*s.vars[i*3] - dm)
		             else :    
		                 overlaparea = overlaparea +  2*(s.vars[i*3] ** 2 + s.vars[c*3]*s.vars[i*3] - dm)
                     
		                             
		## print(cover)                    
		## print(overlap)   
		## print(redundant)
		## print(outdeployment)        
		## print(overlaparea)                 
        # Overlapping of the reading area
        # Revisar para implementar la interferencia, por ahora, 
        # sólo maximizar el área
# =============================================================================
# 		e = 0
# 		f1 = 1/(1+e**2) 
# 		f.append(f1) 
# =============================================================================
		ee = 0.0
	
		g = sum(area)
		if g == 0:
			g = 0.00001  
		## print("..." +str(e) + " " +str(overlaparea))
		## print(area)
		## print(g)        
		## print(overlaparea)        
		# for c in range(s.nVar//3):      
		#     e = e - area[c]  
		# e = e - overlaparea
		ee =  overlaparea / g  
		f1 = 1/(1+ee**2) 

		target = 100 * ee
		f1 = 1/(1+target)   
		f.append(round(f1, 4))
        
        
        # ** Number of useless readers 
		e = 0
		for c in range(s.nVar//3):        
		    if (len(v[c]) == 0) :
		        e = e + 1 
		f2 = 1/(1+e**2)  
        
		target = 100 * e /(s.nVar//3)
		f2 = 1/(1+target)   
		f2 = 0      
		# print(e)   
		f.append(round(f2, 4))  
        
        # ** Number of tags covered
		# e = len(self.rfid) - len(cover)       
		e = (len(self.rfid) - len(cover) )/len(self.rfid)
		f3 = 1/(1+e**2) 
        
		target = 100 * len(cover) /len(self.rfid)
		f3 = 1/(1 + 100 -target)        
		# print(e)
		f.append(round(f3, 4))   
        
        # Number of readers located out of the deployment area
		e = len(outdeployment) 
		f4 = 1/(1+e**2)  
        
		target = 100 * len(outdeployment) /(s.nVar//3)
		f4 = 1/(1 + target)
		f4 = 0
		f.append(round(f4, 4))   
        
        # ** Number of redundant readers
		e = len(redundant)
		f5 = 1/(1+e**2) 
        
		target = 100 * len(redundant)/(s.nVar//3)
		f5 = 1/(1 + target)
		f.append(round(f5, 4))    
        
        # ** Number of tags located in overlapped reading areas
		e = len(overlap) 
		f6 = 1/(1+e**2) 
        
		target = 100* len(overlap)/len(self.rfid)
		f6 = 1/(1 + target)
		f.append(round(f6, 4))        
        
        # ** Number of tags located in overlapped reading areas
		target = 0
		for c in range(s.nVar//3):
		    target = target + area[c]/(len(v[c]) + 1)
            
		e = len(overlap) 
		f7 = 1/(1+e**2)  
        
		f7 = 1/(1+target)
		f.append(round(f7, 4))
        
        
        #         
		for c in range(7):
		    fitness = fitness + self.w[c]*f[c] 
            
		print(f ) 	
		## print(self.w ) 	
		## print(fitness ) 
        
		s.setFitness(fitness)  
        
        
        
	def printgrid(self, s):
		"""  
		@param state.Solution s : 
		@return  :
		@author
		""" 

		# s = [6, 12, 5, 8, 6, 9, 6, 7.5, 15]  
        
		plt.figure()
		ax = plt.gca()
		xr = []
		yr = []        
		# for a, b, color, size in zip(x, y, colors, s):
    		# plot circles using the RGBA colors
		for c in range(s.nVar//3):
		    circle = plt.Circle( (s.vars[c*3 + 1], s.vars[c*3 + 2]) , s.vars[c*3], color='blue', fill=False) 
		    ax.add_artist(circle)
		    xr.append(s.vars[c*3 + 1])
		    yr.append(s.vars[c*3 + 2])
		# plt.plot(circle)
		ax.set_aspect(1.0)
        
		xx = []
		yy = [] 
		for i in range(len(self.rfid) ):
		    r = self.rfid[i] 
		    xx.append( r[0] ) 
		    yy.append( r[1] ) 
            
		plt.plot(xx, yy, "gx",  xr, yr, "rx")   
		# print(xx)         
        
		plt.title('Network Topology Design')
		plt.xlim(-0.5, self.gridx + 0.5)
		plt.ylim(-0.5, self.gridy + 0.5) 
		plt.xlabel("x")
		plt.ylabel("y")     
		plt.grid(True)     
		plt.show()  

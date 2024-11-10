import numpy as np
import math
import copy

from operators.OperatorsGeneric import *

class OperatorsPerm(OperatorsGeneric):

	"""
	:version:
	:author:
	"""

	def __init__(self, typeProblem):
		""" 
		@param String m : 
		@return String :
		@author
		"""
		super().__init__(typeProblem)
		# self.typeProblem = typeProblem
		  

	def mutationSwapping(self, sol):
		u = copy.deepcopy(sol) 
		  
		t1 = np.random.randint(sol.nVar)
		t2 = np.random.randint(sol.nVar)
			
		while (t1 == t2):
			t2 = np.random.randint(sol.nVar)
	 
		aux = u.vars[t1]  
		u.vars[t1] = u.vars[t2] 
		u.vars[t2] = aux  
		  
		return u
	
	
	def mutation(self, name, sols):
		if name == 'SWAPPING':
			solx = self.mutationSwapping(sols[0])
		# 	elif name == 'BASIC2':
		# 		solx = self.mutationSimple2(sols[0])	
		else: 
			raise ValueError("This mutation method is not defined: "+name)
		return solx


	def crossoverAlternatingPosition(self, s1, s2):  
		# 	s1.prints("s1")
		# 	s2.prints("s2")
		elements = [] 

		j=0 
		remElems = list(s1.vars)
        

		while  len(remElems) > 0 :
 			elemSol1 = s1.vars[j]  
 			elemSol2 = s2.vars[j]  
 			 
 			if elemSol1 in remElems :
 				elements.append(elemSol1) 
# 				indices = np.where(remElems==elemSol1)
# 				remElems = np.delete(remElems, indices)
 				remElems.remove(elemSol1) 
                 
 			 
 			if elemSol2 in remElems :
 				elements.append(elemSol2) 
# 				indices = np.where(remElems==elemSol2)
# 				remElems = np.delete(remElems, indices)
 				remElems.remove(elemSol2) 
 			 
 			j = j + 1

	
# =============================================================================
# 		while  len(elements) < s1.nVar :
# 			elemSol1 = s1.vars[j]  
# 			elemSol2 = s2.vars[j]  
# 			 
# 			if elemSol1 in elements :
# 				pass
# 			else :
# 				elements.append(elemSol1) 
# 			 
# 			if elemSol2 in elements :
# 				pass
# 			else :
# 				elements.append(elemSol2) 
# 			 
# 			j = j + 1
# =============================================================================
		# print(s1.nVar)		
		# print(len(elements)	)
		i1 = copy.deepcopy(s1) 
		i1.vars = elements 
		
		return [ i1 ]  
    
    
	def crossoverOrder(self, s1, s2):  
		# Se seleccionan  dos posiciones aleatorias, se intercambian y
        # luego se complementan con con los otros genes del otro padre
		# s1.prints("s1")
		# s2.prints("s2")
		lv = np.random.randint(s1.nVar)
		uv = np.random.randint(s1.nVar)
		while uv < lv:
			uv = np.random.randint(s1.nVar)
		#print(lv, uv)
		elements = []
		nelements = []        
		for i in range(s1.nVar):
			if i<lv or i>uv:
				elements.append("")
				nelements.append(s1.vars[i])
			else:
				elements.append(s1.vars[i])

		for i in range(s2.nVar):
			if s2.vars[i] in nelements: 
				for j in range(s1.nVar):
					if elements[j] == "":
						elements[j] = s2.vars[i] 
						nelements.remove(s2.vars[i])
						break 

		# print(elements)
		i1 = copy.deepcopy(s1)
		i1.vars = elements

		return [ i1 ]
    
    
	def crossoverPartiallyMatched(self, s1, s2):  
		# s1.prints("s1")
		# s2.prints("s2")
		lv = np.random.randint(s1.nVar)
		uv = np.random.randint(s1.nVar)
		while uv < lv:
			uv = np.random.randint(s1.nVar)

		# offspring2 = list(s1.vars)   
		offspring1 = list(s2.vars) 
 
		genSelectToOffsp1 = [] 
		genSelectToOffsp2 = []
		valuesNoTaken = []
#		print(offspring1)    
#		print(lv, uv)    
        
		for i in range(s1.nVar):
			if i<lv or i>uv:
				valuesNoTaken.append(offspring1[i] )
				offspring1[i] = "" 
			else:
				if s2.vars[i] != s1.vars[i]:
					genSelectToOffsp1.append(s2.vars[i])
					genSelectToOffsp2.append(s1.vars[i]) 
		
                     
		f  = 0            
		while f<len(genSelectToOffsp1):  
			v = len(genSelectToOffsp1)   
			b = True                  
			for i in range(f+1,v):
				if genSelectToOffsp2[f]==genSelectToOffsp1[i] and genSelectToOffsp1[f]==genSelectToOffsp2[i]:
					genSelectToOffsp1.pop(i) 
					genSelectToOffsp2.pop(i)       
					genSelectToOffsp1.pop(f) 
					genSelectToOffsp2.pop(f)                      
					b=False
					break
                    
			if b==True:
				f  = f  +1
                        
#		print(offspring1)   
#		print(genSelectToOffsp1)
#		print(genSelectToOffsp2)           
#		print("valuesNoTaken", valuesNoTaken)               
#		print()               
		genSelectAux1 = copy.deepcopy(genSelectToOffsp1)   
		genSelectAux2 = copy.deepcopy(genSelectToOffsp2)   
        
		for i in range(s1.nVar):
			if offspring1[i] == "":
				if s1.vars[i] in genSelectAux1:  
					vaa = s1.vars[i]
					p1 = genSelectAux1.index(vaa)  
					valx = genSelectAux2[p1]  
					
					while not valx in valuesNoTaken:
						vaa = genSelectAux2[p1]
						p1 = genSelectAux1.index(genSelectAux2[p1])  
						valx = genSelectAux2[p1]  
#						print(vaa, "-->", valx) 
                            
					offspring1[i] = genSelectAux2[p1] 
					valuesNoTaken.remove(genSelectAux2[p1])
                    
					genSelectAux1.remove(vaa) 
					genSelectAux2.pop(p1) 
#					print("val", val)                    
#					print("genSelectAux1", genSelectAux1)   
#					print("genSelectAux2", genSelectAux2)   
#					print(offspring1)         
#					print()   
				else:
					offspring1[i] =  s1.vars[i]  

        
		# print(elements)
		i1 = copy.deepcopy(s1)
		i1.vars = offspring1

		return [ i1 ]            
            

	def crossoverCycle(self, s1, s2):  
		# CX     
		offspring1 = list(s1.vars)     
		offspring2 = list(s2.vars) 

		parent =1 
		cycles = []  
		cycle2 = []
		pos = []    
        
		cycleupd = []
		same =[]   
        
		for i in range(s1.nVar):
			if offspring1[i] == offspring2[i]:
				cycleupd.append(i)
				cycle2.append(cycleupd) 
				same =same +cycleupd
				cycleupd = []               
			else:                 
				pos.append(i) 
     
		upd = pos[0] 
		pos.remove(upd)
		initC = s1.vars[upd]  
		cycleupd.append(upd)
        
    
		#print("pos", pos)                    
		#print("cycleupd", cycleupd)   
		#print("upd", upd)   
		#print("initC", initC)           
#		k=10     
        
#		while len(pos) > 0  and  k>0: 
#			k=k-1

        
		while len(pos) > 0 :        
			if parent == 1:
				if len(cycleupd) == 0  :
					#print("1 1" )        
					upd = pos[0]  
					initC = offspring1[upd]     
					cycleupd.append(upd)
					pos.remove(upd)   
				elif initC == offspring2[upd]:
					#print("1 2" )        
					cycles.append(cycleupd) 
					same =same +cycleupd
					cycleupd = []          
					parent = 2
				else:    
					#print("1 3" )   					
					dv = upd
					upd = offspring1.index(offspring2[upd]) 					
					if upd in cycleupd or upd in same: 
						for i in range(len(pos)):   
							#print("i", i) 
							#print("dv", dv) 
							if pos[i]>upd and offspring1[pos[i]] == offspring2[dv]:
								upd = pos[i]  
								break 
					#print("upd", upd) 
					cycleupd.append(upd)
					#print("cycleupd", cycleupd)  
					pos.remove(upd) 
			else:
				if len(cycleupd) == 0 :
					#print("2 1" )                     
					upd = pos[0]  
					initC = offspring2[upd]       
					cycleupd.append(upd)
					pos.remove(upd) 
				elif initC == offspring1[upd] :
					#print("2 2" )        
					cycles.append(cycleupd) 
					same =same +cycleupd
					cycleupd = []          
					parent = 1
				else:     
					#print("2 3" )    					
					dv = upd
					upd = offspring2.index(offspring1[upd])
					if upd in cycleupd or upd in same:     
						for i in range(len(pos)):   
							#print("i", i) 
							#print("dv", dv) 
							if pos[i]>upd and offspring2[pos[i]] == offspring1[dv]:
								upd = pos[i]  
								break                    
					#print("upd", upd) 
					cycleupd.append(upd)
					#print("cycleupd", cycleupd)  
					pos.remove(upd) 
                    
			#print("pos", pos)                    
			#print("cycleupd", cycleupd)                    
			#print("cycles", cycles)   
			#print("upd", upd)   
			#print("initC", initC)         
			#print()     
		cycles.append(cycleupd)   
		cycles  = cycles + cycle2 
		# print(cycles)          
         
		for i in range(1, len(cycles), 2):
			for j in range(len(cycles[i])): 
				f = cycles[i][j]
				offspring1[f] = s2.vars[f]       
		# print(elements)
		i1 = copy.deepcopy(s1)
		i1.vars = offspring1

		return [ i1 ]        

	def crossoverOrderBased(self, s1, s2):   
		# OX2     
		pass    

	def crossoverPositionBased(self, s1, s2):    
		# POS     
		val = []     
		pos = []
		offspring1 = []
		for i in range(s1.nVar):  
			v = np.random.randint(2)
			if v == 1:    
				pos.append(i)    
				val.append(s2.vars[i]) 
                
		# print("pos", pos)  
		# print("val", val)		      
		offspring1 = list(s2.vars)    
		offspring2 = list(s1.vars)   
		ring1 = copy.deepcopy(offspring2)    
                
		for i in range(s1.nVar):
			if not i in pos:   
				j=0                
				while len(ring1) > j :#for j in range(len(ring1)):
					# print("ring1", ring1)  
					# print("val", val)
					v = ring1[j]                    
					if ring1[j] in val: 

						ring1.pop(j)
						val.remove(v)
					else:    
                        
						offspring1[i] = ring1[j] 
						ring1.pop(j)                        
						break         
                
		i1 = copy.deepcopy(s1)
		i1.vars = offspring1

		return [ i1 ]         

	def crossoverVotingRecombination(self, s1, s2):    
		# VR     
		pass 

	def crossoverSequentialConstructive(self, s1, s2):    
		# SCX    
		pass
        
	def crossover(self, name, sols):
		# print(name)        
		if name =='APX': 
			solx = self.crossoverAlternatingPosition(sols[0], sols[1])
		elif name =='PMX':
			solx = self.crossoverPartiallyMatched(sols[0], sols[1])            
		elif name =='OX':
			solx = self.crossoverOrder(sols[0], sols[1])            
		elif name =='CX':
			solx = self.crossoverCycle(sols[0], sols[1])
		elif name =='POS':
			solx = self.crossoverPositionBased(sols[0], sols[1])
		else: 
			raise ValueError("This crossover method is not defined: "+name)
		return solx
				 
		
		
 
 
		

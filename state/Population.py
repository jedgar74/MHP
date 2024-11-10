from state.Solution import *

class Population(object):  
	
	def __init__(self, popSize, problem, init="RANDOM" ):
		""" 
		@return:
		@author
		""" 
		self.popSize = popSize
		self.typeProblem = problem.typeProblem
		self.generateRandom(problem, init) 
		
		
	def generateRandom(self, problem, init):	
		self.popul = []
		
		for i in range(self.popSize):
			f = Solution(problem, init) 
			problem.evaluate(f)
			# This instruction allows to print the generated solution
			# f.prints()
			self.popul.append(f)
		
		
	def sort(self):	
		size = self.popSize

		for i in range(1, size) :  
			for j in range(size - 1) : 
				if (self.typeProblem == "MIN" and self.popul[j].fitness > self.popul[j+1].fitness) :
					aux = self.popul[j]
					self.popul[j] = self.popul[j+1]
					self.popul[j+1] = aux 
				if (self.typeProblem == "MAX" and self.popul[j].fitness < self.popul[j+1].fitness) :
					aux = self.popul[j]
					self.popul[j] = self.popul[j+1]
					self.popul[j+1] = aux 
		
		
	def getBetterSort(self): 
		return self.popul[0]   
		
    
	def indexBetter(self): 
		index = 0
		fitness = self.popul[0].fitness
		
		for i in range(1, self.popSize) : 
				if (self.typeProblem == "MIN" and self.popul[i].fitness < self.popul[j+1].fitness) :
					index = i
					fitness = self.popul[i].fitness 
				if (self.typeProblem == "MAX" and self.popul[i].fitness > self.popul[j+1].fitness) :
					index = i
					fitness = self.popul[i].fitness 
									
		return index
		
				
	## 	Si la variable expansión es true Entonces se permite que el tamaño de la 
	## 	población varíe. En caso contrario el tamaño de la población se mantiene 
	## 	constante y si no es mejor la nueva solución que algún individuo de la 
	## 	población existente no se agrega		
	def addSort(self, insolution, expansion = False ) :
		isBetter = False  
		lenpop = len(self.popul)
		
		for t in range(self.popSize): 
			if (self.typeProblem == "MIN" and insolution.fitness < self.popul[t].fitness )  :
				self.add(t, insolution);  
				isBetter = True;
				break 
				
			if (self.typeProblem == "MAX" and insolution.fitness > self.popul[t].fitness )  :
				self.add(t, insolution);  
				isBetter = True;
				break 	
				
		if expansion == True :		
			if isBetter == False :
				self.popul.append(insolution);
				# self.popSize = len(self.popul)
				# self.add(t, insolution) 
		else :
			if isBetter == True :
				self.popul.pop(lenpop)
				# self.popSize = len(self.popul)	 		
		# 	self.popul.append(insolution)  			
		# 	self.popSize = len(self.popul)
		# self.printFitness(str (len(self.popul)) )
		self.popSize = len(self.popul) 





	def add(self, index, insolution) :
		self.popul.insert(index, insolution);
		self.popSize = len(self.popul)


	def printFitness(self, label) : 
		print("--> " + label + " ", end="")
		
		for i in range(self.popSize): 
			print( str(round(self.popul[i].fitness, 3)) + " ", end = "") 
		
		print("\n") 


	def getIndividual(self, l):  
		return self.popul[l]  


	def removeIndividual(self, l):  
		self.popul.pop(l)
		self.popSize = len(self.popul) 	
				
        
	def removeAll(self): 
		self.popul = []
		self.popSize = 0
		
        
	def addPop(self, popc, nc) : 
		for i in range(nc): 
			# print(popc.getIndividual(i)) 
			self.popul.append(popc.getIndividual(i))
		self.popSize = len(self.popul)
	
	# def copy(self, popc): 
	# 	self.popul = []
	# 	for i in range(popc.popSize): 
	# 		popc.getIndividual(i).prints() 
	# 		self.popul.append(popc.getIndividual(i))
	# 	self.popSize = len(self.popul)

	 
	def contains(self, insolution ) : 
		isContains = False
		for t in range(self.popSize): 
			if self.popul[t].isEquals(insolution) : 
				isContains = True 
				break  
				
		return isContains
		
		
	def totalFitness(self) : 
		sums=0 
		for t in range(self.popSize): 
			sums = sums + self.popul[t].fitness
				
		return sums
	
    
	def prints(self) :  
		
		for i in range(self.popSize): 
			self.popul[i].prints()
		
		print("\n")  

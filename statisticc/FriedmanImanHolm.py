from datetime import datetime, date, time, timedelta
import calendar 
import numpy as np 
import matplotlib.pyplot as plt
#  from scipy.stats import friedmanchisquare
from scipy.stats import chi2
from scipy.stats import f
from scipy.stats import norm
import math 
#  
#  name: desconocido
#  @param
#  @return
#  
# 
# Tiene como entrada una matrix 
#  
#  Algor1 Algor2 ... AlgorK
#  x x ... x
#  x x ... x
#  ...
#  x x ... x
#  
#  Where N represent the number of experiments y K represent the algorithms
 
class FriedmanImanHolm():
	# String nameFile 
	# labels = new Vector<String>()
    # String self.info 
	# Matrix values 
	# boolean graph =false
	# alpha = 0.05
    # decimal = 4 
     
	def __init__(self, nTopAlgorithms=None): 
		super().__init__()
		self.nTopAlgorithms = nTopAlgorithms  
		self.info = ""
		self.alpha = 0.05
		self.decimal = 4
		self.graph = False
		self.bphor = False


	def  minProblem(self ):  
		# System .out.println("\n*******        Jhon Edgar Amaya         *******")
		ahora = datetime.now()  # Obtiene fecha y hora actual 	 
		nameFile = str(ahora.day) +"_"+ str(ahora.month) +"_"+ str(ahora.year) +"_"+ str(ahora.hour) +"_"+ str(ahora.minute) +".txt"
			 
		# Read File 
		# self.values.getRow()  len(self.values)
		# self.values.getCol()  len(self.values[0])
		K = len(self.values[0])
		N = len(self.values)
					
		# # System .out.println("***********************************************")
		# # System .out.println("******* ALG : "+K+ " --- INST : "+N+" *****")
		# # System .out.println("***********************************************")
		# # System .out.print(Terminal.title("ALG : " + K + " --- INST : " + N)) 
		# System .out.print("\nAlgorithms : "+K+ "  ---  Instances : "+N+"\n"  + Terminal.separator())
			 
		self.info = self.info + "\nAlgorithms : "+str(K)+ " --- Instances : "+str(N)+"\n"
		self.info = self.info + self.separator()
			
		# Create matrix values 
		# values.printlnAll()

		# Calculate Rank
		ranks = np.zeros(shape=(N, K)) # Matrix(N, K)
		indexRanking = [] 
		selectedRank = []
		# print(K)
		# print(N)
		for j in range(len(self.values)): #for (j = 0 j < len(self.values) j++): 
			for g in range(len(self.values[0])): #for (g = 0 g < len(self.values[0]) g++):
				indexRanking.append(g) 
			ranking = 1

			while(len(indexRanking) != 0): 
				minv = 1e40

				for g in range(len(indexRanking)): #for (g = 0 g < indexRanking.size() g++): 
					tmpx = self.values[j][indexRanking[g]]
 
					if (tmpx < minv):
						selectedRank = []
						minv = tmpx
						selectedRank.append(indexRanking[g])
					elif (tmpx == minv):
						selectedRank.append(indexRanking[g])
						
					
				rankTemp = (len(selectedRank) + 2 * ranking - 1) / 2
				# # System .out.println(""+ranking+"---"+selectedRank.size()+"..."+rankTemp)
				ranking = ranking + len(selectedRank)

				for g in range(len(selectedRank)): #for (g = 0 g < selectedRank.size() g++): 
					#print(selectedRank[g])
					ranks[j][selectedRank[g]]  =  rankTemp  
				for g in range(len(selectedRank)): #for (g = 0 g < selectedRank.size() g++):
					rs = indexRanking.index(selectedRank[g])
					indexRanking.pop(rs)					 
				 

		# System .out.println()
		#  # System .out.println("***********************************************")
		#  # System .out.println("*** RANKS IN THE MATRIX ***********************")
		#  # System .out.println("***********************************************")
		# System .out.print(Terminal.title("RANKS MATRIX"))
			
		self.info = self.info + "\nRanks Matrix   \n"
		self.info = self.info + self.separator() 
        
		self.info = self.info +  str(ranks)   + "\n"
			 
		#  prmatrix of ranks
		#fff  genMatrix(ranks, nameFile, "Rank_", labels)  # / Esto es nuevo!!!!!!!!!!!!!!!
		#fff  ranks.printlnAll()
		#fff  self.info = self.info + ranks.toString()

		#  stat, p = friedmanchisquare(self.values[:,0], self.values[:,1], self.values[:,2], self.values[:,3], self.values[:,4])
		#  print('Statistics=%.3f, p=%.3f' % (stat, p))
		#  valuec = chi2.ppf(1-self.alpha, K-1)
		#  print(valuec)
		#  valuec = f.ppf(1-self.alpha, K-1, (K-1)*(N-1))
		#  print(valuec)
		# Calculate Friedman
		vFriedman = self.friedmanT(ranks, N, K)

		# Calculate Iman 
		vIman = self.imanDavenportT(vFriedman, N, K)	

		labelsHolm = []
		for g in range(len(self.labels)): #for (g = 0 g < labels.size() g++):
			labelsHolm.append(self.labels[g])
			
		# Calculate Holm
		self.holmT(ranks, N, K, labelsHolm)
        
		if (self.nTopAlgorithms == None):
			
			if (self.graph):
				self.sortMatrix(ranks, self.labels) 
				tmp = np.zeros(len(self.labels)) 
				for i in range(len(self.labels)):  
					tmp[i] = i +1
				fig=plt.figure(1, figsize=(9,6))
				ax=fig.add_subplot(111)
				# ax.boxplot(to_plot)
				bbox_props = dict(color="b")
				line_props = dict(linestyle="--")
				if self.bphor == False:
					ax.boxplot(ranks, whiskerprops=line_props, boxprops=bbox_props)
					plt.xlabel("algorithms")
					plt.ylabel("ranks") 
					plt.xticks(tmp, self.labels)
				else :
					# ax.boxplot(ranks, vert=False)
					ax.boxplot(ranks, vert=False, whiskerprops=line_props, boxprops=bbox_props)
					plt.ylabel("algorithms")
					plt.xlabel("ranks") 
					plt.yticks(tmp, self.labels)	 
	 
				plt.show()				
				
 
			 
				# self.sortMatrix(ranks2, labelsTopAlg)
				# BoxPlotGraph demf = new BoxPlotGraph("", ranks2.getMatrix(), labelsTopAlg)
				# demf.pack() 
				# demf.setVisible(true)
				
		elif (self.nTopAlgorithms < 3):
			print("The minimum values must be 3 top algorithms")
		else :
			 
			# ____________________________________________________

			exxR = []
			dddR = []
			labelsTopAlg = []

			for j in range(len(self.labels)): #for (j = 0 j < labels.size() j++):
				labelsTopAlg.append(self.labels[j])
				

			for j in range(len(ranks[0])): #for (j = 0 j < ranks.getCol() j++):
				dddR.append( j )
				dff = 0.0
				for g in range(len(ranks)): #for (g = 0 g < ranks.getRow() g++): 
					dff = dff + ranks[g][j]
				
				exxR.append(dff)
			

			# ordenar
			for j in range(len(dddR)): #for (j = 0 j < dddR.size()  j++):
				minm = exxR[j]
				for g in range(len(dddR)): #for (g = 0 g < dddR.size() g++):

					if  minm <  exxR[g]  :
						trxx = labelsTopAlg[j]
						trxy = labelsTopAlg[g]
						labelsTopAlg[j] = trxy 
						labelsTopAlg[g] = trxx 
						trxx2 = dddR[j]
						trxy2 = dddR[g]
						dddR[j] = trxy2 
						dddR[g] = trxx2 
						trxx3 = exxR[j]
						trxy3 = exxR[g]
						exxR[j] = trxy3 
						exxR[g] = trxx3 
						minm = exxR[g]
					 

			# for (j = 0  j < dddR.size() j++):
			# System .out.println("alg = "+ dddR.elementAt(j)+" - "+ Maths.rounds(Double.parseDouble(exxR.elementAt(j)), decimal)  + " - "+ labelsTopAlg.elementAt(j))
			Ktop = self.nTopAlgorithms # indicate number algorithm
			# /*Ntop = lines.size() - 1*/ # indicate number experiments
			Ntop = len(self.values)
			# Create matrix values
			values2 = np.zeros(shape=(Ntop, Ktop)) #Matrix(Ntop, Ktop)
			# values2.printlnAll()

			# llenar values2
			for j in range(Ktop): #for (j = 0 j < Ktop j++):
				for g in range(Ntop): #for (g = 0 g < Ntop g++): 
					values2[g][j] =  self.values[g][dddR[j]] 
	 		

	
			# Calculate Rank
			ranks2 = np.zeros(shape=(Ntop, Ktop)) # = Matrix(Ntop, Ktop)
			indexRanking2 = []
			selectedRank2 = []
			
			for j in range(len(values2)): #for (j = 0 j < values2.getRow() j++):
				for g in range(len(values2[0])): #for (g = 0 g < values2.getCol() g++):
					indexRanking2.append(g)
				 
				ranking = 1

				while(len(indexRanking2) != 0):
					minv = 1e40

					for g in range(len(indexRanking2)): # for (g = 0 g < indexRanking2.size() g++):
						
						tmpx = values2[j][indexRanking2[g]]   
						if (tmpx < minv):
							selectedRank2 = []
							minv = tmpx
							selectedRank2.append(indexRanking2[g])
						elif (tmpx == minv):
							selectedRank2.append(indexRanking2[g])
						
					
					rankTemp = (len(selectedRank2) + 2*ranking - 1)/2
					# # System .out.println(""+ranking+"---"+selectedRank.size()+"..."+rankTemp)
					ranking=ranking + len(selectedRank2)

					for g in range(len(selectedRank2)): # for (g = 0 g < selectedRank2.size() g++): 
						ranks2[j][selectedRank2[g]] =  rankTemp 
					

					for g in range(len(selectedRank2)): #for (g = 0 g < selectedRank2.size() g++):
						rs = indexRanking2.index(selectedRank2[g])
						indexRanking2.pop(rs)						
						# ranks.setMatrix(j, Integer.parseInt(selectedRank[g]), rankTemp)
					

			 
			
			# System .out.println()
			# # System .out.println("***********************************************")
			# # System .out.println("*** VALUES IN THE MATRIX **********************")
			# # System .out.println("***********************************************")
			# System .out.print(Terminal.title("MATRIX TOP ALGORITHMS"))
			
			self.info = self.info + "\nTop Algorithms "+str(self.nTopAlgorithms)+"\n"
			self.info = self.info + self.separator()  
			 
			# values2.printlnAll()
			
			# # System .out.println("***********************************************")
			# # System .out.println("*** RANKS IN THE MATRIX ***********************")
			# # System .out.println("***********************************************")
			# System .out.print(Terminal.title("RANKS MATRIX"))
			
			self.info = self.info + "\nRanks Matrix   \n"
			self.info = self.info + self.separator()
			 

			if (len(labelsTopAlg) > self.nTopAlgorithms):				
				while (len(labelsTopAlg) > self.nTopAlgorithms):
					labelsTopAlg.pop(len(labelsTopAlg)-1)
			 

			# genMatrix(ranks2, nameFile, "RankTop_", labelsTopAlg)  # / Esto es nuevo!!!!!!!!!!!!!!!
			# ranks2.printlnAll()
			# self.info = self.info + ranks2.toString()
			
			
			# Calculate Friedman
			vFriedman = self.friedmanT(ranks2, Ntop, Ktop)  

			# Calculate Iman   
			vIman = self.imanDavenportT(vFriedman, Ntop, Ktop)	 

			# Calculate Holm
			self.holmT(ranks2, Ntop, Ktop, labelsTopAlg) 

			
			if (self.graph):
				self.sortMatrix(ranks, self.labels) 
				tmp = np.zeros(len(self.labels)) 
				for i in range(len(self.labels)):  
					tmp[i] = i +1
				fig=plt.figure(1, figsize=(9,6))
				ax=fig.add_subplot(111)
				# ax.boxplot(to_plot)
				
				bbox_props = dict(color="b")
				line_props = dict(linestyle="--")
				if self.bphor == False:
					ax.boxplot(ranks, whiskerprops=line_props, boxprops=bbox_props)
					plt.xlabel("algorithms")
					plt.ylabel("ranks") 
					plt.xticks(tmp, self.labels)
				else :
					# ax.boxplot(ranks, vert=False)
					ax.boxplot(ranks, vert=False, whiskerprops=line_props, boxprops=bbox_props)
					plt.ylabel("algorithms")
					plt.xlabel("ranks") 
					plt.yticks(tmp, self.labels)	 
						
				plt.show()	
			 
				# self.sortMatrix(ranks2, labelsTopAlg)
				# BoxPlotGraph demf = new BoxPlotGraph("", ranks2.getMatrix(), labelsTopAlg)
				# demf.pack() 
				# demf.setVisible(true)
				
				self.sortMatrix(ranks2, labelsTopAlg) 
				tmp = np.zeros(len(labelsTopAlg)) 
				for i in range(len(labelsTopAlg)):  
					tmp[i] = i +1
				fig=plt.figure(1, figsize=(9,6))
				ax=fig.add_subplot(111)
				# ax.boxplot(to_plot)
				bbox_props = dict(color="b")
				line_props = dict(linestyle="--")
				if self.bphor == False:
					ax.boxplot(ranks2, whiskerprops=line_props, boxprops=bbox_props)
					plt.xlabel("algorithms")
					plt.ylabel("ranks") 
					plt.xticks(tmp, labelsTopAlg)
				else :
					# ax.boxplot(ranks, vert=False)
					ax.boxplot(ranks2, vert=False, whiskerprops=line_props, boxprops=bbox_props)
					plt.ylabel("algorithms")
					plt.xlabel("ranks") 
					plt.yticks(tmp, labelsTopAlg)	 
	 
				plt.show()
			
 
				# /*
				#  * I include methods to generate boxplot in Matlab. First, sort columns 
				#  * for median and media. Second, generate the files *.m     
				#  */

				# genFilesMatlab( "Rank_", ranks, labels)
				# genFilesMatlab( "RankTop_", ranks2, labelsTopAlg)
			
			
			
	def maxProblem(self ):
		# System .out.println("\n*******        Jhon Edgar Amaya         *******")
		ahora = datetime.now()  # Obtiene fecha y hora actual 	 
		nameFile = str(ahora.day) +"_"+ str(ahora.month) +"_"+ str(ahora.year) +"_"+ str(ahora.hour) +"_"+ str(ahora.minute) +".txt"
			 
		# Read File 
		# self.values.getRow()  len(self.values)
		# self.values.getCol()  len(self.values[0])
		K = len(self.values[0])
		N = len(self.values)
					
		# # System .out.println("***********************************************")
		# # System .out.println("******* ALG : "+K+ " --- INST : "+N+" *****")
		# # System .out.println("***********************************************")
		# # System .out.print(Terminal.title("ALG : " + K + " --- INST : " + N)) 
		# System .out.print("\nAlgorithms : "+K+ "  ---  Instances : "+N+"\n"  + Terminal.separator())
			 
		self.info = self.info + "\nAlgorithms : "+str(K)+ " --- Instances : "+str(N)+"\n"
		self.info = self.info + self.separator()
			
		# Create matrix values 
		# values.printlnAll()

		# Calculate Rank
		ranks = np.zeros(shape=(N, K)) # Matrix(N, K)
		indexRanking = [] 
		selectedRank = []
		# print(K)
		# print(N)
		for j in range(len(self.values)): #for (j = 0 j < len(self.values) j++): 
			for g in range(len(self.values[0])): #for (g = 0 g < len(self.values[0]) g++):
				indexRanking.append(g) 
			ranking = 1

			while(len(indexRanking) != 0): 
				maxv = 1e-40 

				for g in range(len(indexRanking)): #for (g = 0 g < indexRanking.size() g++): 
					tmpx = self.values[j][indexRanking[g]]
 
					if (tmpx > maxv):
						selectedRank = []
						maxv = tmpx
						selectedRank.append(indexRanking[g])
					elif (tmpx == maxv):
						selectedRank.append(indexRanking[g])
						
					
				rankTemp = (len(selectedRank) + 2 * ranking - 1) / 2
				# # System .out.println(""+ranking+"---"+selectedRank.size()+"..."+rankTemp)
				ranking = ranking + len(selectedRank)

				for g in range(len(selectedRank)): #for (g = 0 g < selectedRank.size() g++): 
					#print(selectedRank[g])
					ranks[j][selectedRank[g]]  =  rankTemp  
				for g in range(len(selectedRank)): #for (g = 0 g < selectedRank.size() g++):
					rs = indexRanking.index(selectedRank[g])
					indexRanking.pop(rs)					 
				 

		# System .out.println()
		#  # System .out.println("***********************************************")
		#  # System .out.println("*** RANKS IN THE MATRIX ***********************")
		#  # System .out.println("***********************************************")
		# System .out.print(Terminal.title("RANKS MATRIX"))
			
		self.info = self.info + "\nRanks Matrix   \n"
		self.info = self.info + self.separator() 
        
		self.info = self.info +  str(ranks)   + "\n"
		#  prmatrix of ranks
		#fff  genMatrix(ranks, nameFile, "Rank_", labels)  # / Esto es nuevo!!!!!!!!!!!!!!!
		#fff  ranks.printlnAll()
		#fff  self.info = self.info + ranks.toString()

		#  stat, p = friedmanchisquare(self.values[:,0], self.values[:,1], self.values[:,2], self.values[:,3], self.values[:,4])
		#  print('Statistics=%.3f, p=%.3f' % (stat, p))
		#  valuec = chi2.ppf(1-self.alpha, K-1)
		#  print(valuec)
		#  valuec = f.ppf(1-self.alpha, K-1, (K-1)*(N-1))
		#  print(valuec)
		# Calculate Friedman
		vFriedman = self.friedmanT(ranks, N, K)

		# Calculate Iman 
		vIman = self.imanDavenportT(vFriedman, N, K)	

		labelsHolm = []
		for g in range(len(self.labels)): #for (g = 0 g < labels.size() g++):
			labelsHolm.append(self.labels[g])
			
		# Calculate Holm
		self.holmT(ranks, N, K, labelsHolm)
	
    
		if (self.nTopAlgorithms == None):
			if (self.graph):
				self.sortMatrix(ranks, self.labels) 
				tmp = np.zeros(len(self.labels)) 
				for i in range(len(self.labels)):  
					tmp[i] = i +1
				fig=plt.figure(1, figsize=(9,6))
				ax=fig.add_subplot(111)
				# ax.boxplot(to_plot) 
				bbox_props = dict(color="b")
				line_props = dict(linestyle="--")
				if self.bphor == False:
					ax.boxplot(ranks, whiskerprops=line_props, boxprops=bbox_props)
					plt.xlabel("algorithms")
					plt.ylabel("ranks") 
					plt.xticks(tmp, self.labels)
				else :
					# ax.boxplot(ranks, vert=False)
					ax.boxplot(ranks, vert=False, whiskerprops=line_props, boxprops=bbox_props)
					plt.ylabel("algorithms")
					plt.xlabel("ranks") 
					plt.yticks(tmp, self.labels)	 
	 
				plt.show() 			
 
			 
				# self.sortMatrix(ranks2, labelsTopAlg)
				# BoxPlotGraph demf = new BoxPlotGraph("", ranks2.getMatrix(), labelsTopAlg)
				# demf.pack() 
				# demf.setVisible(true)
                
		elif (self.nTopAlgorithms < 3):
			print("The minimum values must be 3 top algorithms")
		else :    
			# ____________________________________________________

			exxR = []
			dddR = []
			labelsTopAlg = []

			for j in range(len(self.labels)): #for (j = 0 j < labels.size() j++):
				labelsTopAlg.append(self.labels[j])
				

			for j in range(len(ranks[0])): #for (j = 0 j < ranks.getCol() j++):
				dddR.append( j )
				dff = 0.0
				for g in range(len(ranks)): #for (g = 0 g < ranks.getRow() g++): 
					dff = dff + ranks[g][j]
				
				exxR.append(dff)
			

			# ordenar Revisar esta información tanto en  Java como en  python
			for j in range(len(dddR)): #for (j = 0 j < dddR.size()  j++):
				minm = exxR[j]
				for g in range(len(dddR)): #for (g = 0 g < dddR.size() g++):

					if  minm <  exxR[g]  :
						trxx = labelsTopAlg[j]
						trxy = labelsTopAlg[g]
						labelsTopAlg[j] = trxy 
						labelsTopAlg[g] = trxx 
						trxx2 = dddR[j]
						trxy2 = dddR[g]
						dddR[j] = trxy2 
						dddR[g] = trxx2 
						trxx3 = exxR[j]
						trxy3 = exxR[g]
						exxR[j] = trxy3 
						exxR[g] = trxx3 
						minm = exxR[g]
					 

			# for (j = 0  j < dddR.size() j++):
			# System .out.println("alg = "+ dddR.elementAt(j)+" - "+ Maths.rounds(Double.parseDouble(exxR.elementAt(j)), decimal)  + " - "+ labelsTopAlg.elementAt(j))
			Ktop = self.nTopAlgorithms # indicate number algorithm
			# /*Ntop = lines.size() - 1*/ # indicate number experiments
			Ntop = len(self.values)
			# Create matrix values
			values2 = np.zeros(shape=(Ntop, Ktop)) #Matrix(Ntop, Ktop)
			# values2.printlnAll()

			# llenar values2
			for j in range(Ktop): #for (j = 0 j < Ktop j++):
				for g in range(Ntop): #for (g = 0 g < Ntop g++): 
					values2[g][j] =  self.values[g][dddR[j]] 
	 		


			# Calculate Rank
			ranks2 = np.zeros(shape=(Ntop, Ktop)) # = Matrix(Ntop, Ktop)
			indexRanking2 = []
			selectedRank2 = []
			
			for j in range(len(values2)): #for (j = 0 j < values2.getRow() j++):
				for g in range(len(values2[0])): #for (g = 0 g < values2.getCol() g++):
					indexRanking2.append(g)
				 
				ranking = 1

				while(len(indexRanking2) != 0):
					maxv = 1e-40

					for g in range(len(indexRanking2)): # for (g = 0 g < indexRanking2.size() g++):
						
						tmpx = values2[j][indexRanking2[g]]   
						if (tmpx > maxv):
							selectedRank2 = []
							maxv = tmpx
							selectedRank2.append(indexRanking2[g])
						elif (tmpx == maxv):
							selectedRank2.append(indexRanking2[g])
						
					
					rankTemp = (len(selectedRank2) + 2*ranking - 1)/2
					# # System .out.println(""+ranking+"---"+selectedRank.size()+"..."+rankTemp)
					ranking=ranking + len(selectedRank2)

					for g in range(len(selectedRank2)): # for (g = 0 g < selectedRank2.size() g++): 
						ranks2[j][selectedRank2[g]] =  rankTemp 
					

					for g in range(len(selectedRank2)): #for (g = 0 g < selectedRank2.size() g++):
						rs = indexRanking2.index(selectedRank2[g])
						indexRanking2.pop(rs)						
						# ranks.setMatrix(j, Integer.parseInt(selectedRank[g]), rankTemp)
			  
			
			# System .out.println()
			# # System .out.println("***********************************************")
			# # System .out.println("*** VALUES IN THE MATRIX **********************")
			# # System .out.println("***********************************************")
			# System .out.print(Terminal.title("MATRIX TOP ALGORITHMS"))
			
			self.info = self.info + "\nTop Algorithms "+str(self.nTopAlgorithms)+"\n"
			self.info = self.info + self.separator()  
			 
			# values2.printlnAll()
			
			# # System .out.println("***********************************************")
			# # System .out.println("*** RANKS IN THE MATRIX ***********************")
			# # System .out.println("***********************************************")
			# System .out.print(Terminal.title("RANKS MATRIX"))
			
			self.info = self.info + "\nRanks Matrix   \n"
			self.info = self.info + self.separator()
			 

			if (len(labelsTopAlg) > self.nTopAlgorithms):				
				while (len(labelsTopAlg) > self.nTopAlgorithms):
					labelsTopAlg.pop(len(labelsTopAlg)-1)
			 

			# genMatrix(ranks2, nameFile, "RankTop_", labelsTopAlg)  # / Esto es nuevo!!!!!!!!!!!!!!!
			# ranks2.printlnAll()
			# self.info = self.info + ranks2.toString()
			
			
			# Calculate Friedman
			vFriedman = self.friedmanT(ranks2, Ntop, Ktop)  

			# Calculate Iman   
			vIman = self.imanDavenportT(vFriedman, Ntop, Ktop)	 

			# Calculate Holm
			self.holmT(ranks2, Ntop, Ktop, labelsTopAlg) 

			
			if (self.graph):
				self.sortMatrix(ranks, self.labels) 
				tmp = np.zeros(len(self.labels)) 
				for i in range(len(self.labels)):  
					tmp[i] = i +1
				fig=plt.figure(1, figsize=(9,6))
				ax=fig.add_subplot(111)
				# ax.boxplot(to_plot)
				
				bbox_props = dict(color="b")
				line_props = dict(linestyle="--")
				if self.bphor == False:
					ax.boxplot(ranks, whiskerprops=line_props, boxprops=bbox_props)
					plt.xlabel("algorithms")
					plt.ylabel("ranks") 
					plt.xticks(tmp, self.labels)
				else :
					# ax.boxplot(ranks, vert=False)
					ax.boxplot(ranks, vert=False, whiskerprops=line_props, boxprops=bbox_props)
					plt.ylabel("algorithms")
					plt.xlabel("ranks") 
					plt.yticks(tmp, self.labels)	 
	 
				plt.show() 		 
			  
							 
			 
				# self.sortMatrix(ranks2, labelsTopAlg)
				# BoxPlotGraph demf = new BoxPlotGraph("", ranks2.getMatrix(), labelsTopAlg)
				# demf.pack() 
				# demf.setVisible(true)
				
				self.sortMatrix(ranks2, labelsTopAlg) 
				tmp = np.zeros(len(labelsTopAlg)) 
				for i in range(len(labelsTopAlg)):  
					tmp[i] = i +1
				fig=plt.figure(1, figsize=(9,6))
				ax=fig.add_subplot(111)
				# ax.boxplot(to_plot)
				bbox_props = dict(color="b")
				line_props = dict(linestyle="--")
				if self.bphor == False:
					ax.boxplot(ranks2, whiskerprops=line_props, boxprops=bbox_props)
					plt.xlabel("algorithms")
					plt.ylabel("ranks") 
					plt.xticks(tmp, labelsTopAlg)
				else :
					# ax.boxplot(ranks, vert=False)
					ax.boxplot(ranks2, vert=False, whiskerprops=line_props, boxprops=bbox_props)
					plt.ylabel("algorithms")
					plt.xlabel("ranks") 
					plt.yticks(tmp, labelsTopAlg)	 
	 
				plt.show() 		
 
			
 
				# /*
				#  * I include methods to generate boxplot in Matlab. First, sort columns 
				#  * for median and media. Second, generate the files *.m     
				#  */

				# genFilesMatlab( "Rank_", ranks, labels)
				# genFilesMatlab( "RankTop_", ranks2, labelsTopAlg)		
					

	def setLabels(self, labels) :
		self.labels = labels


	def setValues(self, values) :
		self.values = values

	def setGraph(self, graph) :
		self.graph = graph
		
	def friedmanT(self, ranks2, N, K):
		Friedman2 = 0.0 
		beta = (K+1)/2.0
		# # System .out.println("***********************************************")
		# # System .out.println("*** FRIEDMAN TEST *****************************")
		# # System .out.println("***********************************************")
		# System .out.print(Terminal.title("FRIEDMAN TEST"))
		# System .out.println("N = "+N+ " --- "+"K = "+K)
		# System .out.println("Beta = " + Maths.rounds(beta, decimal)) 
		
		self.info = self.info + "\nFriedman Test\n"
		self.info = self.info + self.separator()
		
		for g in range(len(ranks2[0])): #for (g = 0 g < ranks2.getCol() g++):
			media = 0.0
			for j in range(len(ranks2)): #for (j = 0 j < ranks2.getRow() j++):
				media=media + ranks2[j][g] 
			
			media = media / len(ranks2)
			# System .out.println("media [alg "+g+ "] - " + Maths.rounds(media, decimal))

			media = media - beta
			Friedman2=Friedman2+(media*media)
		
		# # System .out.println("Friedman = "+Friedman)
		Friedman2 = Friedman2*6*N/(K*beta)
		# System .out.println("***********************************************")
		# System .out.println("Friedman value = " + Maths.rounds(Friedman2, decimal))
		# System .out.println("prob Chi-square function = " + Maths.rounds(stats.chiSquaredProbability(Friedman2, K-1), decimal))
		# System .out.println("Calculate with degree = "+(K-1)+ " and obtain critical value with one sided ")
		  
		# System .out.println("Critical value = "+Maths.precisionAndSpaces(x2.inverseCumulativeProbability(1 - alpha), decimal, 10)+ "   alpha = "+alpha)		
		# System .out.println("***********************************************")
		# System .out.println() 
		
		self.info = self.info + "Friedman value = " + str(round(Friedman2, self.decimal))+"\n"
		self.info = self.info + "prob Chi-square function = " + str(round(chi2.cdf(Friedman2, K-1), self.decimal)) +"\n"
		self.info = self.info + "Calculate with degree = "+str(K-1)+ " and obtain critical value with one sided "+"\n"
		self.info = self.info + "Critical value = " + str(round(chi2.ppf(1-self.alpha, K-1), self.decimal)) + "   alpha = "+str(self.alpha) +"\n" 
		return Friedman2
	 
	 
	def imanDavenportT(self, Friedman, N, K):
		# # System .out.println("***********************************************")
		# # System .out.println("*** IMAN DAVENPORT TEST ***********************")
		# # System .out.println("***********************************************")
		# System .out.print(Terminal.title("IMAN-DAVENPORT TEST"))
		
		self.info = self.info + "\nIman-Davenport Test\n"
		self.info = self.info + self.separator()
	 
		ttm = (N - 1) * Friedman
		ttd = N * (K - 1) - Friedman
		Nmin = N-1
		Kmin = K-1
		# System .out.println("Iman-Davenport  = " + Maths.rounds((ttm /ttd), decimal))
		
		self.info = self.info + "Iman-Davenport  = " + str(round((ttm /ttd), self.decimal)) +"\n" 
		
		# System .out.println("prob F-Function  = " + Maths.rounds(stats.FProbability(ttm /ttd, Kmin, Kmin*Nmin), decimal))
		self.info = self.info + "prob F-Function  = " + str(round(f.cdf(ttm /ttd, Kmin, Kmin*Nmin), self.decimal)) +"\n" 
		
		 
		
		
		# System .out.println("Calculate with degree = "+(K-1)+ " X "+(K-1)*(N-1)+" and obtain critical value with one sided ")		
		 
	 
		# System .out.println("Critical value = " + Maths.precisionAndSpaces(x2.inverseCumulativeProbability(1 - alpha), decimal, 10)+ "   alpha = "+alpha)		
		# System .out.println("***********************************************")
		# System .out.println()
		self.info = self.info + "Calculate with degree = "+str(K-1)+ " X "+str((K-1)*(N-1))+" and obtain critical value with one \n\tsided " +"\n" 
		self.info = self.info + "Critical value = "+ str(round(f.ppf(1-self.alpha, K-1, (K-1)*(N-1)), self.decimal))+ "   alpha = "+ str(self.alpha) +"\n" 
		
		return ttm /ttd
	 
	
	def holmT(self,ranks2, N, K, labelsTopAlg):
	 
 
		beta = K*(K+1)/(6*N)
		# # System .out.println("beta "+beta)
		beta = math.sqrt(beta) 
		ss = []
		# # System .out.println()
		# # System .out.println("***********************************************")
		# # System .out.println("************ z Statistics *********************")
		# # System .out.println("***********************************************")
		# System .out.print(Terminal.title("HOLM TEST"))
		# System .out.println("N = "+N+ " --- "+"K = "+K)
		# System .out.println("beta = " + Maths.rounds(beta, decimal))
		self.info = self.info + "\nHolm Test\n"
		self.info = self.info + self.separator()
		for g in range(len(ranks2[0])): ##for (g = 0 g < ranks2.getCol() g++):
			media = 0.0
			for j in range(len(ranks2)): #for (j = 0 j < ranks2.getRow() j++):
				media=media + ranks2[j][g]  
			
			media=media/len(ranks2)
			# System .out.println("media [alg "+g+ "] - " + Maths.rounds(media, decimal))

			ss.append(media)
		
		# # System .out.println("Friedman = "+Friedman) 

		# ordenar
		for j in range(len(ss)): #for (j = 0 j < ss.size()  j++):
			minm = ss[j]
			for g in range(len(ss)): #for (g = 0 g < ss.size() g++):

				if  minm < ss[g] :
					trxx = labelsTopAlg[j]
					trxy = labelsTopAlg[g]
					labelsTopAlg[j] = trxy 
					labelsTopAlg[g] = trxx 
					trxx2 = ss[j]
					trxy2 = ss[g]
					ss[j] = trxy2 
					ss[g] = trxx2 
					minm = ss[g] 
 
		leader = ss[0] 
		# System .out.println()
		# System .out.println("***********************************************")
		# System .out.println("*** <tenor p value> if tenor > value then there is differences ***")
		# System .out.println("***********************************************")
		# System .out.println("CONTROL "+ labelsTopAlg.elementAt(0))
		self.info = self.info + "Control Algorithm "+ labelsTopAlg[0] +"\n"
		self.info = self.info + "[tenor p value] if tenor > value then there is differences (see @ \n\tsymbol)\n"
		self.info = self.info + self.separator()
		for j in range( 1,len(ss) ): #for (j = 1  j < ss.size() j++):
			ttp = ((ss[j] - leader)/beta)
			ptenor = (self.alpha/(K-(K-j)))
			# pp = (1-stats.normalProbability(ttp))  
			pp = (1-norm.cdf(ttp))  
			self.info = self.info + str(j) + " " + labelsTopAlg[j]+" ::: " + str(round(ttp, self.decimal)) + " - "  
			self.info = self.info + str(round(ptenor, self.decimal)) + " p " + str(round(pp, self.decimal)) 
			
			if (ptenor > pp):
				# System .out.println(j+ " "+ labelsTopAlg[j]+" ::: " + str(round(ttp, self.decimal)) + " - "+   str(round(ptenor, self.decimal)) + " p " + str(round(pp, self.decimal)) + " @")
				self.info = self.info +" @\n"
			else:
				# System .out.println(j+ " "+ labelsTopAlg[j]+" ::: "+ str(round(ttp, self.decimal)) + " - "+   str(round(ptenor, self.decimal)) + " p "+ str(round(pp, self.decimal)))
				self.info = self.info +"\n"
			
		
		# System .out.println("***********************************************")
		# System .out.println()
		
		
	def sortMatrix(self, ranks, labels):
		s = "n "

		media  = np.zeros(len(ranks[0]))  
		median = np.zeros(len(ranks[0]))  
		# System .out.println("******** "+ranks.getRow() +" <---> "+ranks.getCol())
		for i in range(len(ranks[0])): #for(i= 0 i < ranks.getCol() i++): 
			tmp = np.zeros(len(ranks)) 
			v = []
			son = 0
			
			for j in range(len(ranks)): #for(j= 0 j < ranks.getRow() j++): 
				tmp[j] = ranks[j][i] 
				v.append(ranks[j][i] )
				son = son + tmp[j]
			
			media[i] =	son / len(ranks) 

			# sort ascent-order  
			for j in range(len(ranks) -1): #for(j= 0 j < ranks.getRow()-1 j++):
				for f in range(j+1, len(ranks)): #for(f = j+1 f < len(ranks) f++):
					if (tmp[f] < tmp[j]):
						tms = tmp[j]
						tm2 = tmp[f]
						tmp[f] = tms
						tmp[j] = tm2  

			middle = len(tmp)//2  #  subscript of middle element
			if (len(tmp) % 2 == 1) : 
				median[i] = tmp[middle]
			else :
				median[i] = (tmp[middle -1] + tmp[middle]) / 2.0
			
			# System .out.println(labels.elementAt(i)+ "--- "+ Maths.rounds(median[i], decimal)  + " ::: "+ Maths.rounds(media[i], decimal)) 
		 
		# Sort columns 
		for k in range(len(ranks[0]) -1): #for(k = 0 k < len(ranks[0]) -1 k++):
			for l in range(k+1, len(ranks[0])): #for(l = k+1 l < len(ranks[0]) l++):
				if (median[l] < median[k]):
					one = labels[k]
					two = labels[l]
					labels[l] = one 
					labels[k] = two  

					tms = median[k]
					tm2 = median[l]
					median[k] = tm2
					median[l] = tms
					tms = media[k]
					tm2 = media[l]
					media[k] = tm2
					media[l] = tms

					for j in range(len(ranks)): #for(j= 0 j < ranks.getRow() j++): 
						sin = ranks[j][l]
						cos = ranks[j][k]
						ranks[j][l] = cos 
						ranks[j][k] = sin 						
					
				elif (median[k] == median[l] and media[l] < media[k] ):
					one = labels[k]
					two = labels[l]
					labels[l] = one 
					labels[k] = two 

					tms = median[k]
					tm2 = median[l]
					median[k] = tm2
					median[l] = tms
					tms = media[k]
					tm2 = media[l]
					media[k] = tm2
					media[l] = tms

					for j in range(len(ranks)): # for(j= 0 j < ranks.getRow() j++): 
						sin = ranks[j][l]
						cos = ranks[j][k]
						ranks[j][l] = cos 
						ranks[j][k] = sin 
				 
		
		 
	 
	def getInfo(self): 
		print(self.info)   		


	def fidh (self, typex, labels, valuesx) :  
		self.setLabels(labels)
		self.setValues(valuesx) 
		self.setGraph(labels)		
		# print( matrixAC )
		# print( np.transpose(matrixAC))
		# f.setValues(np.transpose(matrixAC))
		# f.setValues(valuesx) 
		print( typex )		
		if (typex == "MIN"):
		    self.minProblem() 
		else : 
		    self.maxProblem()
		    
		info = self.getInfo()


	def title(self, m):
		sp = "*******"
		temp = sp + "     " + m + "     "
		diff = 40 - len(temp)
		if (diff > 0):
			for rr in range(diff): #for (int rr = 0 rr < diff rr++) :	
				temp = temp+" "
	   
		temp = temp + sp
		
		return "\n***********************************************" + "\n"+ temp + "\n***********************************************\n" 
 
	
	def separator(self): 
		return "-----------------------------------------------\n"   
 

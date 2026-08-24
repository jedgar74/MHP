from problem.Problem import *
## from util.MatrixI import *
## from state.Solution import *

import numpy as np
import math

class TravelingSalesmanProblem (Problem):

	"""
	Define the classic Traveling Salesperson Problem (TSP)
	:version:
	:author: Jhon Amaya
	"""

	def __init__(self, namInst=None, verbose=False):
		"""
		@param String namInst :
		@param boolean verbose : imprime la matriz de distancias al leer la instancia
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "TSP"
		self.typeState = "PERMUTATIONAL"
		self.typeProblem = "MIN"
		self.verbose = verbose
		# print(self.typeState)
		self.selOpers()
		# print(type(self.op))
		if (not namInst == None):
			self.readInstance(namInst)


	def getCostMatrix(self):
		"""
		Matriz de distancias NxN. La consumen las metaheuristicas
		constructivas (ACO).

		@return numpy.ndarray :
		@author
		"""
		return self.matA


	def readInstance(self, namFile):
		"""
		Soporta dos formatos:
		  1. TSPLIB EUC_2D : cabecera con DIMENSION y seccion NODE_COORD_SECTION.
		  2. Matriz de distancias plana (formato historico, p.ej. ven.txt).
		El formato se detecta por la presencia de NODE_COORD_SECTION / DIMENSION.

		@param String namFile :
		@return  :
		@author
		"""

		with open('./DATA/instances/TSP/'+namFile, 'r') as fileobj:
		    content = fileobj.read()
		    lines = content.split('\n')

		# Se normalizan los saltos de linea de Windows y se descartan las vacias
		lines = [l.strip() for l in lines]
		lines = [l for l in lines if len(l) > 0]

		upper = content.upper()
		if ('NODE_COORD_SECTION' in upper) or ('DIMENSION' in upper):
			self.readInstanceTSPLIB(lines)
		else:
			self.readInstanceMatrix(lines)

		if self.verbose:
			print(self.matA)


	def readInstanceTSPLIB(self, lines):
		"""
		Parsea el formato TSPLIB con coordenadas euclidianas y precomputa la
		matriz de distancias.

		@param list lines : lineas del archivo, sin vacias
		@return  :
		@author
		"""

		dimension = None
		coords = []
		inCoords = False

		for line in lines:
			key = line.upper()

			if key.startswith('EOF'):
				break

			if key.startswith('NODE_COORD_SECTION'):
				inCoords = True
				continue

			# Cualquier otra seccion cierra la lectura de coordenadas
			if inCoords and (key.startswith('DISPLAY_DATA_SECTION')
					or key.startswith('EDGE_WEIGHT_SECTION')
					or key.startswith('TOUR_SECTION')):
				break

			if inCoords:
				r = line.split()
				if len(r) >= 3:
					coords.append((float(r[1]), float(r[2])))
				continue

			# Cabecera. El separador ':' puede llevar o no espacios alrededor
			if key.startswith('DIMENSION'):
				dimension = int(line.split(':')[1].strip())
			elif key.startswith('EDGE_WEIGHT_TYPE'):
				ewt = line.split(':')[1].strip().upper()
				if ewt != 'EUC_2D':
					raise ValueError("Solo se soporta EDGE_WEIGHT_TYPE EUC_2D, recibido: "+ewt)

		if len(coords) == 0:
			raise ValueError("La instancia TSPLIB no contiene NODE_COORD_SECTION valida")

		if (dimension != None) and (dimension != len(coords)):
			raise ValueError("DIMENSION="+str(dimension)+" no coincide con "
					+str(len(coords))+" coordenadas leidas")

		self.nVar = len(coords)
		self.matA = np.zeros(shape=(self.nVar, self.nVar))

		# Distancia euclidiana con el redondeo nint de TSPLIB: int(d + 0.5).
		# No se usa round() de Python porque aplica redondeo bancario (mitad al
		# par) y los costos no coincidirian con los optimos publicados.
		for i in range(self.nVar):
			xi, yi = coords[i]
			for j in range(i+1, self.nVar):
				xj, yj = coords[j]
				d = int(math.sqrt((xi - xj)**2 + (yi - yj)**2) + 0.5)
				self.matA[i][j] = d
				self.matA[j][i] = d


	def readInstanceMatrix(self, lines):
		"""
		Parsea una matriz de distancias plana (formato historico).

		@param list lines : lineas del archivo, sin vacias
		@return  :
		@author
		"""

		self.nVar = len(lines)
		self.matA = np.zeros(shape=(self.nVar, self.nVar))

		for j in range(len(lines)):
			r = lines[j].split()
			for d in range(len(r)):
				self.matA[j][d] = float(r[d])


	def evaluate(self, s):
		"""
		Costo del ciclo cerrado: suma de aristas consecutivas mas el retorno
		desde la ultima ciudad a la primera.

		@param state.Solution s :
		@return  :
		@author
		"""

		# Se normaliza a enteros: algunos operadores (crossoverAlternatingPosition)
		# devuelven vars como lista de Python en vez de ndarray.
		idx = np.asarray(s.vars, dtype=int)

		value = 0

		for j in range(self.nVar - 1):
			value = value + self.matA[idx[j+1]][idx[j]]

		value = value + self.matA[idx[self.nVar-1]][idx[0]]
		s.setFitness(value)

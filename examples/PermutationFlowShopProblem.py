from problem.Problem import *

import numpy as np

class PermutationFlowShopProblem (Problem):

	"""
	Define el Permutation Flow Shop Scheduling Problem (PFSP).

	n trabajos pasan por m maquinas siempre en el mismo orden M1 -> M2 -> ... -> Mm,
	y la secuencia de trabajos es la misma en todas las maquinas. El objetivo es
	minimizar el makespan (Cmax), el instante en que el ultimo trabajo termina en
	la ultima maquina.

	:version:
	:author: Maria Fernanda Cachopo Rojas
	"""

	# Desplazamiento de cada grupo (n, m) dentro de la numeracion ta001..ta120
	# del banco de Taillard. Sirve para cruzar con opt/optimums.txt.
	OFFSETS = {
		(20, 5): 0,    (20, 10): 10,   (20, 20): 20,
		(50, 5): 30,   (50, 10): 40,   (50, 20): 50,
		(100, 5): 60,  (100, 10): 70,  (100, 20): 80,
		(200, 10): 90, (200, 20): 100, (500, 20): 110,
	}

	def __init__(self, namInst=None, verbose=False):
		"""
		@param list namInst : [fichero, indice] p.ej. ["tai20_5.txt", 1].
							  Se admite tambien la cadena sola, con indice 1.
		@param boolean verbose : imprime la matriz de tiempos al leer
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort   = "PFSP"
		self.typeState   = "PERMUTATIONAL"
		self.typeProblem = "MIN"
		self.verbose     = verbose

		# Matriz de tiempos de proceso, forma (nVar, nMachines): times[trabajo][maquina]
		self.times        = None
		self.nMachines    = 0
		self.upperBound   = None
		self.lowerBound   = None
		self.nInstances   = 0
		self.instanceName = None

		self.selOpers()

		if (not namInst == None):
			self.readInstance(namInst)


	def getCostMatrix(self):
		"""
		El PFSP no es un problema basado en grafo: no hay matriz de costos NxN
		entre trabajos. Se devuelve None para que las metaheuristicas
		constructivas (ACO) lo rechacen limpiamente en vez de fallar de forma
		confusa.

		@return None :
		@author
		"""
		return None


	def readInstance(self, namFile):
		"""
		Lee una instancia del banco de Taillard.

		Cada fichero concatena 10 bloques con la forma:

			number of jobs, number of machines, initial seed, upper bound ... :
					  20           5   873654221        1278        1232
			processing times :
			<m filas de n enteros, una por maquina>

		La matriz viene en orden MAQUINA-MAYOR (fila = maquina, columna =
		trabajo) y se transpone al almacenarla, de modo que self.times quede
		indexada como times[trabajo][maquina].

		@param list namFile : [fichero, indice 1-based dentro del fichero]
		@return  :
		@author
		"""

		if isinstance(namFile, (list, tuple)):
			fileName = namFile[0]
			index    = int(namFile[1]) if len(namFile) > 1 else 1
		else:
			fileName = namFile
			index    = 1

		with open('./DATA/instances/PFSP/'+fileName, 'r') as fileobj:
			content = fileobj.read()
			lines = content.split('\n')

		# Se normalizan los saltos de linea de Windows y se descartan las vacias
		lines = [l.strip() for l in lines]
		lines = [l for l in lines if len(l) > 0]

		blocks = self.splitBlocks(lines, fileName)
		self.nInstances = len(blocks)

		if (index < 1) or (index > self.nInstances):
			raise ValueError("Indice de instancia fuera de rango en "+fileName
					+": se pidio "+str(index)+" y el fichero contiene "
					+str(self.nInstances))

		n, m, seed, ub, lb, rows = blocks[index-1]

		self.nVar       = n
		self.nMachines  = m
		self.upperBound = ub
		self.lowerBound = lb

		# rows llega en orden maquina-mayor; la transpuesta deja times[trabajo][maquina]
		self.times = np.array(rows, dtype=int).T

		offset = self.OFFSETS.get((n, m))
		if offset is not None:
			self.instanceName = "ta%03d" % (offset + index)

		if self.verbose:
			print(self.times)


	def splitBlocks(self, lines, fileName):
		"""
		Trocea el fichero en sus bloques de instancia y valida la coherencia de
		cada cabecera contra los datos que la siguen.

		@param list lines : lineas del fichero, sin vacias
		@param String fileName : solo para los mensajes de error
		@return list : lista de tuplas (n, m, seed, ub, lb, rows)
		@author
		"""

		blocks = []
		i = 0

		while i < len(lines):

			if not lines[i].lower().startswith('number of jobs'):
				raise ValueError("Cabecera no reconocida en "+fileName
						+", linea "+str(i+1)+": "+lines[i][:40])

			header = lines[i+1].split() if (i+1) < len(lines) else []
			if len(header) < 5:
				raise ValueError("Cabecera incompleta en "+fileName
						+": se esperaban 5 valores y llegaron "+str(len(header)))

			n, m, seed, ub, lb = [int(x) for x in header[:5]]

			if (i+2) >= len(lines) or not lines[i+2].lower().startswith('processing times'):
				raise ValueError("Falta la seccion processing times en "+fileName
						+" para la instancia "+str(len(blocks)+1))

			rows = lines[i+3 : i+3+m]
			if len(rows) < m:
				raise ValueError("La instancia "+str(len(blocks)+1)+" de "+fileName
						+" declara "+str(m)+" maquinas y solo trae "+str(len(rows))
						+" filas de tiempos")

			matrix = []
			for r in rows:
				values = [int(x) for x in r.split()]
				if len(values) != n:
					raise ValueError("La instancia "+str(len(blocks)+1)+" de "+fileName
							+" declara "+str(n)+" trabajos y una fila trae "
							+str(len(values))+" valores")
				matrix.append(values)

			blocks.append((n, m, seed, ub, lb, matrix))
			i = i + 3 + m

		if len(blocks) == 0:
			raise ValueError("No se encontro ninguna instancia valida en "+fileName)

		return blocks


	def evaluate(self, s):
		"""
		Makespan de la secuencia s. Recurrencia clasica del flow shop:

			C(pi(i), k) = max{ C(pi(i-1), k) , C(pi(i), k-1) } + p[pi(i)][k]

		Se recorre con un unico vector comp de tamano m, donde comp[k] guarda el
		instante en que la maquina k quedo libre. Coste O(n*m).

		@param state.Solution s :
		@return  :
		@author
		"""

		# Se normaliza a enteros: algunos operadores devuelven vars como lista
		# de Python en vez de ndarray.
		idx = np.asarray(s.vars, dtype=int)

		m = self.nMachines
		comp = np.zeros(m)

		# Se recorre len(idx) y no self.nVar a proposito: el makespan de una
		# secuencia PARCIAL esta bien definido, y las heuristicas constructivas
		# (NEH) necesitan evaluar secuencias incompletas mientras las construyen.
		# Para una permutacion completa ambos valores coinciden.
		for j in range(len(idx)):
			job = idx[j]

			# Maquina 0: no hay maquina previa, solo se espera a que quede libre
			comp[0] = comp[0] + self.times[job][0]

			for k in range(1, m):
				if comp[k] > comp[k-1]:
					comp[k] = comp[k] + self.times[job][k]
				else:
					comp[k] = comp[k-1] + self.times[job][k]

		s.setFitness(comp[m-1])

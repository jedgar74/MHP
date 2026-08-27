from problem.Problem import *

import numpy as np

class MaxCutProblem (Problem):

	"""
	Define el Maximum Cut Problem (Max-Cut).

	Dado un grafo no dirigido ponderado G = (V, E) con pesos w_{ij} >= 0 sobre las
	aristas, se busca una particion de los vertices en dos conjuntos (un "corte")
	que maximice el peso total de las aristas que cruzan de un lado al otro.

	Es uno de los 21 problemas NP-completos de Karp. Aqui se resuelve con
	representacion BINARIA x_i in {+1, -1} (el signo indica a que lado del corte
	pertenece cada vertice), que es exactamente la que ya manejan
	state.Solution.initRandomizeBin() y operators.OperatorsBin (mutation FLIPPING).

	Valor del corte de la asignacion x:

		cut(x) = sum_{i<j} w_{ij} * (1 - x_i*x_j) / 2
		       = 0.5 * ( W_total - 0.5 * x^T W x )

	donde W_total es el peso total de las aristas (sum de la mitad de la matriz
	de adyacencia). El termino x^T W x siempre es par, asi que cut(x) es entero.

	Objetivo: MAXIMIZAR cut(x).  typeProblem = "MAX".

	:version:
	:author:
	"""

	def __init__(self, namInst=None, verbose=False):
		"""
		@param String namInst : nombre del fichero de instancia (sin ruta),
			p.ej. "toy4.txt" o "mc20_1.txt". Un fichero por instancia.
		@param boolean verbose : imprime la matriz de adyacencia al leer
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort   = "MAXCUT"
		self.typeState   = "BINARY"
		self.typeProblem = "MAX"
		self.verbose     = verbose

		# Matriz de adyacencia ponderada, forma (nVar, nVar), simetrica, diag 0
		self.adj         = None
		# Peso total de las aristas (suma de los w_{ij} con i < j)
		self.totalWeight = 0.0
		self.instanceName = None

		self.selOpers()

		if (not namInst == None):
			self.readInstance(namInst)


	def getCostMatrix(self):
		"""
		Max-Cut es un problema basado en grafo: la matriz de adyacencia ponderada
		es el analogo natural de la matriz de costos. Se devuelve para mantener
		la coherencia con los problemas de grafo (TSP), aunque las metaheuristicas
		constructivas de este trabajo (GRASP) no la consumen.

		@return numpy.ndarray :
		@author
		"""
		return self.adj


	def readInstance(self, namFile):
		"""
		Lee una instancia con el formato:

			<n>
			<n filas de n enteros>   (matriz de adyacencia simetrica, diagonal 0)

		Se valida que la matriz sea cuadrada y simetrica; si no, se lanza
		ValueError. El nombre de la instancia se deriva del nombre del fichero.

		@param String namFile :
		@return  :
		@author
		"""

		with open('./DATA/instances/MAXCUT/'+namFile, 'r') as fileobj:
			content = fileobj.read()
			lines = content.split('\n')

		# Se normalizan los saltos de linea de Windows y se descartan las vacias
		lines = [l.strip() for l in lines]
		lines = [l for l in lines if len(l) > 0]

		if len(lines) < 2:
			raise ValueError("Instancia vacia o incompleta: "+namFile)

		n = int(lines[0].split()[0])

		rows = []
		for line in lines[1:1+n]:
			values = [int(x) for x in line.split()]
			if len(values) != n:
				raise ValueError("La instancia "+namFile+" declara "+str(n)
						+" vertices y una fila trae "+str(len(values))+" valores")
			rows.append(values)

		if len(rows) != n:
			raise ValueError("La instancia "+namFile+" declara "+str(n)
					+" vertices y solo trae "+str(len(rows))+" filas")

		self.adj = np.array(rows, dtype=int)

		if not np.array_equal(self.adj, self.adj.T):
			raise ValueError("La matriz de adyacencia de "+namFile+" no es simetrica")

		self.nVar = n
		self.totalWeight = float(self.adj.sum()) / 2.0

		# Nombre sin extension: "mc20_1.txt" -> "mc20_1"
		self.instanceName = namFile.split('.')[0]

		if self.verbose:
			print(self.adj)


	def evaluate(self, s):
		"""
		Valor del corte. Se recorre con operaciones vectorizadas de numpy:

			cut(x) = 0.5 * ( W_total - 0.5 * x^T W x )

		Los signos x_i in {+1, -1} indican el lado del corte. Se normaliza a
		float porque Solution.initRandomizeBin() genera un arreglo de floats.

		@param state.Solution s :
		@return  :
		@author
		"""

		idx = np.asarray(s.vars, dtype=float)

		quad = float(idx @ self.adj @ idx)
		cut = 0.5 * (self.totalWeight - 0.5 * quad)

		s.setFitness(round(cut, 6))

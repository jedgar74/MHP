from problem.Problem import *

import numpy as np


class QuadraticAssignmentProblem (Problem):

	"""
	Define el Quadratic Assignment Problem (QAP), de Koopmans y Beckmann (1957).

	Hay n instalaciones y n localizaciones. Entre cada par de instalaciones
	circula un flujo A[i][j], y entre cada par de localizaciones hay una
	distancia B[k][l]. Una solucion es una permutacion p, donde p[i] es la
	localizacion que recibe la instalacion i, y su costo es

		f(p) = SUM_i SUM_j  A[i][j] * B[p[i]][p[j]]

	Se llama cuadratico porque el costo de colocar una instalacion depende de
	donde se hayan colocado TODAS las demas. Esa es la diferencia estructural
	con el PFSP y el TSP: alli el costo se descompone a lo largo de la
	secuencia y una solucion parcial tiene un valor bien definido, aqui no.
	Por eso este problema no admite arranque constructivo tipo NEH y por eso
	getCostMatrix() devuelve None (ver el comentario del metodo).

	Se lee el formato de QAPLIB (Burkard, Karisch y Rendl, 1997), que es el
	banco de instancias que ya estaba en DATA/instances/QAP/.

	:version:
	:author: Jordano Pernia
	"""

	""" ATTRIBUTES
	matA  (public)   matriz de flujos entre instalaciones
	matB  (public)   matriz de distancias entre localizaciones
	"""


	def __init__(self, namInst=None, verbose=False):
		"""
		@param String namInst : fichero de la instancia, p.ej. "had12.dat"
		@param boolean verbose : imprime las dos matrices al leer la instancia
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort = "QAP"
		self.typeState = "PERMUTATIONAL"
		self.typeProblem = "MIN"
		self.verbose = verbose

		# Matriz de distancias entre localizaciones. La de flujos va en matA,
		# que es el atributo que el framework ya reserva para los problemas
		# basados en grafo.
		self.matB = None

		self.selOpers()

		if (not namInst == None):
			self.readInstance(namInst)


	def getCostMatrix(self):
		"""
		Devuelve None de forma deliberada.

		Las metaheuristicas constructivas la usan como visibilidad heuristica:
		"que tan atractivo es el arco i->j". En el QAP no existe tal cosa, el
		costo de una asignacion no se conoce hasta que estan hechas todas las
		demas, y ninguna de las dos matrices por separado la aproxima. Devolver
		matA seria dar a ACO una heuristica que no significa nada.

		La consecuencia practica es que ACO no es una linea base valida para
		este problema en la plataforma. Las que si lo son son GA, SA y TS, que
		son justamente las que el propio banco de salidas del repositorio
		compara sobre QAP (ver DATA/output/QAP 28_5_2019 18_17.txt).

		@return None :
		@author
		"""
		return None


	def readInstance(self, namFile):
		"""
		Lee el formato QAPLIB: un entero n, despues la matriz de flujos nxn y
		despues la matriz de distancias nxn.

		No se parsea linea a linea a proposito. En QAPLIB una fila de la matriz
		se reparte en varias lineas cuando n es grande, y el numero de lineas en
		blanco entre bloques no es constante entre ficheros. Se leen todos los
		numeros del fichero de corrido y se reparten por posicion, que es la
		unica lectura que funciona para las 40 instancias del directorio.

		@param String namFile :
		@return  :
		@author
		"""

		with open('./DATA/instances/QAP/'+namFile, 'r') as fileobj:
			tokens = fileobj.read().split()

		values = [float(t) for t in tokens]

		if len(values) == 0:
			raise ValueError("La instancia QAP esta vacia: "+namFile)

		n = int(values[0])
		expected = 1 + 2*n*n

		if len(values) < expected:
			raise ValueError("La instancia "+namFile+" declara n="+str(n)
					+" y necesita "+str(expected)+" numeros, pero tiene "
					+str(len(values)))

		self.nVar = n
		self.matA = np.array(values[1:1+n*n]).reshape(n, n)
		self.matB = np.array(values[1+n*n:1+2*n*n]).reshape(n, n)

		if self.verbose:
			print("Flujos:")
			print(self.matA)
			print("Distancias:")
			print(self.matB)


	def evaluate(self, s):
		"""
		Costo de la asignacion s.

		Se calcula vectorizado: matB[np.ix_(idx, idx)] construye la matriz cuyo
		elemento (i,j) es B[p[i]][p[j]], se multiplica elemento a elemento por
		los flujos y se suma. Es O(n^2), igual que el doble bucle, pero sin
		pagar el intervalo de Python en cada celda.

		La literatura del QAP acelera la busqueda local con evaluacion
		incremental: al intercambiar dos instalaciones la variacion exacta del
		costo se obtiene en O(n). Aqui NO se usa, y es una decision, no un
		olvido: el presupuesto de esta plataforma se mide en llamadas a
		evaluate(), asi que si la busqueda local evaluara en O(n) mientras GA y
		SA evaluan en O(n^2) las series dejarian de ser comparables con el mismo
		numero de evaluaciones.

		@param state.Solution s :
		@return  :
		@author
		"""

		# Se normaliza a enteros: algunos operadores (crossoverAlternatingPosition)
		# devuelven vars como lista de Python en vez de ndarray.
		idx = np.asarray(s.vars, dtype=int)

		# A diferencia del PFSP, aqui no se recorre len(idx): una asignacion
		# parcial no tiene costo definido en un problema cuadratico.
		value = np.sum(self.matA * self.matB[np.ix_(idx, idx)])

		s.setFitness(float(value))

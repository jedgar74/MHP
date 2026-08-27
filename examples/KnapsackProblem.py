from problem.Problem import *

import numpy as np

class KnapsackProblem (Problem):

	"""
	Define el problema 0/1 Knapsack (KP).

	Hay n objetos, cada uno con un peso y un beneficio, y una mochila con
	capacidad C. Se decide que objetos se meten en la mochila
	maximizando el beneficio total sin superar C.

	:version:
	:author:
	"""

	def __init__(self, namInst=None):
		"""
		@param String namInst : nombre del fichero dentro de DATA/instances/KP/
		@return  :
		@author
		"""
		super().__init__()
		self.nameShort   = "KP"
		self.typeState  = "BINARY"
		self.typeProblem = "MAX"
		self.capacity  = 0
		self.weights   = None
		self.profits   = None
		self.optimum   = None
		self.penalty    = None

		self.selOpers()

		if (not namInst == None):
			self.readInstance(namInst)


	def readInstance(self, namFile):
		"""
		Lee una instancia de KP. El fichero tiene la forma:

			3 50 220
			10 20 30
			60 100 120

		linea 1  : n objetos, capacidad y (opcional) beneficio optimo conocido
		linea 2  : los n pesos
		linea 3  : los n beneficios

		@param String namFile : nombre del fichero dentro de DATA/instances/KP/
		@return  :
		@author
		"""

		with open('./DATA/instances/KP/'+namFile, 'r') as fileobj:
			lines = fileobj.read().split('\n')

		lines = [l.strip() for l in lines]
		lines = [l for l in lines if len(l) > 0]

		if len(lines) < 3:
			raise ValueError("Fichero incompleto en "+namFile
					+": se esperaban cabecera, pesos y beneficios")

		header = lines[0].split()
		if len(header) < 2:
			raise ValueError("Cabecera mal formada en "+namFile
					+": se esperaban n y capacidad")

		n = int(header[0])
		self.capacity = int(header[1])
		self.optimum = float(header[2]) if len(header) > 2 else None

		if n < 1:
			raise ValueError("El numero de objetos debe ser positivo en "+namFile)
		if self.capacity < 1:
			raise ValueError("La capacidad debe ser positiva en "+namFile)

		weights = [int(x) for x in lines[1].split()]
		profits = [int(x) for x in lines[2].split()]

		if len(weights) != n:
			raise ValueError("Inconsistencia en "+namFile+": la cabecera declara "
					+str(n)+" objetos y la linea de pesos trae "
					+str(len(weights)))
		if len(profits) != n:
			raise ValueError("Inconsistencia en "+namFile+": la cabecera declara "
					+str(n)+" objetos y la linea de beneficios trae "
					+str(len(profits)))
		if any(w < 1 for w in weights):
			raise ValueError("Todos los pesos deben ser positivos en "+namFile)
		if any(v < 1 for v in profits):
			raise ValueError("Todos los beneficios deben ser positivos en "+namFile)

		self.nVar     = n
		self.weights  = np.array(weights, dtype=int)
		self.profits  = np.array(profits, dtype=int)

		# Penalizacion derivada de la instancia: cualquier subconjunto tiene
		# beneficio <= sum(profits) y cualquier violacion de capacidad tiene exceso
		# >= 1, luego una solucion inviable queda siempre con fitness < 0.
		self.penalty  = int(np.sum(self.profits)) + 1


	def packing(self, s):
		"""
		Devuelve (peso, beneficio) de la solucion s.

		La solucion esta codificada en {-1, +1}; el mapeo a {0, 1} es
		el mismo patron de UnitCommitmentProblem: (vars + 1) / 2.

		@param state.Solution s :
		@return tuple : (peso_total, beneficio_total)
		@author
		"""

		# vars llega como ndarray de numpy; el mapeo {-1,+1} -> {0,1}
		# produce float64 exacto para enteros pequenos, y se vuelve a int.
		x = ((np.asarray(s.vars, dtype=int) + 1) // 2).astype(int)

		weight = int(np.dot(x, self.weights))
		profit = int(np.dot(x, self.profits))

		return (weight, profit)


	def evaluate(self, s):
		"""
		Beneficio total de la solucion s, en sentido MAX.

		Si el peso supera la capacidad se aplica una penalizacion derivada de la
		propia instancia: se resta el mayor beneficio posible de un subconjunto
		mas 1 (self.penalty) por cada unidad de exceso. Como el beneficio de
		cualquier subconjunto nunca supera sum(profits), exceso >= 1 implica
		fitness < 0, y la solucion vacia (factible) vale 0.

		@param state.Solution s :
		@return  :
		@author
		"""

		weight, profit = self.packing(s)

		if weight > self.capacity:
			profit = profit - self.penalty * (weight - self.capacity)

		s.setFitness(float(profit))

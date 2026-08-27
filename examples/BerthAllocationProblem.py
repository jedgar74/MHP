# coding=UTF-8
from problem.Problem import *
import numpy as np
import os

class BerthAllocationProblem(Problem):
	"""
	Define el Discrete Berth Allocation and Ship Scheduling Problem (BAP).
	
	Un conjunto de N buques de carga arriba a un puerto con M muelles de atraque.
	Cada buque i posee:
	  - Hora de llegada estimada (arrival_time)
	  - Tiempos de operacion/descarga por muelle (handling_times)
	  - Fecha de salida deseada / ventana limite (due_date)
	  - Factor de penalizacion por retraso (weight)
	
	El objetivo es secuenciar y asignar los buques a los muelles minimizando
	el tiempo de permanencia total en puerto y las penalizaciones por demora.

	:author: Maria
	"""

	def __init__(self, namInst=None, verbose=False):
		"""
		@param String namInst : nombre del archivo de instancia (ej. "bap_20_5.txt")
		@param boolean verbose : imprime detalles de carga
		"""
		super().__init__()
		self.nameShort   = "BAP"
		self.typeState   = "PERMUTATIONAL"
		self.typeProblem = "MIN"
		self.verbose     = verbose

		self.nBerths       = 0
		self.arrivalTimes  = None
		self.handlingTimes = None  # matriz (nShips x nBerths)
		self.dueDates      = None
		self.weights       = None
		self.instanceName  = None

		self.selOpers()

		if namInst is not None:
			self.readInstance(namInst)

	def getCostMatrix(self):
		"""
		El BAP es un problema de scheduling dinamico, no de grafo euclidiano.
		Devuelve None para que metodos que exigen grafo (como ACO basico) lo indiquen.
		"""
		return None

	def readInstance(self, namFile):
		"""
		Lee instancias de texto del BAP ubicadas en DATA/instances/BAP/
		Formato del fichero:
		  Linea 1: nShips nBerths
		  Siguientes nShips lineas:
		    ship_id arrival_time due_date weight h_time_b0 h_time_b1 ... h_time_bM
		"""
		if isinstance(namFile, (list, tuple)):
			fileName = namFile[0]
		else:
			fileName = namFile

		self.instanceName = fileName.replace(".txt", "")
		path = os.path.join("./DATA/instances/BAP", fileName)

		with open(path, 'r', encoding='utf-8') as fh:
			lines = [l.strip() for l in fh.readlines() if len(l.strip()) > 0 and not l.startswith('#')]

		# Cabecera
		header = lines[0].split()
		self.nVar     = int(header[0])  # nShips
		self.nBerths  = int(header[1])

		self.arrivalTimes  = np.zeros(self.nVar, dtype=float)
		self.dueDates      = np.zeros(self.nVar, dtype=float)
		self.weights       = np.zeros(self.nVar, dtype=float)
		self.handlingTimes = np.zeros((self.nVar, self.nBerths), dtype=float)

		for i in range(self.nVar):
			row = lines[i + 1].split()
			# row[0] es ship_id
			self.arrivalTimes[i]  = float(row[1])
			self.dueDates[i]      = float(row[2])
			self.weights[i]       = float(row[3])
			for b in range(self.nBerths):
				self.handlingTimes[i][b] = float(row[4 + b])

		if self.verbose:
			print(f"[BAP] Instancia {self.instanceName} cargada: {self.nVar} buques, {self.nBerths} muelles.")

	def evaluate(self, s):
		"""
		Evalua la secuencia de prioridad permutacional de los barcos s.
		Asigna cada buque al muelle que permita su finalizacion mas temprana (Earliest Completion Time).
		Calcula el costo total = tiempo de espera + tiempo de operacion + penalizacion por retraso.
		"""
		idx = np.asarray(s.vars, dtype=int)
		berth_free_time = np.zeros(self.nBerths, dtype=float)

		total_cost = 0.0

		for ship in idx:
			arr = self.arrivalTimes[ship]
			due = self.dueDates[ship]
			w   = self.weights[ship]

			# Encontrar el muelle con menor tiempo de finalizacion
			best_berth = 0
			best_completion = float('inf')

			for b in range(self.nBerths):
				start_time = max(arr, berth_free_time[b])
				completion = start_time + self.handlingTimes[ship][b]
				if completion < best_completion:
					best_completion = completion
					best_berth = b

			# Asignar buque al mejor muelle
			start_time = max(arr, berth_free_time[best_berth])
			completion = start_time + self.handlingTimes[ship][best_berth]
			berth_free_time[best_berth] = completion

			# Coste: tiempo de estancia (salida - llegada) + penalizacion por tardanza
			turnaround = completion - arr
			tardiness = max(0.0, completion - due)
			total_cost += turnaround + (w * tardiness)

		s.setFitness(round(total_cost, 2))
# coding=UTF-8
"""
Utilidades de reporte para experimentos multi-instancia.

Estas funciones estaban definidas unicamente dentro de METACOOSEV.ipynb; se
portan aqui para que los scripts de consola (ExecuteTSP.py) puedan reutilizarlas
sin depender del notebook.
"""

import numpy as np


def instanceRanges(instances):
	"""
	Devuelve los indices donde comienza cada bloque de instancia dentro de la
	lista plana de resultados. Asume que los resultados vienen agrupados por
	instancia, que es como los genera el bucle de experimentacion.

	@param list instances : instancia asociada a cada BasicStats
	@return list :
	@author
	"""

	ranges = []
	if len(instances) == 0:
		return ranges

	ranges.append(0)
	ins = instances[0]

	i = 1
	while (i < len(instances)):
		if (ins != instances[i]):
			ranges.append(i)
			ins = instances[i]
		i = i + 1

	return ranges


def printer(instances, nameParameters, optima=None, startCosts=None):
	"""
	Imprime, por instancia, la tabla Mejor / N.Mejor / Media / Desv.Estandar.
	Si se suministra 'optima' se anade la columna de gap relativo al optimo
	conocido, que es lo que hace comparable el desempeno entre instancias de
	escalas muy distintas.

	Si ademas se suministra 'startCosts' se anaden dos columnas para los
	metodos que declaran un arranque constructivo (hoy solo ACO, via el tour
	por vecino mas cercano que usa para fijar tau0):

	  Start%  gap del costo medio de partida respecto al optimo
	  Delta   puntos porcentuales que cierra la busqueda (Start% - Gap%)

	Delta separa el merito de la metaheuristica del merito de su inicializacion.
	Sin esa columna no se distingue una colonia que busca de una que se limita
	a devolver su tour inicial.

	@param list instances : instancia asociada a cada BasicStats
	@param list nameParameters : lista de objetos BasicStats
	@param dict optima : instancia -> optimo conocido (opcional)
	@param list startCosts : por serie, lista de costos de arranque (opcional)
	@return  :
	@author
	"""

	ranges = instanceRanges(instances)

	for rd in range(len(ranges)):
		ini = ranges[rd]
		if (rd < len(ranges) - 1):
			fin = ranges[rd+1]
		else:
			fin = len(nameParameters)

		best = None
		if (optima is not None) and (instances[ini] in optima):
			best = float(optima[instances[ini]])

		# Solo se muestran las columnas de arranque si alguna serie del bloque
		# las reporta y hay optimo con el que normalizar.
		showStart = False
		if (startCosts is not None) and (best is not None):
			for r in range(ini, fin):
				if (r < len(startCosts)) and startCosts[r]:
					showStart = True
					break

		print("\n:: Instance :: " + str(instances[ini]))
		if best is not None:
			print(":: Known optimum :: " + str(best))
		print(":: N. Experiment.:: " + str(len(nameParameters[ini].solutions)))
		print("---------------------------------------------------------------")
		print('{: <24s}'.format(""), end="")
		print('{: <12s}'.format("Better"), end="")
		print('{: <9s}'.format("N.Bet."), end="")
		print('{: <12s}'.format("Mean"), end="")
		print('{: <12s}'.format("S.D."), end="")
		if best is not None:
			print('{: <10s}'.format("Gap%"), end="")
		if showStart:
			print('{: <10s}'.format("Start%"), end="")
			print('{: <10s}'.format("Delta"), end="")
		print("")
		print("---------------------------------------------------------------")

		for r in range(ini, fin):
			ave = nameParameters[r].average()
			print('{: <24s}'.format(nameParameters[r].getLabel()), end="")
			print('{: <12.4f}'.format(round(nameParameters[r].getBetter(), 4)), end="")
			print('{: <9d}'.format(nameParameters[r].getNBetter()), end="")
			print('{: <12.4f}'.format(round(ave, 4)), end="")
			print('{: <12.4f}'.format(round(nameParameters[r].stDeviat(ave), 4)), end="")
			gap = None
			if best is not None:
				gap = 100.0 * (ave - best) / best
				print('{: <10.2f}'.format(gap), end="")
			if showStart:
				sc = startCosts[r] if r < len(startCosts) else None
				if sc:
					sgap = 100.0 * (float(np.mean(sc)) - best) / best
					print('{: <10.2f}'.format(sgap), end="")
					print('{: <10.2f}'.format(sgap - gap), end="")
				else:
					print('{: <10s}'.format("-"), end="")
					print('{: <10s}'.format("-"), end="")
			print("")


def getMatrix(instances, nameParameters):
	"""
	Construye la matriz que consume FriedmanImanHolm.fidh: N x K con
	N = instancias (bloques) y K = algoritmos (columnas). Cada celda es la
	media de las repeticiones de ese par (instancia, algoritmo).

	Nota: las repeticiones NO son bloques del test; se colapsan aqui en una
	media. Por eso el numero de instancias es lo que determina la potencia
	estadistica de Friedman.

	@param list instances : instancia asociada a cada BasicStats
	@param list nameParameters : lista de objetos BasicStats
	@return (list, numpy.ndarray) : etiquetas de algoritmo y matriz N x K
	@author
	"""

	labels = []
	for r in range(len(nameParameters)):
		s = nameParameters[r].getLabel()
		v = s.index("[")
		name = s[0:v]
		if (not name in labels):
			labels.append(name)

	ranges = instanceRanges(instances)
	if len(ranges) == 0:
		raise ValueError("No hay resultados que agrupar")

	val = len(labels)
	if len(nameParameters) != len(ranges) * val:
		raise ValueError("Los resultados no forman una rejilla completa: "
				+ str(len(ranges)) + " instancias x " + str(val)
				+ " algoritmos != " + str(len(nameParameters)) + " series")

	valuesx = np.zeros((len(ranges), val))

	for rd in range(len(ranges)):
		ini = ranges[rd]
		if (rd < len(ranges) - 1):
			fin = ranges[rd+1]
		else:
			fin = len(nameParameters)

		if (fin - ini) != val:
			raise ValueError("La instancia " + str(instances[ini]) + " tiene "
					+ str(fin - ini) + " series, se esperaban " + str(val))

		# La columna se ubica por nombre de algoritmo, no por posicion, para
		# que las columnas queden alineadas con 'labels' aunque el orden de
		# ejecucion varie entre instancias.
		for r in range(ini, fin):
			s = nameParameters[r].getLabel()
			name = s[0:s.index("[")]
			valuesx[rd][labels.index(name)] = round(nameParameters[r].average(), 4)

	return labels, valuesx

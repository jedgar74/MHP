"""Validacion experimental reproducible de QAP + VNS sobre qap4."""

import itertools
import numpy as np

from agent.Agent import Agent
from examples.QuadraticAssignmentProblem import QuadraticAssignmentProblem


def exact_optimum(problem):
	"""Calcula el optimo por enumeracion, solo viable para esta instancia 4x4."""
	values = []
	for permutation in itertools.permutations(range(problem.nVar)):
		values.append(problem_cost(problem, permutation))
	return min(values)


def problem_cost(problem, permutation):
	return sum(problem.flow[i][j] * problem.distance[permutation[i]][permutation[j]]
		for i in range(problem.nVar) for j in range(problem.nVar))


def main():
	problem = QuadraticAssignmentProblem('qap4.txt')
	optimum = exact_optimum(problem)
	results = []
	for seed in range(30):
		np.random.seed(seed)
		agent = Agent(problem, ['VNS', 'VNSQAP', 100, 1])
		agent.init()
		results.append(agent.stats.getBetter())
	print('QAP qap4 | optimo exacto: %.0f | mejor: %.0f | media: %.2f | exitos: %d/30'
		% (optimum, min(results), np.mean(results),
			sum(value == optimum for value in results)))


if __name__ == '__main__':
	main()
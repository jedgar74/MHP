"""Ejecuta PSO sobre una instancia de la funcion Rastrigin.

Ejemplos, desde la raiz del repositorio:

    python ExecuteRastrigin.py
    python ExecuteRastrigin.py --dimensions 10 --evals 10000 --runs 10 --seed 7
"""

import argparse
import numpy as np

from agent.Agent import Agent
from examples.Rastrigin import Rastrigin


def parseArguments():
	parser = argparse.ArgumentParser(description="PSO aplicado a Rastrigin")
	parser.add_argument("--dimensions", type=int, choices=[2, 10, 30], default=10)
	parser.add_argument("--evals", type=int, default=10000)
	parser.add_argument("--runs", type=int, default=5)
	parser.add_argument("--seed", type=int, default=None)
	return parser.parse_args()


def main():
	args = parseArguments()
	if args.evals < 1:
		raise ValueError("--evals debe ser mayor que cero")
	if args.runs < 1:
		raise ValueError("--runs debe ser mayor que cero")
	if args.seed is not None:
		np.random.seed(args.seed)

	problem = Rastrigin("Rastrigin%d.json" % args.dimensions)
	agent = Agent(problem, ["PSO", "PSOS", args.evals, args.runs])
	agent.init()


if __name__ == "__main__":
	main()

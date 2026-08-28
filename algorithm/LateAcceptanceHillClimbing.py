# coding=UTF-8
"""
Late Acceptance Hill Climbing (LAHC).

A diferencia de Hill Climbing clasico, LAHC puede aceptar una solucion que sea
peor que la actual si es suficientemente buena respecto al estado de hace L
iteraciones. Esta memoria corta ayuda a escapar de optimos locales sin usar
temperatura (SA) ni poblacion (GA).
"""

from algorithm.Heuristic import *
from state.Solution import *
import copy


class LateAcceptanceHillClimbing(Heuristic):

    def __init__(self, problem, fileConfig, run=True):
        super().__init__()
        self.shortTerm = "LAHC"
        self.objProblem = problem
        self.setParameters(fileConfig)

        self.status.stateInitial = Solution(
            self.objProblem, self.parameters.get('initialTypeSolution'))
        self.objProblem.evaluate(self.status.stateInitial)
        self.objProblem.counter.incCount()

        self.status.stateFinal = copy.deepcopy(self.status.stateInitial)
        self.current = copy.deepcopy(self.status.stateInitial)

        if run:
            self.lateAcceptanceHillClimbing()

    def setParameters(self, fileConfig):
        self.parameters = self.readParameters(fileConfig, self.shortTerm)

        if 'historyLength' not in self.parameters:
            self.parameters.update(dict(historyLength=50))
        if 'initialTypeSolution' not in self.parameters:
            self.parameters.update(dict(initialTypeSolution="RANDOM"))
        if 'mutationoper' not in self.parameters:
            self.parameters.update(dict(mutationoper="FLIPPING"))

        history = int(self.parameters.get('historyLength'))
        if history <= 0:
            raise ValueError("historyLength debe ser mayor que cero")
        self.parameters['historyLength'] = history

    def _better_value(self, a, b):
        if self.objProblem.typeProblem == "MIN":
            return a < b
        return a > b

    def _not_worse_value(self, a, b):
        if self.objProblem.typeProblem == "MIN":
            return a <= b
        return a >= b

    def lateAcceptanceHillClimbing(self, solution=None):
        if solution is None:
            current = copy.deepcopy(self.current)
        else:
            current = copy.deepcopy(solution)
            if current.fitness is None:
                self.objProblem.evaluate(current)
                self.objProblem.counter.incCount()

        best = copy.deepcopy(current)
        length = self.parameters.get('historyLength')
        history = [float(current.fitness)] * length
        iteration = 0

        while self.isStopCriteria():
            candidate = self.objProblem.op.mutation(
                self.parameters.get('mutationoper'), [current])
            self.objProblem.evaluate(candidate)
            self.objProblem.counter.incCount()

            slot = iteration % length
            late_fitness = history[slot]

            accept = (self._better_value(candidate.fitness, current.fitness)
                      or self._not_worse_value(candidate.fitness, late_fitness))

            if accept:
                current = candidate

            if self.objProblem.op.isBetter([current, best]):
                best = copy.deepcopy(current)

            # La historia conserva el fitness del estado aceptado en esta
            # iteracion. Es la referencia contra la que se comparara L pasos
            # mas tarde.
            history[slot] = float(current.fitness)
            iteration += 1

        self.current = copy.deepcopy(current)
        if self.objProblem.op.isBetter([best, self.status.stateFinal]):
            self.status.stateFinal = copy.deepcopy(best)
        return self.status.stateFinal

    def run(self, solution=None):
        return self.lateAcceptanceHillClimbing(solution)

    def replaceSolution(self, solution):
        self.current = copy.deepcopy(solution)
        self.status.stateFinal = copy.deepcopy(solution)

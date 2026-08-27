#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 12:20:33 2020

@author: tauger
"""

from algorithm.Heuristic import *
from problem.Problem import *
from state.Population import *

import numpy as np
import math
import copy


class FireworksAlgorithm(Heuristic):
    """
    Algoritmo de Fuegos Artificiales (Fireworks Algorithm - FWA).
    Metaheuristica de optimizacion basada en enjambres inspirada en la
    explosion de fuegos artificiales (Tan & Zhu 2010; Tan 2015).
    """

    def __init__(self, problem, fileConfig, run=True):
        """
        @param problem.Problem problem :
        @param String fileConfig :
        @param boolean run :
        @return :
        """
        super().__init__()

        self.shortTerm = "FWA"
        self.objProblem = problem

        self.setParameters(fileConfig)
        self.popul = Population(self.parameters.get('fireworks'), self.objProblem, self.parameters.get('initialTypeSolution'))
        self.popul.sort()
        self.objProblem.counter.incCount(self.parameters.get('fireworks'))

        self.status.stateInitial = self.popul.getBetterSort()
        self.status.stateFinal = copy.deepcopy(self.status.stateInitial)

        if run == True:
            if self.objProblem.typeState == "PERMUTATIONAL":
                self.fireworksAlgorithmPerm(self.status.stateFinal)
            else:
                self.fireworksAlgorithm(self.status.stateFinal)

    def run(self, sol=None):
        """
        @param state.Solution sol :
        @return :
        """
        if self.objProblem.typeState == "PERMUTATIONAL":
            self.fireworksAlgorithmPerm(sol if sol is not None else self.status.stateFinal)
        else:
            self.fireworksAlgorithm(sol if sol is not None else self.status.stateFinal)

    def replaceSolution(self, solution):
        """
        @param state.Solution solution :
        @return :
        """
        self.status.stateFinal = copy.deepcopy(solution)

    def setParameters(self, fileConfig):
        """
        @param String fileConfig :
        @return :
        """
        self.parameters = self.readParameters(fileConfig, self.shortTerm)

        if not 'initialTypeSolution' in self.parameters:
            self.parameters.update(dict(initialTypeSolution="RANDOM"))

        if not 'fireworks' in self.parameters:
            self.parameters.update(dict(fireworks=10))

        if not 'version' in self.parameters:
            self.parameters.update(dict(version="BASIC"))

        if not 'm' in self.parameters:
            self.parameters.update(dict(m=4))

        if not 'a' in self.parameters:
            self.parameters.update(dict(a=0.3))

        if not 'b' in self.parameters:
            self.parameters.update(dict(b=0.7))

        if not 'aprime' in self.parameters:
            self.parameters.update(dict(aprime=3))

    def fireworksAlgorithm(self, solution=None):
        """
        Bucle principal para problemas en dominios continuos/reales/mixtos.
        @param state.Solution solution :
        @return :
        """
        if solution is not None:
            self.popul.addSort(solution)

        popTx = Population(0, self.objProblem)

        while self.isStopCriteria():
            s = self.nSparks()
            a = self.amplitudes()
            sparks = self.displacement(s, a)
            self.gaussianMutation(sparks)
            if sparks.popSize > 0:
                popTx.addSort(copy.deepcopy(sparks.getIndividual(0)), True)
            elif self.popul.popSize > 0:
                popTx.addSort(copy.deepcopy(self.popul.getIndividual(0)), True)

            popTx = self.selectionStrategy(sparks, popTx)
            self.popul = copy.deepcopy(popTx)
            popTx.removeAll()

        if self.popul.popSize > 0:
            self.status.stateFinal = copy.deepcopy(self.popul.getIndividual(0))

    def nSparks(self):
        """
        Calcula el numero de chispas por cada fuego artificial.
        @return np.ndarray :
        """
        s = np.zeros(self.popul.popSize)
        e = 0.001

        worst = self.popul.getIndividual(self.popul.popSize - 1).fitness
        sumx = 0
        for j in range(self.popul.popSize):
            sumx += math.fabs(worst - self.popul.getIndividual(j).fitness)
        sumx += e

        m = self.parameters.get('m')
        a_param = self.parameters.get('a')
        b_param = self.parameters.get('b')

        for j in range(self.popul.popSize):
            tmp = m * (math.fabs(worst - self.popul.getIndividual(j).fitness) + e) / sumx
            if tmp < m * a_param:
                val = round(m * a_param)
            elif tmp > m * b_param and a_param < b_param and b_param < 1:
                val = round(m * b_param)
            else:
                val = tmp
            s[j] = int(val)
        return s

    def amplitudes(self):
        """
        Calcula la amplitud de explosion de cada fuego artificial.
        @return np.ndarray :
        """
        a = np.zeros(self.popul.popSize)
        e = 0.001

        better = self.popul.getIndividual(0).fitness
        sumx = 0
        for j in range(self.popul.popSize):
            sumx += math.fabs(better - self.popul.getIndividual(j).fitness)
        sumx += e

        aprime = self.parameters.get('aprime')
        for j in range(self.popul.popSize):
            a[j] = aprime * (math.fabs(better - self.popul.getIndividual(j).fitness) + e) / sumx

        return a

    def displacement(self, s, a):
        """
        Genera chispas normales por desplazamiento aleatorio en amplitud.
        @param np.ndarray s :
        @param np.ndarray a :
        @return state.Population :
        """
        popTemp = Population(0, self.objProblem)

        for i in range(self.popul.popSize):
            for j in range(int(s[i])):
                if not self.isStopCriteria():
                    break
                nextState = copy.deepcopy(self.popul.getIndividual(i))
                dimension = np.random.randint(1, self.objProblem.nVar + 1) if self.objProblem.nVar > 1 else 1
                for k in range(min(dimension, self.objProblem.nVar)):
                    rr = nextState.getValue(k) + (np.random.rand() * 2 * a[i] - a[i])

                    if self.objProblem.typeState == "MIX" and nextState.typeVarMix[k] == "integer":
                        rr = int(rr)

                    if rr > nextState.upperlimits[k]:
                        rr = nextState.upperlimits[k]
                    elif rr < nextState.lowerlimits[k]:
                        rr = nextState.lowerlimits[k]

                    nextState.setValue(k, rr)
                self.objProblem.evaluate(nextState)
                self.objProblem.counter.incCount()
                popTemp.addSort(nextState, True)
            if not self.isStopCriteria():
                break
        return popTemp

    def gaussianMutation(self, popTemp):
        """
        Genera chispas por mutacion gaussiana para diversificar la busqueda.
        @param state.Population popTemp :
        @return :
        """
        self.gaussian = int(self.popul.popSize * 0.5)
        for i in range(self.gaussian):
            if not self.isStopCriteria():
                break
            d = np.random.randint(self.popul.popSize)
            nextState = copy.deepcopy(self.popul.getIndividual(d))
            dimension = np.random.randint(1, self.objProblem.nVar + 1) if self.objProblem.nVar > 1 else 1
            for k in range(min(dimension, self.objProblem.nVar)):
                rr = nextState.getValue(k) * np.random.rand()
                if rr > nextState.upperlimits[k]:
                    rr = nextState.upperlimits[k]
                elif rr < nextState.lowerlimits[k]:
                    rr = nextState.lowerlimits[k]
                if self.objProblem.typeState == "MIX" and nextState.typeVarMix[k] == "integer":
                    rr = int(rr)
                nextState.setValue(k, rr)
            self.objProblem.evaluate(nextState)
            self.objProblem.counter.incCount()
            popTemp.addSort(nextState, True)

    def selectionStrategy2(self, popTemp, popTx):
        for i in range(self.popul.popSize - 1):
            if i < popTemp.popSize:
                popTx.addSort(copy.deepcopy(popTemp.getIndividual(i)), True)

        for i in range(self.popul.popSize):
            popTx.addSort(copy.deepcopy(self.popul.getIndividual(i)))

        return popTx

    def selectionStrategy(self, sparks, popTx):
        """
        Estrategia de seleccion basada en distancias/probabilidad proporcional.
        @param state.Population sparks :
        @param state.Population popTx :
        @return state.Population :
        """
        e = 0.001

        if sparks.popSize == 0:
            for i in range(self.popul.popSize):
                popTx.addSort(copy.deepcopy(self.popul.getIndividual(i)), True)
            return popTx

        for i in range(self.popul.popSize):
            sparks.addSort(copy.deepcopy(self.popul.getIndividual(i)), True)
        if sparks.popSize > 0:
            sparks.removeIndividual(0)

        if sparks.popSize == 0:
            for i in range(self.popul.popSize):
                popTx.addSort(copy.deepcopy(self.popul.getIndividual(i)), True)
            return popTx

        prob = np.zeros(sparks.popSize)
        total = 0

        worst = sparks.getIndividual(sparks.popSize - 1).fitness
        sumx = 0
        for j in range(sparks.popSize):
            sumx += math.fabs(worst - sparks.getIndividual(j).fitness)
        sumx += e

        for j in range(sparks.popSize):
            prob[j] = (math.fabs(worst - sparks.getIndividual(j).fitness) + e) / sumx
            total += prob[j]

        while popTx.popSize < self.popul.popSize:
            sumx = 0
            rnd = np.random.rand() * total
            added = False
            for s in range(sparks.popSize):
                sumx += prob[s]
                if sumx >= rnd:
                    popTx.addSort(copy.deepcopy(sparks.getIndividual(s)), True)
                    added = True
                    break
            if not added and sparks.popSize > 0:
                popTx.addSort(copy.deepcopy(sparks.getIndividual(sparks.popSize - 1)), True)

        return popTx

    def fireworksAlgorithmPerm(self, solution=None):
        """
        Bucle principal para problemas combinatorios/permutacionales.
        @param state.Solution solution :
        @return :
        """
        if solution is not None:
            self.popul.addSort(solution)

        popTx = Population(0, self.objProblem)

        while self.isStopCriteria():
            s = self.nSparksPerm()
            a = self.amplitudesPerm()
            sparks = self.displacementPerm(s, a)
            self.gaussianMutationPerm(sparks)
            if sparks.popSize > 0:
                popTx.addSort(copy.deepcopy(sparks.getIndividual(0)), True)
            elif self.popul.popSize > 0:
                popTx.addSort(copy.deepcopy(self.popul.getIndividual(0)), True)

            popTx = self.selectionStrategyPerm(sparks, popTx)
            self.popul = copy.deepcopy(popTx)
            popTx.removeAll()

        if self.popul.popSize > 0:
            self.status.stateFinal = copy.deepcopy(self.popul.getIndividual(0))

    def nSparksPerm(self):
        """
        Calcula el numero de chispas por fuego artificial en dominio permutacional.
        @return np.ndarray :
        """
        s = np.zeros(self.popul.popSize)
        e = 0.001

        worst = self.popul.getIndividual(self.popul.popSize - 1).fitness
        sumx = 0
        for j in range(self.popul.popSize):
            sumx += math.fabs(worst - self.popul.getIndividual(j).fitness)
        sumx += e

        m = self.parameters.get('m')
        a_param = self.parameters.get('a')
        b_param = self.parameters.get('b')

        for j in range(self.popul.popSize):
            tmp = m * (math.fabs(worst - self.popul.getIndividual(j).fitness) + e) / sumx
            if tmp < m * a_param:
                val = round(m * a_param)
            elif tmp > m * b_param and a_param < b_param and b_param < 1:
                val = round(m * b_param)
            else:
                val = tmp
            s[j] = int(val)
        return s

    def amplitudesPerm(self):
        """
        Calcula la amplitud (numero de swaps) en dominio permutacional.
        @return np.ndarray :
        """
        a = np.zeros(self.popul.popSize)
        e = 0.001

        better = self.popul.getIndividual(0).fitness
        sumx = 0
        for j in range(self.popul.popSize):
            sumx += math.fabs(better - self.popul.getIndividual(j).fitness)
        sumx += e

        aprime = self.parameters.get('aprime')
        for j in range(self.popul.popSize):
            a[j] = aprime * (math.fabs(better - self.popul.getIndividual(j).fitness) + e) / sumx

        return a

    def displacementPerm(self, s, a):
        """
        Genera chispas permutacionales aplicando mutaciones SWAPPING segun la amplitud.
        @param np.ndarray s :
        @param np.ndarray a :
        @return state.Population :
        """
        sparks = Population(0, self.objProblem)

        for i in range(self.popul.popSize):
            for j in range(int(s[i])):
                if not self.isStopCriteria():
                    break
                nextState = copy.deepcopy(self.popul.getIndividual(i))
                num_swaps = max(1, int(round(a[i])))
                for _ in range(num_swaps):
                    nextState = self.objProblem.op.mutation('SWAPPING', [nextState])

                self.objProblem.evaluate(nextState)
                self.objProblem.counter.incCount()
                sparks.addSort(nextState, True)
            if not self.isStopCriteria():
                break
        return sparks

    def gaussianMutationPerm(self, sparks):
        """
        Aplica mutaciones adicionales de diversificacion en permutaciones.
        @param state.Population sparks :
        @return :
        """
        self.gaussian = int(self.popul.popSize * 0.5)
        for i in range(self.gaussian):
            if not self.isStopCriteria():
                break
            d = np.random.randint(self.popul.popSize)
            nextState = copy.deepcopy(self.popul.getIndividual(d))
            nextState = self.objProblem.op.mutation('SWAPPING', [nextState])
            self.objProblem.evaluate(nextState)
            self.objProblem.counter.incCount()
            sparks.addSort(nextState, True)

    def selectionStrategyPerm(self, sparks, popTx):
        """
        Seleccion de poblacion para la siguiente iteracion en dominios permutacionales.
        @param state.Population sparks :
        @param state.Population popTx :
        @return state.Population :
        """
        e = 0.001

        if sparks.popSize == 0:
            for i in range(self.popul.popSize):
                popTx.addSort(copy.deepcopy(self.popul.getIndividual(i)), True)
            return popTx

        for i in range(self.popul.popSize):
            sparks.addSort(copy.deepcopy(self.popul.getIndividual(i)), True)
        if sparks.popSize > 0:
            sparks.removeIndividual(0)

        if sparks.popSize == 0:
            for i in range(self.popul.popSize):
                popTx.addSort(copy.deepcopy(self.popul.getIndividual(i)), True)
            return popTx

        prob = np.zeros(sparks.popSize)
        total = 0

        worst = sparks.getIndividual(sparks.popSize - 1).fitness
        sumx = 0
        for j in range(sparks.popSize):
            sumx += math.fabs(worst - sparks.getIndividual(j).fitness)
        sumx += e

        for j in range(sparks.popSize):
            prob[j] = (math.fabs(worst - sparks.getIndividual(j).fitness) + e) / sumx
            total += prob[j]

        while popTx.popSize < self.popul.popSize:
            sumx = 0
            rnd = np.random.rand() * total
            added = False
            for s in range(sparks.popSize):
                sumx += prob[s]
                if sumx >= rnd:
                    popTx.addSort(copy.deepcopy(sparks.getIndividual(s)), True)
                    added = True
                    break
            if not added and sparks.popSize > 0:
                popTx.addSort(copy.deepcopy(sparks.getIndividual(sparks.popSize - 1)), True)

        return popTx
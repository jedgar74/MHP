from algorithm.Heuristic import *
from problem.Problem import *
from state.Solution import *
import math
import copy
import numpy as np
from typing import Optional, List, Tuple
from collections import deque
import logging

class ImprovedSimulatedAnnealing(Heuristic):
    """
    Algoritmo de Recocido creado por Samuel, si sirve, gracias a dios, si no sirve, gracias a mi
    Simulado con:
    1. Enfriamiento adaptativo (Cauchy + Boltzman)
    2. Múltiples operadores de vecindad (intercambio, inserción, inversión)
    3. Reinicio inteligente con memoria de soluciones
    4. Búsqueda local 
    5. Aceptación de soluciones peores
    6. Registro de convergencia 
    """
    
    def __init__(self, problem: Problem, fileConfig: str, run: bool = True):
        super().__init__()
        self.shortTerm = "ISA"
        self.objProblem = problem
        
        # Variables de seguimiento
        self.convergence_history: List[float] = []
        self.temperature_history: List[float] = []
        self.acceptance_ratio: float = 0.0
        self.total_accepted: int = 0
        self.total_proposed: int = 0
        
        # Memoria de soluciones (tabu short-term)
        self.tabu_list: deque = deque(maxlen=7)
        self.best_solutions: List[Tuple[float, np.ndarray]] = []
        
        self.setParameters(fileConfig)
        
        # Inicializar solución
        self.status.stateInitial = Solution(self.objProblem, self.parameters.get('initialTypeSolution'))
        self.objProblem.evaluate(self.status.stateInitial)
        self.objProblem.counter.incCount()
        self.status.stateFinal = copy.deepcopy(self.status.stateInitial)
        
        if run:
            self.improvedSimulatedAnnealing()
    
    def setParameters(self, fileConfig: str):
        """Configuración con parámetros avanzados"""
        self.parameters = self.readParameters(fileConfig, self.shortTerm)
        
        defaults = {
            'initTemperature': 100.0,
            'finalTemperature': 0.001,
            'coolingFactor': 0.92,
            'coolingStrategy': 'adaptive',  # 'geometric', 'adaptive', 'cauchy'
            'maxRestarts': 5,
            'localSearchIterations': 50,
            'tabuSize': 7,
            'initialTypeSolution': "RANDOM",
            'mutationoper': "SWAPPING",
            'neighborhood_size': 3,  # Número de vecinos a evaluar por iteración
            'stagnation_limit': 200,
            'diversity_threshold': 0.1
        }
        
        for key, value in defaults.items():
            if key not in self.parameters:
                self.parameters.update({key: value})
    
    def improvedSimulatedAnnealing(self, solution: Optional[Solution] = None):
        """
        Implementación principal del algoritmo con todas las mejoras.
        """
        # Inicializar solución
        if solution is None:
            current = copy.deepcopy(self.status.stateFinal)
        else:
            current = copy.deepcopy(solution)
        
        best = copy.deepcopy(current)
        initial_best = best.fitness
        
        # Parámetros de control
        temperature = self.parameters.get('initTemperature')
        final_temp = self.parameters.get('finalTemperature')
        cooling_factor = self.parameters.get('coolingFactor')
        cooling_strategy = self.parameters.get('coolingStrategy')
        max_restarts = self.parameters.get('maxRestarts')
        local_search_iter = self.parameters.get('localSearchIterations')
        neighborhood_size = self.parameters.get('neighborhood_size')
        stagnation_limit = self.parameters.get('stagnation_limit')
        diversity_threshold = self.parameters.get('diversity_threshold')
        
        # Variables de estado
        restarts = 0
        stagnation_counter = 0
        iteration = 0
        no_improve_iter = 0
        best_overall = best.fitness
        best_in_phase = best.fitness
        
        # Registrar inicio
        self.convergence_history = [best.fitness]
        self.temperature_history = [temperature]
        self.total_accepted = 0
        self.total_proposed = 0
        
        logging.info(f"ISA iniciado. Temperatura inicial: {temperature:.2f}")
        
        while self.isStopCriteria():
            iteration += 1
            
            # === 1. GENERACIÓN DE VECINDAD DINÁMICA ===
            neighbors = self._generate_diverse_neighbors(current, neighborhood_size)
            self.total_proposed += len(neighbors)
            
            # === 2. BÚSQUEDA LOCAL EN EL VECINDARIO ===
            local_best = current
            for neighbor in neighbors:
                # Verificar tabú
                if self._is_tabu(neighbor):
                    continue
                    
                # Evaluar vecino
                self.objProblem.evaluate(neighbor)
                self.objProblem.counter.incCount()
                
                # Aceptación con criterio de Metropolis mejorado
                delta = neighbor.fitness - current.fitness
                accept = False
                
                if delta < 0:
                    accept = True
                    # Si mejora el mejor global
                    if self.objProblem.op.isBetter([neighbor, best]):
                        best = copy.deepcopy(neighbor)
                        best_overall = best.fitness
                        no_improve_iter = 0
                        stagnation_counter = 0
                        # Añadir a lista de mejores soluciones
                        self.best_solutions.append((best.fitness, best.vars.copy()))
                        if len(self.best_solutions) > 10:
                            self.best_solutions.pop(0)
                else:
                    # Probabilidad de Boltzmann con temperatura adaptativa
                    prob = math.exp(-abs(delta) / temperature)
                    # Aceptar si la probabilidad lo permite
                    if np.random.rand() < prob:
                        accept = True
                
                if accept:
                    current = copy.deepcopy(neighbor)
                    self.total_accepted += 1
                    # Actualizar mejor de la fase
                    if self.objProblem.op.isBetter([neighbor, local_best]):
                        local_best = copy.deepcopy(neighbor)
                    # Añadir a lista tabú
                    self._add_tabu(current.vars.copy())
                else:
                    stagnation_counter += 1
            
            # === 3. ACTUALIZACIÓN DE TEMPERATURA ADAPTATIVA ===
            if cooling_strategy == 'adaptive':
                # Enfriamiento adaptativo basado en la tasa de aceptación
                acceptance_rate = self.total_accepted / max(1, self.total_proposed)
                if acceptance_rate < 0.1:
                    temperature *= 0.95  # Enfriar más rápido si no hay aceptación
                elif acceptance_rate > 0.5:
                    temperature *= 0.98  # Enfriar más lento si hay mucha aceptación
                else:
                    temperature *= cooling_factor
            elif cooling_strategy == 'cauchy':
                # Enfriamiento tipo Cauchy (más lento)
                temperature = self.parameters.get('initTemperature') / (1 + iteration)
            else:
                # Enfriamiento geométrico estándar
                temperature *= cooling_factor
            
            self.temperature_history.append(temperature)
            
            # === 4. MEJORA DE LA MEJOR SOLUCIÓN CON BÚSQUEDA LOCAL ===
            if iteration % 5 == 0 and self.objProblem.op.isBetter([best, current]):
                # Búsqueda local intensiva alrededor de la mejor solución
                improved_best = self._intensify_search(best, local_search_iter)
                if improved_best.fitness < best.fitness:
                    best = copy.deepcopy(improved_best)
                    best_overall = best.fitness
                    no_improve_iter = 0
            
            # === 5. REINICIO INTELIGENTE ===
            # 5a. Reinicio por estancamiento
            if stagnation_counter > stagnation_limit and restarts < max_restarts:
                logging.info(f"Reinicio {restarts + 1}/{max_restarts} (estancamiento)")
                current = self._intelligent_restart(best, diversity_threshold)
                temperature = self.parameters.get('initTemperature') / (restarts + 1)
                restarts += 1
                stagnation_counter = 0
                no_improve_iter = 0
            
            # 5b. Reinicio por falta de diversidad
            if no_improve_iter > 0 and iteration % 100 == 0:
                diversity = self._calculate_diversity(current, best)
                if diversity < diversity_threshold and restarts < max_restarts:
                    logging.info(f"Reinicio {restarts + 1}/{max_restarts} (diversidad baja: {diversity:.3f})")
                    current = self._intelligent_restart(best, diversity_threshold)
                    temperature = self.parameters.get('initTemperature') / (restarts + 2)
                    restarts += 1
                    stagnation_counter = 0
                    no_improve_iter = 0
            
            # Registrar convergencia
            if iteration % 10 == 0:
                self.convergence_history.append(best.fitness)
            
            # === 6. CRITERIO DE PARADA ADICIONAL ===
            if temperature <= final_temp:
                break
            
            # Actualizar mejor de fase
            if self.objProblem.op.isBetter([local_best, best_in_phase]):
                best_in_phase = local_best.fitness
                no_improve_iter = 0
            else:
                no_improve_iter += 1
        
        # Guardar mejor solución encontrada
        self.status.stateFinal = best
        self.acceptance_ratio = self.total_accepted / max(1, self.total_proposed)
        
        logging.info(f"ISA finalizado. Mejor fitness: {best.fitness:.4f}")
        logging.info(f"Tasa de aceptación: {self.acceptance_ratio:.2%}")
        logging.info(f"Reinicios realizados: {restarts}")
    
    def _generate_diverse_neighbors(self, solution: Solution, n: int) -> List[Solution]:
        """
        Genera vecinos diversos usando diferentes operadores de mutación.
        """
        neighbors = []
        operators = ['SWAPPING', 'SWAPPING', 'INSERTION', 'REVERSAL']
        
        for i in range(n):
            # Seleccionar operador aleatorio
            op = operators[i % len(operators)]
            
            # Generar vecino
            neighbor = self.objProblem.op.mutation(op, [solution])
            
            # Aplicar mutación adicional si es necesario
            if np.random.rand() < 0.2:
                neighbor = self.objProblem.op.mutation(op, [neighbor])
            
            neighbors.append(neighbor)
        
        return neighbors
    
    def _is_tabu(self, solution: Solution) -> bool:
        """Verifica si una solución está en la lista tabú"""
        for tabu_sol in self.tabu_list:
            if np.array_equal(solution.vars, tabu_sol):
                return True
        return False
    
    def _add_tabu(self, solution_vars: np.ndarray):
        """Añade una solución a la lista tabú"""
        self.tabu_list.append(solution_vars.copy())
    
    def _intensify_search(self, solution: Solution, iterations: int) -> Solution:
        """Búsqueda local intensiva alrededor de una solución"""
        best = copy.deepcopy(solution)
        current = copy.deepcopy(solution)
        
        for _ in range(iterations):
            # Generar vecino
            neighbor = self.objProblem.op.mutation('SWAPPING', [current])
            self.objProblem.evaluate(neighbor)
            self.objProblem.counter.incCount()
            
            if neighbor.fitness < best.fitness:
                best = copy.deepcopy(neighbor)
                current = copy.deepcopy(neighbor)
            elif neighbor.fitness < current.fitness:
                current = copy.deepcopy(neighbor)
        
        return best
    
    def _intelligent_restart(self, best: Solution, diversity_threshold: float) -> Solution:
        """
        Reinicio inteligente: combina la mejor solución con soluciones aleatorias
        para mantener diversidad sin perder calidad.
        """
        # Crear nueva solución a partir de la mejor
        new_sol = copy.deepcopy(best)
        
        # Perturbar con alta intensidad
        perturbation_rate = 0.5 + np.random.rand() * 0.3
        n_perturbations = int(self.objProblem.nVar * perturbation_rate)
        
        for _ in range(n_perturbations):
            # Mezclar operadores para mayor diversidad
            op = np.random.choice(['SWAPPING', 'INSERTION', 'REVERSAL'])
            new_sol = self.objProblem.op.mutation(op, [new_sol])
        
        # Asegurar que la nueva solución tiene diversidad
        diversity = self._calculate_diversity(new_sol, best)
        if diversity < diversity_threshold:
            # Si sigue siendo similar, reemplazar completamente
            new_sol = Solution(self.objProblem, "RANDOM")
            self.objProblem.evaluate(new_sol)
            self.objProblem.counter.incCount()
        
        self.objProblem.evaluate(new_sol)
        self.objProblem.counter.incCount()
        
        return new_sol
    
    def _calculate_diversity(self, sol1: Solution, sol2: Solution) -> float:
        """Calcula la diversidad entre dos soluciones (0 = idénticas, 1 = totalmente diferentes)"""
        if sol1.nVar != sol2.nVar:
            return 1.0
        
        diff_count = sum(1 for i in range(sol1.nVar) if sol1.vars[i] != sol2.vars[i])
        return diff_count / sol1.nVar
    
    def get_convergence_stats(self) -> dict:
        """Retorna estadísticas de convergencia del algoritmo"""
        return {
            'convergence_history': self.convergence_history,
            'temperature_history': self.temperature_history,
            'acceptance_ratio': self.acceptance_ratio,
            'total_accepted': self.total_accepted,
            'total_proposed': self.total_proposed,
            'best_solutions': self.best_solutions,
            'initial_best': self.convergence_history[0] if self.convergence_history else None,
            'final_best': self.convergence_history[-1] if self.convergence_history else None
        }
    
    def replaceSolution(self, solution: Solution):
        """Reemplaza la solución actual con una nueva"""
        self.status.stateFinal = copy.deepcopy(solution)
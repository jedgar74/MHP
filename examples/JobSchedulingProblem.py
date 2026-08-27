from problem.Problem import *
import numpy as np
import json
from typing import List, Tuple, Optional 
import logging

class JobSchedulingProblem(Problem):
    """ Algoritmo de Recocido creado por Samuel, si sirve, gracias a dios, si no sirve, gracias a mi
    Problema de Programación de Tareas en Máquinas Paralelas (Parallel Machine Scheduling Problem)
    con tiempos de procesamiento, tiempos de setup dependientes de la secuencia y fechas de entrega.
    
    - Múltiples máquinas no idénticas 
    - Tiempos de setup dependientes de la secuencia 
    - Ventanas de tiempo 
    - Fechas de entrega con penalizaciones por tardanza
    - Función objetivo multi-objetivo ponderada
    """
    
    def __init__(self, namInst: Optional[str] = None):
        super().__init__()
        self.nameShort = "JSP"
        self.typeState = "PERMUTATIONAL"
        self.typeProblem = "MIN"
        
        # Parámetros avanzados
        self.processing_times: np.ndarray = None
        self.machine_speeds: np.ndarray = None  # Velocidad relativa de cada máquina
        self.setup_times: np.ndarray = None     # Matriz de tiempos de setup [job_i][job_j]
        self.due_dates: np.ndarray = None       # Fechas de entrega para cada tarea
        self.earliness_weights: np.ndarray = None  # Penalización por entrega anticipada
        self.tardiness_weights: np.ndarray = None  # Penalización por tardanza
        self.release_dates: np.ndarray = None   # Fecha de disponibilidad de cada tarea
        
        # Métricas para análisis
        self.makespan_history: List[float] = []
        self.tardiness_history: List[float] = []
        
        self.selOpers()
        if namInst is not None:
            self.readInstance(namInst)
    
    def readInstance(self, namFile: str):
        """Lee una instancia JSON con parámetros avanzados"""
        with open(f'./DATA/instances/JSP/{namFile}', 'r') as file:
            data = json.load(file)
        
        self.nVar = data['nJobs']
        self.nMachines = data['nMachines']
        
        # Tiempos de procesamiento
        self.processing_times = np.array(data['processing_times'], dtype=float)
        
        # Velocidades de máquinas (por defecto todas iguales)
        self.machine_speeds = np.array(data.get('machine_speeds', [1.0] * self.nMachines), dtype=float)
        
        # Tiempos de setup (si no existen, son cero)
        setup = data.get('setup_times')
        if setup:
            self.setup_times = np.array(setup, dtype=float)
        else:
            self.setup_times = np.zeros((self.nVar, self.nVar), dtype=float)
        
        # Fechas de entrega y penalizaciones
        self.due_dates = np.array(data.get('due_dates', [float('inf')] * self.nVar), dtype=float)
        self.earliness_weights = np.array(data.get('earliness_weights', [0.0] * self.nVar), dtype=float)
        self.tardiness_weights = np.array(data.get('tardiness_weights', [1.0] * self.nVar), dtype=float)
        
        # Fechas de liberación
        self.release_dates = np.array(data.get('release_dates', [0.0] * self.nVar), dtype=float)
        
        # Pesos de la función objetivo
        self.objective_weights = {
            'makespan': data.get('makespan_weight', 0.4),
            'tardiness': data.get('tardiness_weight', 0.3),
            'earliness': data.get('earliness_weight', 0.1),
            'setup': data.get('setup_weight', 0.2)
        }
        
        # Límites no necesarios para permutaciones
        self.upperlimits = [self.nVar - 1] * self.nVar
        self.lowerlimits = [0] * self.nVar
    
    def evaluate(self, s: Solution):
        """
        Evaluación multi-objetivo de una solución con:
        1. Makespan (tiempo total)
        2. Tardanza total ponderada
        3. Adelanto total ponderado
        4. Tiempo total de setup
        """
        # Decodificar la permutación usando List Scheduling con tiempos de setup
        schedule = self._decode_solution(s.vars)
        
        # Calcular métricas
        makespan = max(schedule[:, 1])  # Tiempo de finalización máximo
        
        # Calcular tardanza y adelanto
        total_tardiness = 0.0
        total_earliness = 0.0
        total_setup = 0.0
        
        # Máquina anterior para cada tarea (para calcular setup)
        prev_job = [-1] * self.nMachines
        
        for job_idx, job in enumerate(s.vars):
            machine = np.argmin(schedule[:, 0])  # Máquina menos cargada
            start_time = schedule[machine, 0]
            
            # Añadir tiempo de setup si hay tarea anterior en la misma máquina
            if prev_job[machine] != -1:
                setup = self.setup_times[prev_job[machine]][job]
                start_time += setup
                total_setup += setup
            
            # Tiempo de procesamiento considerando velocidad de la máquina
            proc_time = self.processing_times[job] / self.machine_speeds[machine]
            completion_time = start_time + proc_time
            
            # Verificar fecha de liberación
            if start_time < self.release_dates[job]:
                start_time = self.release_dates[job]
                completion_time = start_time + proc_time
            
            # Actualizar schedule
            schedule[machine, 0] = completion_time
            schedule[machine, 1] = max(schedule[machine, 1], completion_time)
            prev_job[machine] = job
            
            # Calcular tardanza/adelanto
            due_date = self.due_dates[job]
            if completion_time > due_date:
                total_tardiness += self.tardiness_weights[job] * (completion_time - due_date)
            else:
                total_earliness += self.earliness_weights[job] * (due_date - completion_time)
        
        # Función objetivo ponderada
        fitness = (
            self.objective_weights['makespan'] * makespan +
            self.objective_weights['tardiness'] * total_tardiness +
            self.objective_weights['earliness'] * total_earliness +
            self.objective_weights['setup'] * total_setup
        )
        
        # Almacenar historial para análisis
        self.makespan_history.append(makespan)
        self.tardiness_history.append(total_tardiness)
        
        s.setFitness(fitness)
        s.metadata = {
            'makespan': makespan,
            'tardiness': total_tardiness,
            'earliness': total_earliness,
            'setup': total_setup,
            'schedule': schedule.copy()
        }
    
    def _decode_solution(self, sequence: np.ndarray) -> np.ndarray:
        """
        Decodifica una permutación en un schedule de máquinas.
        Retorna una matriz [máquinas x 2] con [tiempo_actual, tiempo_final]
        """
        schedule = np.zeros((self.nMachines, 2), dtype=float)
        return schedule
    
    def getCostMatrix(self):
        """No aplica para este problema"""
        return None
    
    def print_solution(self, s: Solution):
        """Imprime una solución de forma detallada"""
        print("=" * 70)
        print("JOB SCHEDULING SOLUTION")
        print("=" * 70)
        print(f"Secuencia de tareas: {s.vars.tolist()}")
        print(f"Fitness (ponderado): {s.fitness:.4f}")
        
        if hasattr(s, 'metadata'):
            meta = s.metadata
            print(f"\nMétricas:")
            print(f"  Makespan: {meta['makespan']:.2f}")
            print(f"  Tardanza total: {meta['tardiness']:.2f}")
            print(f"  Adelanto total: {meta['earliness']:.2f}")
            print(f"  Tiempo de setup: {meta['setup']:.2f}")
            
            print(f"\nAsignación por máquina:")
            if 'schedule' in meta:
                for m in range(self.nMachines):
                    print(f"  Máquina {m+1}: finaliza en {meta['schedule'][m, 1]:.2f}")
        
        print("=" * 70)

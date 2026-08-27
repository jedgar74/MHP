from agent.Agent import * 
from examples.JobSchedulingProblem import *
from statisticc.Reporter import printer, getMatrix
from statisticc.FriedmanImanHolm import FriedmanImanHolm
import copy
import time

"""
Algoritmo de Recocido creado por Samuel, si sirve, gracias a dios, si no sirve, gracias a mi
"""

def main():
    # Problema JSP
    problem = JobSchedulingProblem("instance_5_3.json")

    # Algoritmos a comparar
    algorithms = [
        ["SA", "SAS", 3000, 10],    # Simulated Annealing estándar
        ["ISA", "ISAS", 3000, 10],   # Improved Simulated Annealing
        ["GA", "GAS", 3000, 10]    
    ]

    print("=" * 50)
    print("Comparación de Algoritmos para el Problema de Scheduling")
    print(f"Instancia: {problem.nVar} tareas, {problem.nMachines} máquinas")
    print("=" * 50)

    stats_results = []
    instance_names = []

    for i, (method, config, evals, runs) in enumerate(algorithms):
        print(f"\n--- Ejecutando {method} ---")
        agent = Agent(problem, [method, config, evals, runs])
        agent.init()
        stats_results.append(agent.stats)
        instance_names.append("JSP")
        print(f"{method} - Mejor: {agent.stats.getBetter():.2f}")
        print(f"{method} - Media: {agent.stats.average():.2f}")
        print(f"{method} - Desv. Est.: {agent.stats.stDeviat(agent.stats.average()):.2f}")

    # Análisis estadístico 
    print("\n" + "=" * 50)
    print("Análisis Estadístico (Friedman / Iman-Davenport / Holm)")
    print("=" * 50)

    labels, matrix = getMatrix(instance_names, stats_results)

    print(f"\nMatriz de resultados ({matrix.shape[0]} instancias x {matrix.shape[1]} algoritmos):")
    print("Algoritmos:", labels)
    print(matrix)

    f = FriedmanImanHolm()
    f.fidh("MIN", copy.deepcopy(labels), matrix)

    # Mostrar boxplot 
    try:
        import matplotlib.pyplot as plt
        from statisticc.Reporter import boxplot
        boxplot(labels, matrix, "JSP")
        plt.show()
    except:
        print("No se pudo generar el boxplot (matplotlib no disponible)")

if __name__ == "__main__":
    main()

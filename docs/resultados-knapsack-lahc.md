# Resultados: 0/1 Knapsack + LAHC

## Configuración experimental

La corrida utilizada para dejar resultados reproducibles en el repositorio fue:

```bash
python ExecuteKnapsack.py --instances 5 --evals 2000 --runs 3 --quiet \
  --output DATA/output/knapsack_comparison.csv
```

Se usaron cinco instancias `kp60_01` a `kp60_05`, tres corridas por serie y 2000 evaluaciones por corrida. Los gaps se calculan contra óptimos exactos obtenidos por programación dinámica.

Antes de la comparación principal se calibró la longitud de historia de LAHC con:

```bash
python ExecuteKnapsack.py --history --instances 5 --evals 2000 --runs 3 --quiet
```

El resultado medio fue:

| Configuración LAHC | Gap medio |
|---|---:|
| LAHC100 | **16.46%** |
| LAHC200 | 17.96% |
| LAHC500 | 20.16% |
| LAHC20 | 21.19% |

Por eso `LAHC100` se usa como configuración principal para el presupuesto de 2000 evaluaciones.

## Comparación principal

| Posición | Algoritmo | Gap medio | Desv. del gap | Victorias por instancia |
|---:|---|---:|---:|---:|
| 1 | GA / GAKP | **9.67%** | 1.85 | 5/5 |
| 2 | LAHC / LAHC100 | **17.30%** | 2.46 | 0/5 |
| 3 | RW / RWKP | 40.29% | 20.86 | 0/5 |
| 4 | SA / SAKP | 40.45% | 20.17 | 0/5 |

### Lectura de los resultados

**GA fue el método con mejor calidad promedio** en este banco y con este presupuesto: ganó las cinco instancias y obtuvo un gap medio de 9.67%.

**LAHC quedó segundo**. No superó al GA, pero mostró un comportamiento mucho más estable que SA y RW: su desviación del gap fue solo 2.46 puntos y las 15 soluciones finales de la comparación principal fueron factibles. Esto muestra que el nuevo algoritmo es competitivo como búsqueda de trayectoria simple, aunque en estas instancias la recombinación poblacional de GA aporta una ventaja clara.

SA y RW tuvieron corridas que terminaron inviables bajo la penalización del modelo. Esa inestabilidad aumenta su gap promedio. No se ocultó ese comportamiento porque forma parte de la comparación con las implementaciones existentes del repositorio.

## Archivos de resultados

- `DATA/output/knapsack_comparison.csv`: resultados principales por instancia y algoritmo.
- `DATA/output/knapsack_comparison.txt`: salida de consola de la comparación principal.
- `DATA/output/knapsack_history_comparison.csv`: calibración de `historyLength`.
- `DATA/output/knapsack_history_comparison.txt`: salida de consola de la calibración.

## Conclusión

Para estas cinco instancias y 2000 evaluaciones, el orden observado fue:

**GA > LAHC > RW ≈ SA**.

Esto no significa que GA sea universalmente superior. La conclusión solo corresponde al banco, parámetros y presupuesto probados. El script permite aumentar instancias, corridas y evaluaciones para un estudio más extenso.

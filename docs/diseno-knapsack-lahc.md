# Extensión MHP: 0/1 Knapsack + Late Acceptance Hill Climbing

## 1. Problema nuevo: 0/1 Knapsack

Se incorporó el **0/1 Knapsack Problem (KP)**. Dado un conjunto de objetos con un valor y un peso, y una mochila con capacidad limitada, se debe seleccionar el subconjunto que maximiza el valor total sin superar la capacidad.

La representación usa el tipo `BINARY` que ya existe en MHP:

- `+1`: objeto seleccionado.
- `-1`: objeto no seleccionado.
- Objetivo: `MAX`.

Las soluciones que exceden la capacidad reciben fitness negativo igual al exceso de peso. Así, cualquier solución viable domina a una inviable sin modificar silenciosamente las variables dentro de `evaluate()`.

La clase está en `examples/KnapsackProblem.py` y las instancias en `DATA/instances/KNAPSACK/`.

## 2. Datos y óptimos

`DATA/instances/KNAPSACK/generate.py` usa una semilla fija (`20260828`) para crear diez instancias de 60 objetos y una instancia pequeña `toy3` usada como oráculo de pruebas.

Formato:

```text
n capacity
value_1 weight_1
value_2 weight_2
...
value_n weight_n
```

Los óptimos exactos se calculan mediante programación dinámica y se guardan en `DATA/instances/KNAPSACK/opt/optimums.txt`. Esto permite reportar el **gap porcentual real** de cada metaheurística.

## 3. Algoritmo nuevo: LAHC

Se agregó **Late Acceptance Hill Climbing (LAHC)** en `algorithm/LateAcceptanceHillClimbing.py`.

Hill Climbing tradicional solo acepta mejoras y puede quedar atrapado rápidamente. LAHC mantiene un historial circular de longitud `L`. Un candidato se acepta cuando mejora la solución actual o cuando no es peor que la solución registrada `L` iteraciones atrás. Con esto puede atravesar deterioros temporales y escapar de óptimos locales.

La configuración se encuentra en `DATA/config/LAHC/`:

- `LAHC20.json`: historial 20.
- `LAHC100.json`: historial 100.
- `LAHC200.json`: historial 200.
- `LAHC500.json`: historial 500.
- `LAHCk.json`: configuración de referencia inicial (50).

Todas usan `FLIPPING`, el operador binario existente en MHP.

## 4. Integración con Agent

`agent/Agent.py` registra `LAHC` de la misma manera que GA, SA, RW, TS, ILS y GRASP. Por ejemplo:

```python
from agent.Agent import Agent
from examples.KnapsackProblem import KnapsackProblem

problem = KnapsackProblem("kp60_01.txt")
agent = Agent(problem, ["LAHC", "LAHC100", 2000, 3])
agent.init()
```

## 5. Comparación

`ExecuteKnapsack.py` compara el algoritmo nuevo contra tres algoritmos binarios ya existentes:

- LAHC: algoritmo nuevo.
- GA: algoritmo genético.
- SA: recocido simulado.
- RW: caminata aleatoria como línea base.

Todos reciben el **mismo número de evaluaciones y corridas**. La semilla de NumPy se fija por par instancia/algoritmo para hacer el experimento reproducible.

Comandos principales:

```bash
python ExecuteKnapsack.py --quiet
python ExecuteKnapsack.py --instances 5 --evals 2000 --runs 3 --quiet
python ExecuteKnapsack.py --history --instances 5 --evals 2000 --runs 3 --quiet
python ExecuteKnapsack.py --full --evals 5000 --runs 5 --quiet
```

`--history` compara distintas longitudes de memoria de LAHC. `--full` habilita las diez instancias; se deja separado porque el GA original de la plataforma hace esa corrida considerablemente más costosa.

## 6. Pruebas

Se añadieron:

- `tests/test_knapsack_reader.py`: lectura, metadatos, factibilidad, penalización, óptimo del caso `toy3` y correspondencia con la tabla de óptimos.
- `tests/test_lahc.py`: carga de configuración, presupuesto de evaluaciones, conservación del mejor estado, integración con `Agent` y validez binaria.

Para ejecutar todo el proyecto:

```bash
python -m unittest discover tests -v
```

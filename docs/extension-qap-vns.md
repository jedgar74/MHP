# Extension QAP + VNS

**Fecha:** 27 de agosto de 2026  
**Base de diseño:** `docs/diseno-pfsp-ts.md`

## Resumen

Se incorpora una segunda extensión independiente de PFSP + TS:

- **Problema:** Asignación Cuadrática (QAP), en `examples/QuadraticAssignmentProblem.py`.
- **Metaheurística:** Búsqueda de Vecindario Variable (VNS), en
  `algorithm/VariableNeighborhoodSearch.py`.
- **Instancia reproducible:** `DATA/instances/QAP/qap4.txt`.
- **Configuración:** `DATA/config/VNS/VNSQAP.json`.
- **Ejecutar experimento:** `python ExecuteQAP.py`.
- **Pruebas:** `python -m unittest tests/test_qap_vns.py`.

## Problema y representación

Hay `n` instalaciones y `n` localizaciones. Una solución permutacional `p` asigna la
instalación `i` a la localización `p[i]`. Con `F` como matriz de flujos y `D` como matriz de
distancias, se minimiza:

$$
coste(p) = \sum_{i=0}^{n-1}\sum_{j=0}^{n-1} F_{ij}D_{p_i p_j}
$$

El lector acepta un fichero con el tamaño, la sección `flow` y la sección `distance`. El
evaluador valida que la solución sea una permutación completa, evitando costes silenciosos
para soluciones inválidas. QAP no expone una matriz de costes entre pares de localizaciones,
por lo que `getCostMatrix()` devuelve `None` y ACO no se ofrece como método aplicable.

## Metaheurística e integración

VNS comienza con una solución aleatoria y explora, en orden, los vecindarios `SWAP` e
`INSERTION`. Toma el mejor candidato del vecindario; si mejora, vuelve al primer vecindario,
y si no mejora, avanza al siguiente. El ciclo termina al agotar el presupuesto de
evaluaciones del `Counter`. Cada candidato se evalúa antes de incrementar el contador, y se
conserva siempre el mejor estado global.

La sigla `VNS` se registró en `agent/Agent.py` para `init()` e `init2()`. El contrato de la
plataforma se mantiene: la instancia se construye como problema, la configuración se lee por
sigla y `Agent` administra repeticiones y estadísticas.

## Validación funcional

La instancia `qap4` usa matrices simétricas de 4x4. La enumeración de sus `4! = 24`
permutaciones establece un óptimo exacto de **96**, alcanzado por dos soluciones debido a la
simetría. Las pruebas comprueban:

1. lectura de tamaño y cálculo de un coste conocido;
2. óptimo exacto y número de soluciones óptimas;
3. alcance del óptimo por VNS con semilla fija;
4. respeto del presupuesto y validez de la permutación;
5. rechazo de soluciones con elementos repetidos.

## Validación experimental

`ExecuteQAP.py` ejecuta 30 corridas de una evaluación piloto, con semillas `0..29`, 100
evaluaciones por corrida y la instancia pequeña para la que se conoce el óptimo exacto. El
script imprime el mejor coste, la media y el número de éxitos sobre 30. La brecha se calcula
contra la enumeración exacta, no contra una cota heurística.

Comando:

```text
python ExecuteQAP.py
```

Este experimento valida la incorporación extremo a extremo: lectura de datos, construcción
del agente, selección de `VNS`, uso del archivo JSON, consumo del presupuesto y reporte
estadístico. Para estudiar escalabilidad se deben añadir instancias QAP mayores y sustituir la
enumeración exacta por una referencia publicada.

Resultado observado en esta versión: **mejor 96**, **media 96.60** y **21/30 corridas** con
el óptimo exacto. Las nueve corridas restantes terminaron en coste 98; la brecha máxima fue
por tanto $((98 - 96) / 96) 100 = 2.08\%$. El resultado es una validación piloto sobre una
instancia pequeña, no una afirmación de rendimiento general del algoritmo.

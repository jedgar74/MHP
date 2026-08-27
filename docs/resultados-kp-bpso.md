# Experimentación Knapsack + BPSO

## Diseño experimental

- Problema: 0/1 Knapsack.
- Algoritmos: BPSO, GA y SA.
- 6 instancias:
  - 2 de n=10
  - 2 de n=20
  - 2 de n=30
- 5 corridas independientes.
- presupuesto objetivo: 1000 evaluaciones.
- óptimos exactos calculados mediante programación dinámica.
- BPSO sin calibración exhaustiva.

## Resultados

| Instancia | Óptimo | BPSO gap % | GA gap % | SA gap % |
|---|---|---|---|---|
| kp_10_1 | 380 | 0.00 | 14.63 | 2.21 |
| kp_10_2 | 411 | 0.00 | 13.28 | 2.53 |
| kp_20_1 | 733 | 2.51 | 17.52 | 10.04 |
| kp_20_2 | 817 | 5.04 | 24.46 | 15.03 |
| kp_30_1 | 1295 | 9.13 | 24.69 | 18.90 |
| kp_30_2 | 1251 | 8.25 | 20.45 | 15.84 |

| Algoritmo | Gap medio | Rango medio | Observación |
|---|---|---|---|
| BPSO | 4.16 % | 1.00 | Menor gap en las 6 instancias; alcanza el óptimo en kp_10_1, kp_10_2 y kp_20_1 |
| SA | 10.76 % | 2.00 | Segundo en todas las instancias; óptimo en las dos de n=10 |
| GA | 19.17 % | 3.00 | Tercero en todas las instancias; nunca alcanza el óptimo |

Los gaps medios corresponden a la media de las 5 corridas sobre el óptimo exacto (DP) de cada instancia; ejecución de `ExecuteKnapsack.py` con 6 instancias × 3 algoritmos × 5 corridas × 1000 evals = 90 000 evaluaciones.

## Contraste estadístico

Prueba no paramétrica sobre la matriz de gaps medios (N=6 bloques × K=3 algoritmos), considerada como problema MIN (menor gap, mejor).

- **Friedman**: estadístico = 12.0000; valor crítico (α=0.05, gl=2) = 5.9915. Como 12.0000 > 5.9915, se rechaza la hipótesis nula de igualdad de desempeño: hay evidencia de diferencias entre los algoritmos. El framework imprime además "prob Chi-square function = 0.9975"; se trata de la **función de distribución acumulada** de la χ² con 2 gl evaluada en el estadístico (P(X ≤ 12.0) ≈ 0.9975), NO de un p-valor en sentido estricto. El p-valor del contraste es p ≈ 1 − 0.9975 ≈ 0.0025, coherente con el rechazo de la igualdad al 5 %.
- **Iman-Davenport**: el framework devuelve `inf`. No debe leerse como una medida normal: es una **degeneración matemática** provocada por la ordenación perfectamente consistente de los rangos (BPSO < SA < GA en las seis instancias según gap), que lleva el estadístico de Friedman a su máximo posible para N=6 y K=3 (12.0) y anula el denominador de la F de Iman-Davenport. El resultado queda sin valor informativo en este experimento.
- **Holm** (control = BPSO, mejor rango medio), valores reales obtenidos:
  - SA: estadístico = 1.7321 · p = 0.0416 · umbral Holm = 0.05 · marcada con `@` (significativa).
  - GA: estadístico = 3.4641 · p = 0.0003 · umbral Holm = 0.025 · marcada con `@` (significativa).

Según la implementación usada, ambas comparaciones quedan marcadas como significativas. No obstante, con solo 6 instancias el análisis tiene carácter **exploratorio** y debe interpretarse con cautela: la significancia reportada proviene de rangos perfectamente consistentes (BPSO < SA < GA en todas las instancias). La degeneración del Iman-Davenport ya descrita es una manifestación adicional de esa consistencia perfecta y refuerza la necesidad de no tratar estos valores como concluyentes.

## Conclusión

En el conjunto experimental evaluado, BPSO mostró el mejor comportamiento: menor gap medio (4.16 %), mejor rango medio (1.0) y los únicos óptimos alcanzados (kp_10_1, kp_10_2 y kp_20_1). SA quedó en segundo lugar (gap medio 10.76 %) y GA en tercero (gap medio 19.17 %), con estas ordenaciones idénticas en las 6 instancias.

El test de Friedman y la corrección de Holm sobre los rangos indican que las diferencias entre BPSO y los demás algoritmos son estadísticamente significativas en este experimento. No obstante, estas conclusiones se limitan a este conjunto reducido de instancias y presupuestos, por lo que no debe generalizarse que BPSO sea universalmente superior: en particular, BPSO no introdujo parámetros calibrados y el problema 0/1 Knapsack es un caso sencillo donde métodos de trayectoria también alcanzaron el óptimo.

## Limitaciones

- Solo 6 instancias.
- 5 corridas.
- Presupuesto objetivo de 1000 evaluaciones.
- BPSO sin calibración exhaustiva (usó la configuración por defecto).
- Pequeñas diferencias en evaluaciones reales por el criterio de parada de GA/SA dentro del framework existente: BPSO consume exactamente 1000, SA ≈1001 y GA entre 1004 y 1009 evaluaciones por corrida; se reportan los picos registrados.
- Resultados exploratorios; el Iman-Davenport degenera a `inf` por la concordancia perfecta de los rangos (Friedman alcanza su máximo para N=6, K=3).
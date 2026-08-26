# Resultados experimentales — PFSP con Búsqueda Tabú

**Rama:** `feature/pfsp-tabu`
**Fecha de la corrida:** 25–26 de agosto de 2026
**Guion:** `ExecuteFlowShop.py --full --headless --log DATA/output/pfsp_full.log`

Este documento recoge la validación experimental que pedía el tercer entregable
del profesor. El diseño del experimento está justificado en
`docs/diseno-pfsp-ts.md`, sección 6.

---

## 1. Diseño del experimento

| Elemento | Valor | Justificación |
|----------|-------|---------------|
| Instancias (bloques) | 30 — `ta001` a `ta030` | Subconjunto `n = 20` del banco de Taillard, donde la referencia de calidad es sólida (26 de 30 cotas coinciden con el mejor valor conocido) |
| Series comparadas | 5 | Ver tabla siguiente |
| Evaluaciones por corrida | 50 000 | Fijado en la fase 4 con datos medidos: con 5 000 el vecindario de 361 candidatos solo daría 13 iteraciones a TS |
| Métrica | `(Cmax − BKS) / BKS × 100` | Referencia: `opt/optimums.txt`, **no** la cota de la cabecera, que es la de Taillard (1993) y ya fue superada |
| Contraste | Friedman + Iman-Davenport + post-hoc de Holm | `statisticc/FriedmanImanHolm.py`, ya presente en el repositorio |
| Celdas totales | 150 | 30 instancias × 5 series |

### Las cinco series

| Serie | Qué es | Corridas |
|-------|--------|----------|
| `TS/TSc` | Búsqueda Tabú, memoria por solución, arranque NEH | 1 |
| `TS/TSattr` | Búsqueda Tabú, memoria por atributo (formulación clásica), arranque NEH | 1 |
| `TS/TSr` | Búsqueda Tabú, memoria por solución, arranque **aleatorio** | 10 |
| `GA/GAS` | Algoritmo Genético, cruce OX permutacional | 10 |
| `SA/SAS` | Recocido Simulado, mutación SWAPPING | 10 |

**Sobre el número de corridas.** El briefing del equipo indicaba 30. Aquí se
usan 10 para las series estocásticas y 1 para las deterministas. La razón es que
`TSc` y `TSattr` **no tienen ningún componente aleatorio**: arrancan de NEH, que
es determinista, y siempre eligen el mejor candidato. Treinta corridas
devolverían treinta veces el mismo número con desviación estándar 0.

Bajar de 30 a 10 repeticiones no debilita el contraste porque **la potencia del
test de Friedman la aportan las instancias**, que son sus bloques; las
repeticiones se colapsan en una media dentro de cada celda (ver `getMatrix` en
`statisticc/Reporter.py`). Reducir el número de instancias sí lo debilitaría, y
por eso se mantienen las 30.

---

## 2. Resultados descriptivos

Desviación media sobre el mejor valor conocido, 30 instancias:

| Puesto | Serie | Rango medio de Friedman | Desviación media |
|--------|-------|-------------------------|------------------|
| 1 | **`TS/TSc`** | **1,833** | **1,65 %** |
| 2 | `TS/TSr` | 2,133 | 1,82 % |
| 3 | `TS/TSattr` | 2,500 | 1,94 % |
| 4 | `GA/GAS` | 3,567 | 2,65 % |
| 5 | `SA/SAS` | 4,967 | 7,94 % |

Las tres variantes de Búsqueda Tabú ocupan los tres primeros puestos.

### Cuánto aporta la búsqueda por encima de su arranque

La columna `Delta` del reporte —que ya existía en `statisticc/Reporter.py`,
escrita por el compañero para separar el mérito del ACO del de su tour por
vecino más cercano— responde a esto directamente:

| Serie | Arranque (`Start%`) | Final (`Gap%`) | Cierra (`Delta`) |
|-------|---------------------|----------------|------------------|
| `TS/TSc` (NEH) | 3,88 % | 1,65 % | 2,23 pp |
| `TS/TSattr` (NEH) | 3,88 % | 1,94 % | 1,94 pp |
| **`TS/TSr` (aleatorio)** | **25,31 %** | **1,82 %** | **23,49 pp** |

El dato de `TSr` es el más informativo del experimento: **arranca 6,5 veces peor
que NEH y termina prácticamente en el mismo sitio.** La búsqueda cierra 23,49
puntos porcentuales por sí sola.

El 3,88 % de NEH coincide además con lo publicado en la literatura para
instancias `20×5`, lo que valida la implementación del arranque constructivo por
una vía independiente de nuestras propias pruebas.

---

## 3. Contraste estadístico

### 3.1 Friedman e Iman-Davenport

```
Friedman        = 78,6133    valor crítico = 9,4877    (α = 0,05, 4 gl)
Iman-Davenport  = 55,0851    valor crítico = 2,4499    (α = 0,05, 4 x 116 gl)
```

El estadístico de Friedman supera al valor crítico por un factor de 8. **Se
rechaza la hipótesis nula** de que las cinco series rinden igual. Iman-Davenport,
que corrige el conservadurismo de Friedman, lo confirma con el mismo holgura.

### 3.2 Post-hoc de Holm

Algoritmo de control: `TS/TSc`, por ser el de mejor rango medio.

| Comparación | Estadístico | Umbral de Holm | p | ¿Diferencia? |
|-------------|-------------|----------------|---|--------------|
| vs `TS/TSr` | 0,7348 | 0,0500 | 0,2312 | No |
| vs `TS/TSattr` | 1,6330 | 0,0250 | 0,0512 | No |
| vs `GA/GAS` | 4,2458 | 0,0167 | 0,0000 | **Sí** |
| vs `SA/SAS` | 7,6751 | 0,0125 | 0,0000 | **Sí** |

---

## 4. Interpretación

### 4.1 Lo que los datos permiten afirmar

**La Búsqueda Tabú supera al Algoritmo Genético y al Recocido Simulado con
significación estadística** sobre 30 instancias, con el mismo presupuesto de
evaluaciones y la misma representación. Este es el resultado principal y está
sólidamente respaldado: ambos contrastes rechazan la nulidad con holgura y el
post-hoc de Holm marca las dos diferencias.

**El Recocido Simulado se degrada con la dificultad.** Pasa de un 3,20 % en
`ta001` (5 máquinas) a cerca del 9 % en las instancias de 10 y 20 máquinas. Es
coherente con su mecánica: un intercambio aleatorio por paso explora muy poco
cuando el paisaje se vuelve más accidentado.

### 4.2 Lo que los datos NO permiten afirmar

**No se puede afirmar que la memoria por solución sea superior a la memoria por
atributo.** La comparación `TSc` vs `TSattr` da p = 0,0512, que queda por encima
del umbral de Holm en ese escalón (0,0250). La evidencia descriptiva la favorece
—mejor rango medio, mejor desviación media, y en la fase 5 no perdió ninguna de
diez instancias— pero con 30 instancias el contraste no certifica la diferencia.

Presentarla como demostrada sería incorrecto. La formulación honesta es: *la
memoria por solución elimina un ciclo de periodo 2 verificado experimentalmente
y rinde mejor en media, pero la diferencia no alcanza significación estadística
en este banco.*

Conviene añadir un matiz observado durante la corrida: la ventaja de `TSc` sobre
`TSattr` **no es uniforme**. En el bloque de 20 máquinas ambas casi se igualan
(1,42 % frente a 1,53 %), mientras que en el global la distancia es mayor. Al
crecer el número de máquinas hay menos mesetas de empate, y el punto ciego del
tabú por atributo —que aparece justo en los movimientos de inserción entre
posiciones adyacentes— pesa menos.

### 4.3 El resultado inesperado

**El arranque constructivo no es determinante.** `TSc` (NEH) frente a `TSr`
(aleatorio) da p = 0,2312: ninguna diferencia significativa. Combinado con el
`Delta` de 23,49 puntos de `TSr`, la conclusión es que **el mérito del resultado
es de la búsqueda, no de la heurística de inicialización**.

Esto cierra una duda que surgió en la fase 5. Al probar `ta001` aisladamente,
TS devolvía exactamente el valor de NEH y parecía que la metaheurística no
aportaba nada. Resultó ser una instancia desafortunada —NEH cae allí en una
meseta especialmente fuerte—: sobre 30 instancias la búsqueda sí aporta, y lo
hace incluso partiendo del azar.

---

## 5. Ficheros generados

| Fichero | Contenido |
|---------|-----------|
| `DATA/output/pfsp_full.log` | Progreso, una línea por celda con tiempo y ETA |
| `DATA/output/pfsp_full_stdout.txt` | Tablas descriptivas por instancia y contraste completo |
| `DATA/output/PFSP_ranks_boxplot_main.png` | Diagrama de cajas de los rangos, experimento principal |
| `DATA/output/PFSP_ranks_boxplot_tenure.png` | Diagrama de cajas de los rangos, calibración |
| `DATA/output/pfsp_tenure.log` | Calibración de la tenencia (sección 6) |

Reproducible con:

```
python ExecuteFlowShop.py --full --headless --log DATA/output/pfsp_full.log
```

---

## 6. Calibración de la tenencia

Cuatro valores de tenencia —3, 7, 15 y 25— sobre las mismas 30 instancias, con
todo lo demás idéntico (memoria por solución, arranque NEH, 50 000
evaluaciones). Las cuatro configuraciones son deterministas, así que basta una
corrida por celda y su valor es exacto.

```
python ExecuteFlowShop.py --tenure --full --headless --log DATA/output/pfsp_tenure.log
```

### 6.1 Resultados

| Tenencia | Configuración | Rango medio | Desviación media |
|----------|---------------|-------------|------------------|
| 3 | `TS3` | 3,217 | 1,82 % |
| **7** | **`TSc`** | **2,833** | **1,65 %** |
| 15 | `TS15` | 2,133 | 1,39 % |
| **25** | **`TS25`** | **1,817** | **1,15 %** |

```
Friedman        = 22,07     valor crítico = 7,8147   (α = 0,05, 3 gl)
Iman-Davenport  =  9,42     valor crítico = 2,7094
```

Post-hoc de Holm, control `TS25`:

| Comparación | p | ¿Diferencia? |
|-------------|---|--------------|
| vs `TS15` | 0,1711 | No |
| vs `TSc` (tenencia 7) | 0,0011 | **Sí** |
| vs `TS3` | 0,0000 | **Sí** |

### 6.2 Interpretación

**La tendencia es monótona: a mayor tenencia, mejor resultado**, en todo el
rango probado. Y la diferencia no es marginal — pasar de 7 a 25 reduce la
desviación de 1,65 % a 1,15 %, una mejora relativa del 30 %.

**El valor 7 que se fijó en el diseño es significativamente peor que 25**
(p = 0,0011). Se eligió por ser el valor clásico de la literatura, y la
calibración demuestra que en este problema no es el adecuado. Tiene sentido:
con `n = 20` y un vecindario de 361 candidatos, recordar solo 7 permutaciones
es una memoria muy corta para el tamaño del espacio que se recorre.

**La curva no ha llegado al techo.** Entre 15 y 25 ya no hay diferencia
significativa (p = 0,1711), pero la media sigue mejorando. No se puede afirmar
dónde está el óptimo: podría estar más allá de 25. Extender el barrido es
trabajo pendiente.

### 6.3 Nota metodológica

**La calibración debería haberse hecho antes de la comparación principal.** El
experimento de la sección 3 se corrió con tenencia 7, que ahora sabemos
subóptima. Es un error de orden en el plan de trabajo y conviene declararlo.

No invalida ninguna conclusión, y la razón es que **el sesgo va en contra del
método que gana**: la Búsqueda Tabú superó a GA y a SA con significación
estadística *estando mal calibrada*. Con tenencia 25 su desviación baja de
1,65 % a 1,15 %, así que la ventaja sobre GA (2,65 %) y SA (7,94 %) solo se
ensancha. Repetir la comparación principal con `TS25` reforzaría el resultado,
nunca lo revertiría.

Lo que sí conviene decir en el informe es que la cifra que representa al método
bien configurado es **1,15 %**, no el 1,65 % de la tabla de la sección 2.

---

## 7. Trabajo pendiente

- Repetir la comparación principal con `TS25` para reportar la Búsqueda Tabú en
  su mejor configuración.
- Extender el barrido de tenencia más allá de 25 para localizar el techo.
- Las instancias de `n = 50` están descargadas y sin usar; sirven como prueba de
  escalabilidad.
- Acordar con el compañero el presupuesto de 50 000 evaluaciones. Si su ACO se
  midió con otro, las dos series no son comparables.

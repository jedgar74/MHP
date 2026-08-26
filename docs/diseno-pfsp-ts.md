# Diseño: Flow Shop de permutación resuelto con Búsqueda Tabú

**Autora:** María Fernanda Cachopo Rojas
**Proyecto:** Extensión de la plataforma MHP (Metaheuristics Platform)
**Rama:** `feature/pfsp-tabu`
**Base:** `main` @ `5d1598f`
**Fecha:** 24 de agosto de 2026

---

## 1. Contexto y objetivo

La actividad consiste en extender la plataforma MHP con un problema de optimización nuevo y
una metaheurística nueva, y validar la incorporación experimentalmente. Según las
instrucciones del profesor, los entregables son tres:

1. Un nuevo problema de optimización, en `examples/`, con sus instancias en `DATA/instances/`.
2. Una nueva metaheurística, en `algorithm/`, con su configuración en `DATA/config/` y su
   integración en `agent/Agent.py`.
3. Validación experimental, aprovechando las clases estadísticas ya existentes
   (`BasicStats`, `FriedmanImanHolm`).

Este documento cubre el diseño de los tres. La implementación se reparte en las fases 2 a 7
del plan de trabajo.

### 1.1 Relación con el trabajo del compañero

El repositorio ya incorpora, en `main`, la extensión de José Gregorio Briceño: el problema
del viajante (TSP) con lector TSPLIB y la metaheurística de colonia de hormigas (ACO),
mergeadas en el PR #1.

El briefing que el equipo elaboró a partir del audio del profesor planteaba tres caminos
posibles. Este trabajo toma la **Opción C — dominio permutacional**, que proponía
literalmente *«Nuevo Problema: Flow Shop Scheduling Problem (FSSP)»* y *«Nuevo Algoritmo:
Tabu Search (TS)»*, y que quedó libre cuando el compañero optó por TSP + ACO.

Las dos extensiones son complementarias por diseño: ambas trabajan sobre representación
permutacional, lo que permite un estudio comparativo entre familias de metaheurísticas
sobre una base común (sección 7).

---

## 2. El problema: Permutation Flow Shop Scheduling Problem (PFSP)

### 2.1 Definición

Hay `n` trabajos que deben procesarse en `m` máquinas. Cada trabajo pasa por **todas** las
máquinas en el **mismo orden** (M1 → M2 → … → Mm). El tiempo de proceso del trabajo `j` en
la máquina `k` es `p[j][k]`, conocido y determinista.

La restricción que da nombre al problema —*de permutación*— es que **el orden de los
trabajos es el mismo en todas las máquinas**. Es decir, no se puede adelantar un trabajo en
la máquina 2 si iba detrás en la máquina 1. Esto reduce el espacio de búsqueda de
`(n!)^m` a `n!`, y es lo que permite representar una solución como una única permutación.

Restricciones adicionales del modelo clásico:

- Una máquina procesa un solo trabajo a la vez.
- Un trabajo se procesa en una sola máquina a la vez.
- No hay interrupción (*no preemption*): una vez empezada, la operación termina.
- Todos los trabajos están disponibles desde el instante 0.
- Los tiempos de preparación están incluidos en `p[j][k]`.

**Objetivo:** minimizar el *makespan* (`Cmax`), el instante en que el último trabajo termina
en la última máquina.

### 2.2 Formulación

Sea `π = (π(1), π(2), …, π(n))` una permutación de los `n` trabajos, y `C(π(i), k)` el
instante de terminación del trabajo en la posición `i` sobre la máquina `k`. Entonces:

```
C(π(1), 1) = p[π(1)][1]

C(π(i), 1) = C(π(i-1), 1) + p[π(i)][1]                        para i = 2..n

C(π(1), k) = C(π(1), k-1) + p[π(1)][k]                        para k = 2..m

C(π(i), k) = max{ C(π(i-1), k), C(π(i), k-1) } + p[π(i)][k]   para i = 2..n, k = 2..m

Cmax(π) = C(π(n), m)
```

El `max` es la clave del problema: un trabajo en la máquina `k` no puede empezar hasta que
(a) la máquina esté libre —terminó el trabajo anterior de la secuencia— y (b) el trabajo
haya terminado en la máquina anterior. El que llegue más tarde de los dos manda.

El cálculo es **O(n·m)** por evaluación, con una tabla de `n×m`.

El PFSP con `m ≥ 3` es NP-difícil en sentido fuerte, lo que justifica el uso de una
metaheurística.

### 2.3 Instancia de referencia calculada a mano

Esta instancia 3×3 es el **oráculo de prueba** del proyecto: el valor calculado a mano aquí
es contra el que se validará `evaluate()` en la fase 3. Sin un número verificado
manualmente no hay forma de saber si el resto de la implementación es correcta.

**Tiempos de proceso `p[trabajo][máquina]`:**

| Trabajo | M1 | M2 | M3 | Total |
|---------|----|----|----|-------|
| A       | 5  | 1  | 1  | 7     |
| B       | 1  | 1  | 5  | 7     |
| C       | 2  | 3  | 2  | 7     |

**Cálculo para π = (B, C, A):**

Máquina 1 — los trabajos se encadenan sin espera, es la primera máquina:

```
C(B,1) = 0 + 1 = 1
C(C,1) = 1 + 2 = 3
C(A,1) = 3 + 5 = 8
```

Máquina 2 — cada trabajo espera al máximo entre «máquina libre» y «trabajo listo»:

```
C(B,2) = max{ 0 , C(B,1)=1 } + 1 = 1 + 1 = 2
C(C,2) = max{ C(B,2)=2 , C(C,1)=3 } + 3 = 3 + 3 = 6
C(A,2) = max{ C(C,2)=6 , C(A,1)=8 } + 1 = 8 + 1 = 9
```

Máquina 3:

```
C(B,3) = max{ 0 , C(B,2)=2 } + 5 = 2 + 5 = 7
C(C,3) = max{ C(B,3)=7 , C(C,2)=6 } + 2 = 7 + 2 = 9
C(A,3) = max{ C(C,3)=9 , C(A,2)=9 } + 1 = 9 + 1 = 10
```

**Cmax(B, C, A) = 10**

**Las seis permutaciones, para comprobar que el orden importa:**

| Permutación | Cmax |
|-------------|------|
| (B, C, A)   | **10** ← óptimo |
| (B, A, C)   | 13   |
| (C, B, A)   | 13   |
| (A, B, C)   | 14   |
| (C, A, B)   | 14   |
| (A, C, B)   | 17   |

El óptimo es único y el rango va de 10 a 17: un 70 % de diferencia entre la mejor y la peor
secuencia sobre los mismos tiempos de proceso. Eso hace de la instancia un buen caso de
prueba, porque un error en el `max` de la recurrencia daría un número distinto de 10 casi
con seguridad.

**Nota deliberada:** los tres trabajos tienen el mismo tiempo total de proceso (7). Esto no
es casual — sirve para probar que el desempate de la heurística NEH (sección 4.4) es
determinista, ya que NEH ordena precisamente por ese total.

### 2.4 Formato de las instancias — verificado

Se usan las instancias de **Taillard**, el banco de pruebas estándar para PFSP. El formato
que sigue quedó **verificado contra los ficheros realmente descargados** en la fase 2; no es
un supuesto:

```
number of jobs, number of machines, initial seed, upper bound and lower bound :
          20           5   873654221        1278        1232
processing times :
 54 83 15 71 77 36 53 38 27 87 76 91 14 29 12 77 32 87 68 94
 79  3 11 99 56 70 99 60  5 56  3 61 73 75 47 14 21 86  5 77
 16 89 49 15 89 45 60 23 57 64  7  1 63 41 63 47 26 75 77 40
 66 58 31 68 78 91 13 59 49 85 85  9 39 41 56 40 54 77 51 31
 58 56 20 85 53 35 53 41 69 13 86 72  8 49 47 87 58 18 68 28
```

La verificación arrojó tres hallazgos. **Dos de ellos corrigen supuestos de la primera
versión de este documento**, y quedan registrados como tales.

**(a) La matriz viene en orden máquina-mayor.** Confirmado: cada fila es una máquina y cada
columna un trabajo. Los ficheros `tai20_*` traen 5, 10 o 20 filas de 20 valores cada una. Al
leerla hay que transponerla o indexarla en consecuencia. Sigue siendo el error de lectura
más probable, y por eso el test del lector se escribe antes que el lector.

**(b) CORRECCIÓN — cada fichero contiene 10 instancias, no una.** La primera versión de este
documento asumía un fichero por instancia, como en el TSP del compañero. Es falso: los
ficheros de Taillard concatenan diez bloques `cabecera + tiempos`. `tai20_5.txt` tiene 80
líneas = 10 × (1 cabecera + 1 datos + 1 rótulo + 5 máquinas).

Esto cambia la firma del lector, y resulta que **el framework ya tiene ese patrón**:
`SingleMachineTotalWeightedTardinessProblem` recibe `namFile` como lista `[fichero, nVar]` y
selecciona el bloque con una variable `instancer`. El PFSP debe seguir el patrón de SMTWTP,
no el del TSP:

```python
problema = PermutationFlowShopProblem(["tai20_5.txt", 1])   # fichero, indice de instancia
```

A diferencia de SMTWTP —donde `instancer = 1` está fijo en el código y no se puede
seleccionar otra instancia— aquí el índice será un parámetro real. Es una mejora sobre el
patrón existente, no solo una copia.

**(c) CORRECCIÓN — la cota de la cabecera NO es el mejor valor conocido.** La primera versión
afirmaba que la cabecera permitía autovalidar las pruebas «sin depender de una tabla externa
de óptimos». Es incorrecto. La cabecera trae la cota superior de **Taillard (1993)**, la
mejor conocida en el momento de publicar el banco. Décadas de investigación posterior la han
mejorado. Comparando las 60 instancias descargadas contra la tabla de mejores valores
conocidos:

| Subconjunto | Instancias | Coinciden | Desviación máxima de la cabecera |
|-------------|-----------|-----------|----------------------------------|
| `n=20` (ta001–ta030) | 30 | 26 | +5 (ta007) |
| `n=50` (ta031–ta060) | 30 | 11 | +34 (ta041) |

La cabecera **nunca** da un valor menor que el mejor conocido, siempre igual o mayor. Si se
usara como referencia, un buen resultado en `ta041` podría reportar una desviación negativa
—como si hubiéramos batido el óptimo—, lo cual sería un artefacto de medición, no un
hallazgo.

**Decisión:** el lector lee la cabecera porque es metadato legítimo del fichero, pero
**la métrica de calidad usa `DATA/instances/PFSP/opt/optimums.txt`**, la tabla de mejores
valores conocidos, que se descarga junto con las instancias.

**(d) Consecuencia para el diseño experimental.** En las instancias de 20 trabajos la
cabecera casi siempre coincide con el mejor valor conocido (26 de 30), señal de que esos
valores llevan mucho tiempo asentados y son en la práctica óptimos. En las de 50 trabajos las
diferencias son grandes, señal de que siguen siendo difíciles. **Los experimentos principales
usarán el subconjunto `n = 20`** (ta001–ta030): son suficientemente pequeñas para que TS
complete iteraciones significativas dentro del presupuesto (ver el riesgo del coste del
vecindario en la sección 7) y su referencia de calidad es sólida. Las de `n = 50` quedan como
prueba de escalabilidad.

**Inventario descargado** en `DATA/instances/PFSP/`:

| Fichero | Instancias | n | m | Rango |
|---------|-----------|---|---|-------|
| `tai20_5.txt`  | 10 | 20 | 5  | ta001–ta010 |
| `tai20_10.txt` | 10 | 20 | 10 | ta011–ta020 |
| `tai20_20.txt` | 10 | 20 | 20 | ta021–ta030 |
| `tai50_5.txt`  | 10 | 50 | 5  | ta031–ta040 |
| `tai50_10.txt` | 10 | 50 | 10 | ta041–ta050 |
| `tai50_20.txt` | 10 | 50 | 20 | ta051–ta060 |
| `opt/optimums.txt` | — | — | — | mejores valores conocidos, ta001–ta060 |

Sesenta instancias en total, muy por encima de las «2 o 3» que pedía el briefing, y margen
de sobra para que el contraste de Friedman de la fase 6 tenga potencia estadística.

---

## 3. La metaheurística: Búsqueda Tabú (TS)

### 3.1 Justificación de la elección

La Búsqueda Tabú aparece en la **Tabla 1.1 del Capítulo 1** del texto del profesor, con
siglas **TS**, referencia **[94]** y —este es el punto— metáfora **«–»**. Es uno de los
pocos métodos del catálogo que **no se apoya en ninguna metáfora natural**: no imita
hormigas, ni recocido de metales, ni polinización. Su mecanismo se describe directamente en
términos de búsqueda: memoria, prohibición y aspiración.

Eso da el eje de la justificación. El catálogo del profesor contiene unas 80 técnicas, de
las cuales la enorme mayoría son de metáfora biológica o física, y buena parte de la Tabla
1.2 aparece incluso sin clasificar. Elegir deliberadamente un método sin metáfora, y decir
por qué, es una postura defendible: los mecanismos de TS son inspeccionables y ajustables
uno por uno, sin la capa de analogía que en la literatura reciente se ha criticado por
ocultar que muchos métodos «nuevos» son reformulaciones de otros ya conocidos.

**Contraste con el ACO del compañero.** La elección no es solo distinta, es
*complementaria* en las dos dimensiones que estructuran el campo:

| Dimensión              | ACO (ref. [73], Biológico) | TS (ref. [94], «–»)          |
|------------------------|----------------------------|------------------------------|
| Paradigma              | Poblacional                | Trayectoria (una solución)   |
| Modo de operar         | Constructivo               | Mejorativo                   |
| Tipo de memoria        | Implícita (feromona)       | Explícita (lista tabú)       |
| Uso del vecindario     | No enumera                 | Enumera y elige el mejor     |
| Escape de óptimos locales | Estocasticidad de la construcción | Prohibición + aspiración |
| Metáfora               | Sí                         | No                           |

Tener las dos en la misma plataforma, sobre la misma representación permutacional, es lo
que hace posible el estudio comparativo de la sección 7.

### 3.2 Componentes del algoritmo

**Representación.** Una permutación de los `n` trabajos, exactamente la que ya maneja
`state.Solution` cuando `typeState == "PERMUTATIONAL"`.

**Vecindario: inserción.** Un vecino se obtiene sacando el trabajo de la posición `i` y
reinsertándolo en la posición `j`, desplazando los intermedios. Se elige inserción y no
intercambio porque, en flow shop, un intercambio altera la posición de dos trabajos y
suele degradar mucho el makespan, mientras que la inserción desplaza suavemente la
secuencia; es el vecindario estándar en la literatura de PFSP.

El tamaño del vecindario es **(n−1)²** vecinos distintos. Para `n = 20`, son 361.

**Lista tabú — CORRECCIÓN de la fase 5.** El diseño inicial especificaba memoria *por
atributo*: cuando el trabajo `j` sale de la posición `p`, el par `(j, p)` queda prohibido
durante `tenure` iteraciones. Es la formulación clásica, y **falla sobre el vecindario de
inserción**. Se detectó instrumentando el bucle sobre `ta001`:

```
it 1  mov (2, 0, 2)
it 2  mov (16, 0, 1)
it 3  mov (8, 0, 1)
it 4  mov (16, 0, 1)   <- permutacion ya visitada
it 5  mov (8, 0, 1)    <- ciclo de periodo 2, 166 iteraciones sin mejorar
```

La causa es geométrica, no un error de programación. Mover el trabajo 16 de la posición 0 a
la 1 prohíbe `(16, 0)`. Pero esa inserción entre posiciones adyacentes **es un intercambio**:
el trabajo desplazado, el 8, queda en la posición 0, y mover *el 8* de 0 a 1 deshace
exactamente el cambio. El movimiento inverso se atribuye a otro trabajo, así que el atributo
de 16 no lo bloquea. En general, toda inserción adyacente admite dos atribuciones y la
memoria por atributo solo cubre una.

**Solución adoptada: memoria por solución.** Se guardan las últimas `tenure` permutaciones
visitadas y se prohíbe volver a cualquiera de ellas. Impide por construcción los ciclos de
longitud menor o igual que la tenencia. El coste es despreciable: comparar tuplas frente al
80 % del tiempo que consume `evaluate()` (ver sección 7).

**Los dos modos quedan implementados** y se seleccionan con el parámetro `tabuMode`, lo que
convierte el fallo en un experimento. Medido sobre las diez instancias `20×5`, con 40 000
evaluaciones:

| Modo | Gap medio | Victorias | Derrotas | Empates |
|------|-----------|-----------|----------|---------|
| `ATTRIBUTE` (clásico) | 1,69 % | 0 | 4 | 6 |
| `SOLUTION` (por defecto) | **1,40 %** | **4** | 0 | 6 |

`SOLUTION` no pierde en ninguna instancia. La comparación entre ambos modos entra en el
estudio de la fase 6 como resultado propio.

**Tenencia (`tenure`).** Número de iteraciones que un atributo permanece prohibido. Valor
inicial 7, el clásico de la literatura. Se calibra experimentalmente en la fase 6.

**Criterio de aspiración.** Si un movimiento prohibido produce una solución **mejor que la
mejor encontrada hasta el momento**, la prohibición se levanta. Sin este criterio, la lista
tabú podría descartar el óptimo global.

**Criterio de parada.** El del framework: `self.isStopCriteria()`, basado en el contador de
evaluaciones. Esto garantiza una comparación justa contra ACO, GA y SA, que usan el mismo
presupuesto.

### 3.3 Pseudocódigo

```
s  ← solución inicial (NEH)
s* ← s                                  # mejor global
T  ← lista tabú vacía

mientras no se agote el presupuesto de evaluaciones:

    N ← vecindario(s)                   # (n-1)^2 candidatos por inserción
    mejor_candidato ← nulo

    para cada (vecino, movimiento) en N:
        evaluar(vecino)                 # incrementa el contador del framework

        es_tabu  ← movimiento está en T
        aspira   ← fitness(vecino) mejor que fitness(s*)

        si (no es_tabu) o aspira:
            si mejor_candidato es nulo o vecino mejor que mejor_candidato:
                mejor_candidato ← vecino

    si mejor_candidato es nulo:         # todo el vecindario está prohibido
        continuar                       # (o vaciar T; ver sección 6)

    s ← mejor_candidato                 # se acepta AUNQUE empeore: así se escapa
                                        # del óptimo local
    registrar movimiento en T con tenencia
    envejecer T

    si s mejor que s*:
        s* ← s

devolver s*
```

El punto que distingue a TS de una búsqueda local pura está en la penúltima parte: **el
mejor candidato se acepta aunque sea peor que la solución actual**. Es la lista tabú, y no
la mejora, la que impide volver sobre los pasos ya dados.

### 3.4 Solución inicial: heurística NEH

En vez de arrancar de una permutación aleatoria, se usa **NEH** (Nawaz, Enscore y Ham), la
heurística constructiva de referencia para PFSP:

1. Calcular el tiempo total de proceso de cada trabajo, `T[j] = Σ_k p[j][k]`.
2. Ordenar los trabajos por `T[j]` decreciente.
3. Tomar los dos primeros y quedarse con el mejor de sus dos órdenes posibles.
4. Para cada trabajo restante, en orden: probar su inserción en **todas** las posiciones de
   la secuencia parcial y quedarse con la mejor.

Esta decisión es un espejo deliberado del trabajo del compañero: su ACO arranca de un tour
por vecino más cercano y expone el costo resultante como `ACO.lnnCost`, que `Agent`
recolecta en `self.startCosts`. La implementación de TS expondrá análogamente `self.nehCost`,
de modo que el mismo mecanismo de reporte funcione para las dos metaheurísticas sin
tocarlo.

**Desempate:** cuando dos trabajos tienen el mismo `T[j]` —como ocurre en la instancia
3×3 de la sección 2.3, donde los tres valen 7— se ordena por índice de trabajo ascendente.
La regla se fija explícitamente para que el algoritmo sea reproducible entre corridas.

---

## 4. Diseño de la integración

### 4.1 El problema — `examples/PermutationFlowShopProblem.py`

Clase `PermutationFlowShopProblem`, heredando de `problem.Problem`, siguiendo el patrón que
el compañero estableció en `TravelingSalesmanProblem`:

```python
class PermutationFlowShopProblem(Problem):

    def __init__(self, namInst=None, verbose=False):
        """
        @param list namInst : [fichero, indice] p.ej. ["tai20_5.txt", 1]
        """
        super().__init__()
        self.nameShort  = "PFSP"
        self.typeState  = "PERMUTATIONAL"
        self.typeProblem = "MIN"
        self.verbose    = verbose
        self.selOpers()
        if namInst is not None:
            self.readInstance(namInst)

    def readInstance(self, namFile):
        # namFile = [fichero, indice de instancia dentro del fichero]
        # Sigue el patron de SingleMachineTotalWeightedTardinessProblem, no el
        # del TSP: cada fichero de Taillard contiene 10 instancias. Ver 2.4(b).
        ..."

    def evaluate(self, s):             # makespan O(n*m); termina en s.setFitness(cmax)
        ...

    def getCostMatrix(self):
        return None                    # ver nota abajo
```

**Atributos propios:** `self.times` como matriz numpy `n × m` de tiempos de proceso,
`self.nMachines`, `self.upperBound` y `self.lowerBound` leídas de la cabecera, y
`self.instanceName` (p. ej. `"ta001"`) para poder cruzar con `optimums.txt`.

Recordar que la cabecera es metadato del fichero, **no** la referencia de calidad: para eso
está `optimums.txt`, por lo explicado en 2.4(c).

**Sobre `getCostMatrix()`.** El compañero añadió este método a `problem.Problem` para que
las metaheurísticas constructivas (ACO) pudieran obtener la matriz de costos. El PFSP **no
es un problema de grafo**: no existe una matriz de costos `N×N` entre trabajos. Por tanto se
devuelve `None`, que es el valor por defecto de la clase base. La consecuencia práctica es
deseable: si alguien intenta ejecutar ACO sobre PFSP, el ACO lo rechaza limpiamente —hay un
test suyo que cubre justamente ese caso— en vez de fallar de forma confusa.

**Detalles de lectura heredados del patrón del compañero:** normalizar los saltos de línea
de Windows, descartar líneas vacías, y validar que las dimensiones declaradas en la
cabecera coinciden con los datos leídos, lanzando `ValueError` si no.

### 4.2 La extensión de `operators/OperatorsPerm.py`

**Esta es la parte estructural del trabajo, y corrige un supuesto del briefing.**

El briefing del equipo afirmaba que la Opción C *«usa `OperatorsPerm` (swapping, ox, pmx,
etc.)»*, dando a entender que los operadores existentes bastaban. Al revisar el código
fuente —el briefing se redactó a partir del README, no del fuente— resulta que no bastan:

- `OperatorsPerm.mutation()` solo admite `'SWAPPING'`, y devuelve **un** vecino obtenido por
  un intercambio **aleatorio**. Es lo que necesitan SA y GA, que muestrean el vecindario al
  azar.
- Los operadores `ox`, `pmx`, `crossoverCycle`, etc. son operadores de **cruce**, propios de
  algoritmos poblacionales. No generan vecindarios.
- La Búsqueda Tabú necesita lo contrario: **enumerar el vecindario completo** y elegir el
  mejor candidato no prohibido.

Esa API no existe en ninguna parte del repositorio. Hay que construirla.

**Y hay evidencia de que el profesor ya la tenía prevista.** Sus ficheros de configuración
huérfanos —métodos con configuración pero sin código— nombran exactamente los parámetros de
un generador de vecindarios:

```
DATA/config/HC/HCE.cfg        DATA/config/ILS/ILSFa.cfg
METHOD=HC                     INCLUDEMETHODS=HC
TYPEINITIAL=RANDOM            CONFIGMETHODS=HCF
FACTORNEIGHS=2                NICCONSTANT=2000
ALLNEIGHS=NONE                TYPEINITIAL=RANDOM
                              PERTURBATION=BLOCKING
                              FACTORNEIGHS=4
                              ALLNEIGHS=NONE
```

Los dos métodos que usan esos parámetros —Hill Climbing e Iterated Local Search— no tienen
implementación en el repositorio. Construir esta API no solo habilita TS: deja el terreno
listo para HC, ILS y VNS.

**Diseño propuesto:**

```python
def neighborhood(self, name, sol, factor=None):
    """
    Devuelve la lista de vecinos de sol junto con el movimiento que los genera.

    @param String name : 'INSERTION' o 'SWAP'
    @param state.Solution sol :
    @param float factor : None enumera todo el vecindario; un valor k muestrea
                          k*nVar vecinos al azar (ver ALLNEIGHS/FACTORNEIGHS)
    @return list : lista de tuplas (vecino, movimiento)
    """
    if name == 'INSERTION':
        return self.neighborhoodInsertion(sol, factor)
    elif name == 'SWAP':
        return self.neighborhoodSwap(sol, factor)
    else:
        raise ValueError("This neighborhood method is not defined: "+name)
```

**Decisión de diseño clave:** cada elemento de la lista es la tupla `(vecino, movimiento)`,
no solo el vecino. El movimiento —`(trabajo, posición_origen, posición_destino)`— es
indispensable, porque la lista tabú se gestiona por atributos del movimiento, no por
soluciones. Devolver solo los vecinos haría imposible implementar TS.

Se respeta la forma de `mutation(name, sols)`, incluido el `raise ValueError` con el mismo
texto, para que el archivo no desentone.

**Interpretación de los parámetros del profesor.** Como no hay código que consultar, se
adopta —y se documenta— esta lectura:

| Parámetro      | Valor        | Significado adoptado                          |
|----------------|--------------|-----------------------------------------------|
| `ALLNEIGHS`    | `"ALL"`      | Enumerar el vecindario completo, `(n−1)²`     |
| `ALLNEIGHS`    | `"NONE"`     | Muestrear un subconjunto al azar               |
| `FACTORNEIGHS` | `k`          | Con `ALLNEIGHS=NONE`, tamaño de muestra `k·n` |

> Esta interpretación es nuestra, no está documentada en el repositorio. Queda registrada
> aquí para que sea revisable y para no presentarla como si viniera del framework.

**Restricción de seguridad:** `OperatorsPerm` es el **único archivo compartido** con el ACO
del compañero. Se modifica **solo por adición** —métodos nuevos, sin tocar los existentes— y
la suite completa se vuelve a ejecutar antes de continuar. Si los 10 tests actuales dejan de
pasar, se rompió su trabajo.

### 4.3 La metaheurística — `algorithm/TabuSearch.py`

Clase `TabuSearch`, heredando de `algorithm.Heuristic`, copiando la estructura de
`SimulatingAnnealing`, que es el trayectorial ya existente:

```python
class TabuSearch(Heuristic):

    def __init__(self, problem, fileConfig, run=True):
        super().__init__()
        self.shortTerm  = "TS"
        self.objProblem = problem
        self.setParameters(fileConfig)

        self.status.stateInitial = self.buildNEH()      # o RANDOM segun config
        self.objProblem.evaluate(self.status.stateInitial)
        self.objProblem.counter.incCount()
        self.status.stateFinal = copy.deepcopy(self.status.stateInitial)
        self.nehCost = self.status.stateInitial.fitness  # espejo de ACO.lnnCost

        if run:
            self.tabuSearch()

    def setParameters(self, fileConfig):   # JSON + valores por defecto
        ...

    def run(self, solution=None):          # requerido por Agent.init2()/run()
        ...

    def replaceSolution(self, solution):   # requerido por Agent.replacement()
        ...
```

**Contrato con el framework, punto por punto:**

- El bucle principal se controla con `self.isStopCriteria()`.
- Cada evaluación llama a `self.objProblem.evaluate(sol)` seguido de
  `self.objProblem.counter.incCount()`.
- Las comparaciones usan `self.objProblem.op.isBetter([a, b])`, que ya respeta
  `typeProblem` MIN/MAX. **No** se compara con `<` directamente.
- El resultado se deja en `self.status.stateFinal`, que es lo que `Agent` recoge.
- `setParameters` rellena los valores ausentes del JSON con los de por defecto, igual que
  hace `SimulatingAnnealing`, para que una configuración incompleta no rompa la ejecución.

### 4.4 Registro en `agent/Agent.py`

Tres cambios:

1. Importar: `from algorithm.TabuSearch import *`
2. En `init()`, añadir el bloque:

```python
if (self.metaheuristic == "TS") :
    TS = TabuSearch(self.problem, self.paraMetaheuristic)
    self.stats.add(TS.status.stateFinal)
    self.startCosts.append(TS.nehCost)
```

3. En `init2()`, añadir:

```python
if (self.metaheuristic == "TS") :
    self.objMetaheuristic = TabuSearch(self.problem, self.paraMetaheuristic, False)
```

> **Atención:** son **dos** bloques distintos en dos métodos distintos. `init()` ejecuta las
> corridas completas; `init2()` prepara el objeto para el modo cooperativo. Registrar solo
> el primero es un bug silencioso: el método parece funcionar hasta que alguien lo usa desde
> una búsqueda cooperativa y obtiene `None`.

### 4.5 Configuración — `DATA/config/TS/TSc.json`

Formato JSON, como el `ACOS.json` del compañero, pero conservando los nombres de parámetro
que el profesor ya había fijado en sus `.cfg`:

```json
{
    "tenure": 7,
    "neighborhood": "INSERTION",
    "tabuMode": "SOLUTION",
    "allNeighs": "ALL",
    "factorNeighs": 2,
    "aspiration": true,
    "initialTypeSolution": "NEH"
}
```

Se prevén variantes `TSc7.json`, `TSc15.json`, etc., para la calibración de la tenencia en
la fase 6.

---

## 5. Decisiones fijadas

Estas decisiones se toman **ahora** para no discutirlas a mitad de la implementación. Si
alguna cambia, cambia aquí primero y luego en el código.

| Elemento              | Decisión                                     | Motivo |
|-----------------------|----------------------------------------------|--------|
| Representación        | Permutación de `n` trabajos                  | Reutiliza `OperatorsPerm` y `Solution.initRandomizePer()` sin cambios |
| Objetivo              | Makespan `Cmax`, minimizar                   | `typeProblem = "MIN"`, coherente con el resto de la plataforma |
| Vecindario            | Inserción, `(n−1)²` vecinos                  | Estándar en PFSP; el intercambio degrada demasiado el makespan |
| Lista tabú            | **Por solución** (`tabuMode=SOLUTION`)       | La versión por atributo cicla sobre inserciones adyacentes; ver 3.2 |
| Tenencia              | Estática, valor inicial 7                    | Valor clásico; se calibra en la fase 6 |
| Aspiración            | Levantar la prohibición si mejora el récord  | Evita descartar el óptimo global |
| Solución inicial      | NEH, con desempate por índice ascendente     | Espeja el arranque por vecino más cercano del ACO |
| Criterio de parada    | `self.isStopCriteria()` del framework        | Presupuesto de evaluaciones: comparación justa |
| Instancias            | Taillard, 60 descargadas; experimentos sobre `n=20` | Ver 2.4(d): en `n=20` la referencia de calidad es sólida |
| Referencia de calidad | `opt/optimums.txt`, **no** la cabecera       | La cabecera trae la cota de 1993, ya superada; ver 2.4(c) |
| Selección de instancia| `[fichero, índice]`, patrón de SMTWTP        | Cada fichero contiene 10 instancias; ver 2.4(b) |
| Corridas              | 30 por configuración                         | Número fijado en el briefing del equipo |

---

## 6. Plan de validación

### 6.1 Pruebas unitarias

Se usa `unittest`, como el compañero, ejecutable con `python -m unittest discover tests/`.
No hace falta instalar nada.

**`tests/test_pfsp_reader.py`** — se escribe **antes** que el lector:

- Las dimensiones leídas coinciden con las declaradas en la cabecera, en las 60 instancias
  de los seis ficheros.
- Cada fichero entrega exactamente 10 instancias, y el índice las selecciona correctamente
  (comprobar que el índice 2 no devuelve la instancia 1).
- La matriz de tiempos tiene forma `n × m` y todos sus valores están entre 1 y 99, que es el
  rango con el que Taillard generó el banco.
- Se leen correctamente las cotas superior e inferior de la cabecera.
- Un índice fuera de rango y una cabecera inconsistente lanzan `ValueError`.
- **`Cmax(B, C, A) == 10`** sobre la instancia 3×3 de la sección 2.3, y las otras cinco
  permutaciones dan 13, 13, 14, 14 y 17.

**`tests/test_neighborhood.py`:**

- El vecindario de inserción de una permutación de tamaño `n` tiene exactamente `(n−1)²`
  elementos.
- Todos los vecinos son permutaciones válidas: sin repetidos y con los mismos elementos.
- Ningún vecino es igual a la solución de origen.
- Cada vecino viene acompañado de un movimiento coherente con la transformación.
- Un nombre de vecindario inexistente lanza `ValueError`.

**`tests/test_tabu.py`:**

- No se excede el presupuesto de evaluaciones (el ACO tiene un test equivalente; conviene
  reproducir la comprobación porque la enumeración del vecindario evalúa por lotes).
- Un movimiento registrado como tabú no se deshace antes de que expire la tenencia.
- El criterio de aspiración sí acepta un movimiento prohibido cuando mejora el récord.
- Un JSON incompleto no rompe la ejecución: `setParameters` rellena los valores por defecto.
- Calidad: la desviación sobre `ta001` queda por debajo del 5 % con presupuesto fijo.

**Regresión obligatoria:** los 10 tests existentes deben seguir pasando después de tocar
`OperatorsPerm`.

### 6.2 Experimentación

Guion `ExecuteFlowShop.py` en la raíz, espejo de `ExecuteTSP.py`.

- **Métodos comparados:** TS, GA y SA sobre las mismas instancias y el mismo presupuesto.
  Las configuraciones comparadoras quedaron **verificadas en la fase 3**: `SA`/`SAS` usa
  mutación `SWAPPING` y `GA`/`GAS` usa cruce `OX`, ambos permutacionales, y ambos corren
  sobre PFSP sin modificar nada. Ojo: la configuración `GAc.json` **no** sirve, porque
  declara cruce `LAPLACE`, que es para variables reales.
- **Corridas:** 30 por configuración; se reportan media, mejor solución y desviación
  estándar, que es exactamente lo que devuelve `BasicStats`.
- **Aviso medido en la fase 5: TS con arranque NEH es determinista.** El arranque no tiene
  azar y la selección del mejor candidato tampoco, así que las 30 corridas devuelven el mismo
  valor y la desviación estándar es 0. No es un fallo, pero hay que decidirlo antes de correr:
  o se reporta TS con una sola corrida por instancia —su valor es exacto, lo que de hecho
  favorece al contraste de Friedman, que trabaja por rangos entre instancias— o se usa la
  configuración `TSr.json`, con arranque aleatorio, para obtener dispersión comparable a la de
  GA, SA y ACO. Se recomienda reportar ambas: `TSc` como resultado del método y `TSr` para la
  comparación de varianza.
- **Instancias:** el subconjunto `n = 20` (ta001–ta030), por lo argumentado en 2.4(d).
- **Métrica:** desviación porcentual respecto del **mejor valor conocido** de
  `opt/optimums.txt`, `(Cmax − BKS) / BKS × 100`. **No** se usa la cota de la cabecera: en
  `ta041` daría una desviación negativa espuria de hasta un 1 %.
- **Contraste estadístico:** `statisticc/FriedmanImanHolm.py` — Friedman, Iman-Davenport y
  post-hoc de Holm. Son unas 900 líneas ya presentes en el repositorio que ningún guion usa
  actualmente; activarlas es parte del valor de esta entrega.
- **Calibración:** al menos tres valores de tenencia, reportando cuál gana y por qué.

### 6.3 Estudio comparativo conjunto

Con TSP + ACO (del compañero) y PFSP + TS (esta extensión), la plataforma queda con dos
problemas permutacionales y dos metaheurísticas nuevas de familias opuestas, más las
existentes GA y SA. Eso habilita un análisis cruzado que ninguna de las dos extensiones
podría sustentar por separado.

Para que los resultados sean comparables, el presupuesto de evaluaciones y el número de
corridas deben ser los mismos en ambos trabajos. Es el único acuerdo experimental que hay
que cerrar con el compañero, y basta con hacerlo antes de las corridas finales.

---

## 7. Riesgos y puntos abiertos

**Coste de enumerar el vecindario — MEDIDO en la fase 4.** La estimación se confirmó. Con
`n = 20` el vecindario de inserción tiene exactamente 361 candidatos distintos, y cada uno
consume una evaluación del contador:

| Concepto | Coste medido |
|----------|--------------|
| Generar el vecindario (361 vecinos) | 9,4 ms |
| Evaluar los 361 vecinos | 37,0 ms |
| **Iteración completa de TS** | **46,4 ms** |
| Presupuesto 5 000 evaluaciones | **13 iteraciones**, 0,6 s por corrida |
| Presupuesto 50 000 evaluaciones | **138 iteraciones**, 6,4 s por corrida |

Trece iteraciones son insuficientes: con tenencia 7, la lista tabú apenas alcanzaría a
llenarse dos veces antes de que se agote el presupuesto, y la memoria —que es el mecanismo
entero del método— no llegaría a actuar.

Un dato secundario relevante: **la generación solo cuesta el 20 % del total**; el 80 % es
evaluar. Es decir, el `copy.deepcopy` por vecino no es el cuello de botella, y no merece la
pena optimizarlo. Lo que domina es `evaluate()`, que es exactamente lo que el contador del
framework mide. La contabilidad de esfuerzo es honesta.

**Decisión para la fase 6:** subir el presupuesto común a **50 000 evaluaciones** en lugar de
muestrear con `FACTORNEIGHS`. Mantiene la comparación limpia frente a ACO, GA y SA —todos
reciben el mismo presupuesto— mientras que muestrear cambiaría la naturaleza del método. El
coste en tiempo es asumible: 30 corridas sobre las 30 instancias de `n = 20` son unas
1,6 horas para TS, y menos para los demás. `FACTORNEIGHS` queda implementado y probado por si
hiciera falta escalar a `n = 50`.

**Aceleraciones de evaluación.** Existe una técnica clásica que evalúa todas las inserciones
de un trabajo en `O(n·m)` en lugar de `O(n²·m)`. No se va a usar: el framework mide el
esfuerzo contando llamadas a `evaluate()`, y una evaluación acelerada rompería la
equivalencia de presupuesto frente a ACO, GA y SA. La comparación justa pesa más que la
velocidad.

**Vecindario íntegramente prohibido.** Si todos los candidatos son tabú y ninguno aspira, el
pseudocódigo de la sección 3.3 no tiene candidato que elegir. La alternativa habitual es
vaciar la lista tabú y reintentar. Con aspiración activada la situación es rara, pero el
caso debe estar cubierto en el código para no quedar en un bucle sin avance.

**Conflicto en `OperatorsPerm`.** Único archivo compartido con el trabajo del compañero.
Mitigación: avisar antes de tocarlo, modificar solo por adición, y correr la suite completa
antes de seguir.

**Formato de las instancias.** Todo el diseño del lector asume la cabecera de Taillard de la
sección 2.4. Verificar el fichero real es una tarea explícita de la fase 2, previa a
escribir código.

---

## 8. Referencias

- Tabla 1.1, Capítulo 1 «Conceptos Básicos», del texto del profesor: **TS**, referencia
  **[94]**, metáfora «–». *(Confirmar la entrada bibliográfica exacta contra la lista de
  referencias del texto.)*
- Tabla 1.1, misma fuente: **ACO**, referencia **[73]**, metáfora «Biológico» — la
  extensión del compañero.
- Glover, F. — originador de la Búsqueda Tabú y de los conceptos de memoria adaptativa,
  lista tabú y criterio de aspiración.
- Nawaz, M.; Enscore, E.; Ham, I. — heurística NEH para flow shop.
- Taillard, É. — banco de instancias de referencia para PFSP, y vecindario de inserción.
- Briefing del equipo, «Opción C: Dominio Permutacional», elaborado a partir del audio del
  profesor.

---

## Anexo: registro de cambios de este documento

| Fecha | Cambio |
|-------|--------|
| 2026-08-24 | Versión inicial. Decisiones de la sección 5 fijadas. |
| 2026-08-25 | Fase 2. Formato de instancias verificado sobre ficheros reales. Dos correcciones: cada fichero trae 10 instancias, no una (2.4b); la cota de la cabecera no es el mejor valor conocido, la métrica pasa a `optimums.txt` (2.4c). Propagado a 4.1, 5, 6.1 y 6.2. |
| 2026-08-25 | Fase 5. `algorithm/TabuSearch.py` implementado y registrado en `Agent.init()` e `init2()`; 16 tests nuevos, 48 en total en verde. **Corrección de diseño:** la lista tabú por atributo cicla con periodo 2 sobre el vecindario de inserción (ver 3.2); se añade memoria por solución como modo por defecto y se conservan ambos para compararlos en la fase 6. `evaluate()` del PFSP pasa a recorrer `len(idx)` en vez de `nVar` para admitir las secuencias parciales que NEH necesita. Calidad sobre las 10 instancias 20×5: NEH solo 3,30 % — TS 1,40 %. |
| 2026-08-25 | Fase 4. API de vecindarios anadida a `OperatorsPerm` **solo por adicion** (135 lineas, 0 eliminaciones); 11 tests nuevos en verde y los 21 previos intactos — el ACO reproduce su 438/2,82 % exacto en `eil51`. Coste del vecindario medido: 46,4 ms por iteracion con n=20, lo que fija el presupuesto de la fase 6 en 50 000 evaluaciones (ver seccion 7). |
| 2026-08-25 | Fase 3. `examples/PermutationFlowShopProblem.py` y `tests/test_pfsp_reader.py` implementados; 11 tests nuevos en verde y los 10 originales sin tocar. El diseño de la sección 4.1 se implementó sin desviaciones. Referencias de calidad medidas en `ta001` (mejor conocido 1278): SA/SAS = 1339 (+4,77 %), GA/GAS = 1297 (+1,49 %). |

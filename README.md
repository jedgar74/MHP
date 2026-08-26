# MHP

El proyecto consiste en el desarrollo de una plataforma para ejecutar y desarrollar diferentes  metaheurísticas para solucionar diferentes problemas monoobjetivo (por ahora). Se desarrolló el software en Python 3 y en Spyder, se denominó MHP. 

Para la ejecución del proyecto debe generar un archivo python los elementos de la librería necesarios para realizar la simulación. Entre ellos destaca, el problema que desea resolver, las características de este último, el algoritmo utilizado, los parámetros del algoritmo, entre otros. Para simplificar se presentan dos  archivos python creados para tal caso para ejecutarse en la versión terminal o consola y otro en  Jupyter notebooks.

Para la primera forma, simplemente tiene que crear un archivo y se ejecuta de la siguiente manera:

python namefile.py

Puede usar como ejemplo el archivo ExecuteToSP.py y editarlo.

## Ejemplo
``` [pyhon]
 1. from agent.Agent import * 
 2. from examples.NQueens import * 
 3. problemv = NQueens(15)
 4. agent = Agent(problemv, ["SA", "SAS", 25000, 12])
 5. agent.init()
```

En la línea 1, se importa el núcleo principal de la biblioteca. En la línea 2,se importa el problema que queremos resolver, en este caso el problema de las n reinas. En la línea 3, se asignan las características de las n reinas al problema y se indica la instancia, en este caso 15 reinas. En la línea 4 se inicializa el agente con la información del problema y se le pasa por parámetros cuatro características básicas. La primera, el nombre del método a utilizar en este caso *SA*. El segundo, los parámetros de ese algoritmo, en este caso es *SAS*, que es un archivo de configuración de los principales parámetros. El tercero, corresponde al número de evaluaciones a utilizar como criterio de parada. El último parámetro corresponde al número de ejecuciones de esa misma instancia, en este caso 12. En la línea 5 se ejecuta el algoritmo
 
## Estructura 
La plataforma está compuesta por ocho directorios. El primero asociado a la parte estadística denominado *statistics*, que contiene información relacionada con la estadística básica y métodos como el de Friedman. El directorio *DATA* que a su vez contiene subdirectorios importantes como matlab, output, config, instances e input. Los más importantes son *config* donde se encuentran la configuración o los parámetros de configuración del algoritmo que se quiere ejecutar. *instances* donde contiene las instancias de un determinado problema y *output* donde se generan archivos de salida del programa. El directorio *state* representa la forma de describir las soluciones en las heurísticas y cómo esta se podrían agrupar. El directorio *operators* define diferentes métodos para manipular las soluciones dependiendo del tipo de dato que corresponde. *problem* define las características generales de un problema a resolver. *agent* es el directorio principal que encapsula la ejecución de las metaheurísticas. *algorithm* donde se definen los diferentes métodos de ejecución. *examples* corresponde a la definición de los diferentes problemas que se desean ejecutar.

## Extensión: Flow Shop de permutación con Búsqueda Tabú

Se incorporan un problema nuevo, el *Permutation Flow Shop Scheduling Problem* (PFSP), y una metaheurística nueva, la Búsqueda Tabú (TS). El PFSP consiste en secuenciar `n` trabajos que pasan por `m` máquinas siempre en el mismo orden, manteniendo la misma secuencia en todas ellas, de forma que se minimice el *makespan*: el instante en que el último trabajo termina en la última máquina.

``` [pyhon]
 1. from agent.Agent import *
 2. from examples.PermutationFlowShopProblem import *
 3. problemv = PermutationFlowShopProblem(["tai20_5.txt", 1])
 4. agent = Agent(problemv, ["TS", "TSc", 50000, 10])
 5. agent.init()
```

La estructura es la misma del ejemplo anterior, con una diferencia en la línea 3: la instancia se indica con una **lista de dos elementos**, el fichero y el índice. Los ficheros del banco de Taillard concatenan diez instancias cada uno, así que el nombre del fichero por sí solo no basta para identificarla. En la línea 4, *TS* es la Búsqueda Tabú y *TSc* su fichero de configuración.

### Instancias

En `DATA/instances/PFSP/` hay 60 instancias de Taillard, agrupadas en seis ficheros de diez (`tai20_5`, `tai20_10`, `tai20_20`, `tai50_5`, `tai50_10` y `tai50_20`). El subdirectorio `opt/` contiene los mejores valores conocidos, que son la referencia con la que se mide la calidad: las cotas que trae la cabecera de cada instancia son las de Taillard (1993) y la investigación posterior ya las ha superado.

### Configuraciones de la Búsqueda Tabú

Los parámetros se leen de `DATA/config/TS/`. Los principales son la tenencia (`tenure`), el vecindario (`neighborhood`, de momento `INSERTION` o `SWAP`), el tipo de memoria (`tabuMode`) y el arranque (`initialTypeSolution`, `NEH` o `RANDOM`).

| Configuración | Para qué |
|---|---|
| `TSc` | Configuración de referencia: tenencia 7, memoria por solución, arranque NEH |
| `TSattr` | Memoria por atributo, la formulación clásica |
| `TSr` | Arranque aleatorio en vez de NEH |
| `TS3`, `TS15`, `TS25` | Barrido de tenencia |

### Vecindarios

La Búsqueda Tabú necesita **enumerar** el vecindario y escoger el mejor candidato no prohibido, mientras que `mutation()` solo devuelve un vecino al azar, que es lo que necesitan SA y GA. Para ello se añade a `OperatorsPerm` el método `neighborhood(name, sol, factor)`, que devuelve la lista de vecinos junto con el movimiento que genera cada uno. El parámetro `factor` implementa el muestreo previsto por `FACTORNEIGHS`; con `None` se enumera el vecindario completo. Los métodos existentes no se modificaron.

### Experimentación

``` [pyhon]
 python ExecuteFlowShop.py --full --headless --log DATA/output/pfsp.log
 python ExecuteFlowShop.py --tenure --full --headless
```

El guion compara la Búsqueda Tabú contra los métodos ya presentes en la plataforma sobre 30 instancias, y cierra con el contraste no paramétrico de Friedman, Iman-Davenport y el post-hoc de Holm que ofrece `statisticc/FriedmanImanHolm.py`. Con `--tenure` se calibra la tenencia en lugar de comparar metaheurísticas.

El diseño y su justificación están en `docs/diseno-pfsp-ts.md`; los resultados obtenidos, en `docs/resultados-fase6.md`.

### Pruebas

``` [pyhon]
 python -m unittest discover tests/
```

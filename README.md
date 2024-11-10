# MHP

El proyecto consiste en el desarrollo de una plataforma para ejecutar y desarrollar diferentes  metaheurísticas para solucionar diferentes problemas monoobjetivo (por ahora). Se desarrolló el software en Python 3 y en Spyder, se denominó MHP. 

Para la ejecución del proyecto debe generar un archivo python los elementos de la librería necesarios para realizar la simulación. Entre ellos destaca, el problema que desea resolver, las características de este último, el algoritmo utilizado, los parámetros del algoritmo, entre otros. Para simplificar se presentan dos  archivos python creados para tal caso para ejecutarse en la versión terminal o consola y otro en  Jupyter notebooks.

Para la primera forma, simplemente tiene que crear un archivo y se ejecuta de la siguiente manera:

python namefile.py

Puede usar como ejemplo el archivo ExecuteToSP.py y editarlo.

## Ejemplo``` [pyhon]
 1. from agent.Agent import * 
 2. from examples.NQueens import * 
 3. problemv = NQueens(15)
 4. agent = Agent(problemv, ["SA", "SAS", 25000, 12])
 5. agent.init()
```

En la línea 1, se importa el núcleo principal de la biblioteca. En la línea 2,se importa el problema que queremos resolver, en este caso el problema de las n reinas. En la línea 3, se asignan las características de las n reinas al problema y se indica la instancia, en este caso 15 reinas. En la línea 4 se inicializa el agente con la información del problema y se le pasa por parámetros cuatro características básicas. La primera, el nombre del método a utilizar en este caso *SA*. El segundo, los parámetros de ese algoritmo, en este caso es *SAS*, que es un archivo de configuración de los principales parámetros. El tercero, corresponde al número de evaluaciones a utilizar como criterio de parada. El último parámetro corresponde al número de ejecuciones de esa misma instancia, en este caso 12. En la línea 5 se ejecuta el algoritmo
 
## Estructura 
La plataforma está compuesta por ocho directorios. El primero asociado a la parte estadística denominado *statistics*, que contiene información relacionada con la estadística básica y métodos como el de Friedman. El directorio *DATA* que a su vez contiene subdirectorios importantes como matlab, output, config, instances e input. Los más importantes son *config* donde se encuentran la configuración o los parámetros de configuración del algoritmo que se quiere ejecutar. *instances* donde contiene las instancias de un determinado problema y *output* donde se generan archivos de salida del programa. El directorio *state* representa la forma de describir las soluciones en las heurísticas y cómo esta se podrían agrupar. El directorio *operators* define diferentes métodos para manipular las soluciones dependiendo del tipo de dato que corresponde. *problem* define las características generales de un problema a resolver. *agent* es el directorio principal que encapsula la ejecución de las metaheurísticas. *algorithm* donde se definen los diferentes métodos de ejecución. *examples* corresponde a la definición de los diferentes problemas que se desean ejecutar.
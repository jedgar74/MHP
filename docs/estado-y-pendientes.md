# Estado del trabajo y pendientes

**Rama:** `feature/pfsp-tabu` (creada desde `main` @ `5d1598f`)
**Última actualización:** 26 de agosto de 2026

> **Nada está commiteado ni subido a GitHub.** Todo lo descrito aquí existe
> únicamente en el disco local. `origin/main` sigue en `5d1598f`, exactamente
> igual que antes de empezar.

---

## 1. Qué pidió el profesor y cómo va

| Entregable | Estado |
|------------|--------|
| Un problema de optimización nuevo, en `examples/` con instancias en `DATA/instances/` | **Hecho** — PFSP con lector Taillard |
| Una metaheurística nueva, en `algorithm/`, configurada en `DATA/config/` e integrada en `agent/Agent.py` | **Hecho** — Búsqueda Tabú |
| Validación experimental con `BasicStats` y `FriedmanImanHolm` | **Hecho** — ver `docs/resultados-fase6.md` |

El trabajo corresponde a la **Opción C** del briefing que el equipo elaboró a
partir del audio del profesor: *«Nuevo Problema: Flow Shop Scheduling Problem
(FSSP)… Nuevo Algoritmo: Tabu Search (TS)»*. Es la que quedó libre cuando el
compañero optó por TSP + ACO.

---

## 2. Lo que existe hoy

### Ficheros nuevos (2 387 líneas)

| Fichero | Líneas | Contenido |
|---------|--------|-----------|
| `docs/diseno-pfsp-ts.md` | 809 | Documento de diseño, con las correcciones registradas |
| `algorithm/TabuSearch.py` | 445 | La metaheurística |
| `ExecuteFlowShop.py` | 282 | Guion de experimentación |
| `tests/test_tabu.py` | 269 | 16 pruebas |
| `examples/PermutationFlowShopProblem.py` | 222 | El problema |
| `tests/test_neighborhood.py` | 182 | 11 pruebas |
| `tests/test_pfsp_reader.py` | 178 | 11 pruebas |

Más `DATA/instances/PFSP/` (60 instancias de Taillard, la instancia juguete
`toy3x3.txt` y la tabla de mejores valores conocidos) y `DATA/config/TS/`
(6 configuraciones).

### Cambios sobre código que ya existía

```
agent/Agent.py             |  10 ++++     registro de "TS" en init() e init2()
operators/OperatorsPerm.py | 135 +++++    API de vecindarios
2 files changed, 145 insertions(+)
```

**145 inserciones, 0 eliminaciones.** No se modificó ni se borró ninguna línea
existente. El ACO del compañero sigue reproduciendo su resultado exacto
(438 en `eil51`, 2,82 % de desviación).

### Pruebas

48 pruebas en verde con `python -m unittest discover tests/`. No hace falta
instalar nada: el proyecto usa `unittest`, no `pytest`.

---

## 3. Resultados obtenidos

Detalle completo en `docs/resultados-fase6.md`. Desviación media sobre el mejor
valor conocido, **30 instancias**, 50 000 evaluaciones:

| Puesto | Serie | Rango medio | Desviación |
|--------|-------|-------------|------------|
| 1 | **`TS/TSc`** | **1,833** | **1,65 %** |
| 2 | `TS/TSr` | 2,133 | 1,82 % |
| 3 | `TS/TSattr` | 2,500 | 1,94 % |
| 4 | `GA/GAS` | 3,567 | 2,65 % |
| 5 | `SA/SAS` | 4,967 | 7,94 % |

**La Búsqueda Tabú supera a GA y a SA con significación estadística**
(Friedman = 78,61 frente a un crítico de 9,4877; Holm marca ambas con p = 0,0000).

**No se puede afirmar** que la memoria por solución supere a la clásica por
atributo: p = 0,0512 frente a un umbral de Holm de 0,0250. Gana en media y en
rango, pero el contraste no lo certifica.

**El arranque constructivo no es determinante.** `TSr` parte de una permutación
aleatoria al 25,31 % de desviación, cierra 23,49 puntos y acaba en 1,82 %,
estadísticamente indistinguible del arranque NEH (p = 0,2312). El mérito es de
la búsqueda.

Calibración de la tenencia, mismas 30 instancias:

| Tenencia | 3 | **7** | 15 | **25** |
|----------|---|-------|----|----|
| Desviación | 1,82 % | **1,65 %** | 1,39 % | **1,15 %** |

La tenencia 7 usada en el experimento principal es significativamente peor que
la 25 (p = 0,0011). Ver la sección 4.2.

---

## 4. Qué falta para completar la tarea

### 4.1 Hecho desde la última actualización

- **Fase 6 completa.** Experimento principal (150 celdas) y calibración de la
  tenencia (120 celdas), con el contraste de Friedman, Iman-Davenport y Holm.
  Análisis en `docs/resultados-fase6.md`.
- **Fase 7, parte local.** Sección del PFSP en el `README.md` con ejemplo de uso
  verificado, y revisión de docstrings contra la convención del repositorio.

### 4.2 Lo que queda

**Repetir la comparación principal con tenencia 25.** Es lo más importante. La
calibración demostró que la tenencia 7 usada en el experimento principal es
significativamente peor que 25 (p = 0,0011): la desviación baja de 1,65 % a
1,15 %. La conclusión no cambia —la Búsqueda Tabú ya ganaba estando mal
calibrada— pero la cifra que debe representar al método es la de su mejor
configuración. Son unas 4 horas de cómputo.

**Extender el barrido de tenencia más allá de 25.** Entre 15 y 25 ya no hay
diferencia significativa, pero la media sigue mejorando: no se ha localizado el
techo.

**Commits.** No se ha hecho ninguno. Todo el trabajo está en el árbol sin
versionar.

**Pull Request.** No se ha abierto. Requiere subir la rama a GitHub, cosa que no
se ha hecho a propósito.

**Prueba de escalabilidad.** Las 30 instancias de `n = 50` están descargadas y
sin usar.

### 4.3 Decisiones que hay que cerrar con el compañero

Ninguna bloquea el trabajo propio, pero sí la parte conjunta:

1. **El presupuesto de evaluaciones.** Se fijó en 50 000 con datos medidos: con
   `n = 20` el vecindario de inserción tiene 361 candidatos, así que 5 000
   evaluaciones solo darían 13 iteraciones a TS y su lista tabú no llegaría a
   actuar. **Si el compañero midió su ACO con otro presupuesto, los números no
   son comparables** y habría que repetir una de las dos series.
2. **El número de corridas.** El briefing decía 30. Aquí se usan 10 para los
   métodos estocásticos y 1 para los deterministas, con la justificación de que
   la potencia del test de Friedman la aportan las instancias (sus bloques) y no
   las repeticiones.
3. **El aviso sobre `OperatorsPerm.py`.** Es el único fichero compartido. Se
   modificó solo por adición y la suite completa sigue en verde, pero él debería
   saberlo antes de tocarlo.
4. **El README no documentaba su extensión** (TSP + ACO): no había ninguna
   mención. La sección añadida ahora fija un patrón que él puede seguir.

### 4.4 Cosas verificadas que conviene no olvidar

- **`gh` no está instalado** y **nunca se comprobó si hay permiso de escritura**
  en `jedgar74/MHP`. Hay que resolverlo antes de intentar abrir el PR.
- La métrica de calidad usa `opt/optimums.txt`, **no** la cota de la cabecera de
  cada instancia: esa es la de Taillard (1993) y ya fue superada.
- Los experimentos usan el subconjunto `n = 20` (ta001–ta030).

## 5. Correcciones registradas durante el desarrollo

Estas quedan documentadas a propósito en el anexo de cambios del documento de
diseño. Que el diseño se corrija con datos medidos es parte de la metodología
que hay que mostrar, no algo que ocultar.

| Fase | Corrección |
|------|-----------|
| 2 | Cada fichero de Taillard contiene **10 instancias**, no una. Cambió la firma del lector, que pasa a seguir el patrón de `SingleMachineTotalWeightedTardinessProblem`. |
| 2 | La cota de la cabecera **no** es el mejor valor conocido. La métrica pasa a `optimums.txt`. |
| 4 | El coste del vecindario se midió (46,4 ms por iteración con `n=20`) y fijó el presupuesto en 50 000. |
| 5 | La lista tabú **por atributo cicla** con periodo 2 sobre el vecindario de inserción. Se añadió memoria por solución como modo por defecto. |
| 5 | `evaluate()` pasa a recorrer `len(idx)` en vez de `nVar`, porque NEH evalúa secuencias parciales. |
| 6 | **La tenencia 7 fijada en el diseño es subóptima**: la calibración la sitúa significativamente por debajo de 25. La calibración debió preceder a la comparación principal. |
| 6 | El modo `--tenure` sobrescribía el diagrama de cajas del experimento principal por usar el mismo nombre de fichero. Corregido: el nombre depende del modo. |

---

## 6. Cómo retomar

```bash
cd C:/Users/Mafer/proyecto_seminario/MHP
git branch --show-current          # feature/pfsp-tabu
python -m unittest discover tests/ # 48 pruebas, debe dar OK

tail -f DATA/output/pfsp_full.log  # seguir el experimento
```

El documento de diseño (`docs/diseno-pfsp-ts.md`) es la referencia: contiene la
formulación, la justificación de la elección con la taxonomía del profesor, el
diseño de cada pieza y el registro de todas las decisiones.

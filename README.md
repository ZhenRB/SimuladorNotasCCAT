# 📊 Simulador de Notas CCAT

Aplicación web que calcula el promedio final de un curso aplicando las **reglas de evaluación reales** de la Facultad de Ingeniería de Sistemas (FIIS-UNI), y responde a la pregunta que todos los alumnos se hacen:

> *«¿Con cuánto me salvo?»*

No solo te dice si aprobaste o no: **te dice exactamente qué nota necesitas en cada evaluación que te falta.**

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B3B?logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)

---

## 🎯 El problema

El promedio final en la UNI no es un promedio simple. Cada curso tiene su propia regla de ponderación, y encima hay que tratar correctamente tres casos especiales:

| Caso | Significado | Cómo lo trata la app |
|:-----|:------------|:---------------------|
| `NSP` | No se presentó | Equivale a 0 |
| `0A` | Ausente | No se promedia, pero tampoco se elimina |
| Sustitutorio | Examen de recuperación | **Reemplaza siempre** al parcial o al final que más convenga |

Calcularlo a mano es tedioso, y un error de cálculo significa reprobar. Esta app automatiza el cálculo tomando las reglas directamente del sistema, sin depender de que te acuerdes de ellas.

---

## ✨ Funcionalidades

- **17 cursos** configurados en un archivo de datos externo.
- Los **4 modelos de ponderación** de la facultad (B, D, F, G).
- Manejo de `NSP` y `0A`.
- **Desglose del cálculo**: cada componente, su nota, su peso y su aporte, con el total.
- **Explicación del sustitutorio**: a cuál examen reemplaza y por qué.
- **Simulación por matriz**: recorre todas las combinaciones posibles de las evaluaciones pendientes y te dice la **nota mínima** que necesitas para alcanzar el objetivo.

---

## 🚀 Instalación

```bash
git clone https://github.com/ZhenRB/SimuladorNotasCCAT.git
cd SimuladorNotasCCAT
pip install streamlit
```

## ▶️ Uso

```bash
streamlit run View.py
```

La app se abre en `http://localhost:8501`.

> ⚠️ **Ojo:** el comando correcto es `streamlit run View.py`.
> Si ejecutas `python View.py` no verás nada: la app queda en modo "bare" y el script muere sin interfaz.

---

## 🧮 ¿Cómo funciona la simulación?

Esta es la parte más interesante del proyecto.

El objetivo es responder: *«si todavía me falta esto, ¿qué nota necesito?»*

### El enfoque por matriz

La idea es tratar el problema como una **matriz de combinaciones**:

- **M** = cantidad de evaluaciones pendientes (las que aún no rindes)
- **N** = 21 valores posibles por evaluación (la escala de 0 a 20)

Se recorren las **N^M** combinaciones, se calcula el promedio final de cada una, y se conservan las que alcanzan el objetivo:

| Pendientes | Combinaciones | Tiempo |
|:-----------|:--------------|:-------|
| 1 | 21 | instantáneo |
| 2 | 441 | instantáneo |
| 3 | 9 261 | ~0.03 s |
| 4 | 194 481 | ~0.7 s |
| 5 | 4 084 101 | ⚠️ demasiado |

### El desempate: "menos desviadas"

Un detalle importante. Hay muchas combinaciones que llegan al mismo objetivo, así que el orden importa. Las filas se ordenan por:

1. **Menor suma de notas** — el menor esfuerzo total posible.
2. **Menor desviación** — a igual suma, se prioriza el reparto **más parejo** entre las evaluaciones.

Este segundo criterio importa en la práctica. Con parcial y final pendientes, las combinaciones `(0, 11)` y `(6, 8)` suman ambas 11, pero la segunda está mucho mejor repartida. La app elige la segunda.

### El límite de la fuerza bruta

Con 5 o más pendientes la matriz crece demasiado (21⁵ = 4 millones, 21⁶ = 85 millones). En ese caso la app detecta el tamaño, avisa y cambia a un método directo que recorre las **sumas en orden creciente**: prueba `(0,0,0)`, luego `(1,0,0)`, `(0,1,0)`… y se detiene en la primera que llega al objetivo.

Como las sumas se prueban de menor a mayor, la primera solución **es** por construcción la de menor esfuerzo. Los dos métodos coinciden: se verificó sobre 425 casos aleatorios y nunca hubo diferencia de esfuerzo entre ambos.

---

## 📁 Estructura

```
SimuladorNotasCCAT/
├── View.py            # Interfaz (Streamlit)
├── Function.py        # Lógica de cálculo y simulación
├── datos_cursos.json  # Reglas de evaluación de los 17 cursos
└── .gitignore
```

La separación es deliberada: `View.py` no contiene lógica de negocio, todo el cálculo vive en `Function.py`. Eso permite probarlo sin levantar la app.

<details>
<summary><b>Funciones de <code>Function.py</code></b></summary>

**Núcleo de cálculo**
- `convertirANumero(valor)` — Maneja `NSP` y `0A`
- `promedioPracticas(...)` — Promedio de continuas, aplicando qué notas cuentan y la regla de las mejores N
- `promedioFinalCurso(...)` — Ponderación final y resolución del sustitutorio

**Soporte de la simulación**
- `notaExamen(valor)` — Formatea una nota para mostrar
- `nombreEvaluacion(tipo, indice)` — Etiqueta legible de una evaluación
- `matrizSimulacion(...)` — Recorre la matriz de combinaciones
- `simularNotaMinima(...)` — Método directo por sumas crecientes
- `_composiciones(...)` — Generador de combinaciones para el método directo

**Resolución**
- `resolverSustitutorio(...)` — Determina qué nota de examen se usó realmente

</details>

---

## 📐 Reglas de evaluación

`datos_cursos.json` define las reglas de cada curso:

```json
"ALGORITMIA Y ESTRUCTURA DE DATOS": {
    "NombreCurso": "ALGORITMIA Y ESTRUCTURA DE DATOS",
    "TipoCalificacion": "F",
    "Practicas": 4,
    "Laboratorios": 0,
    "ExamenParcial": 1,
    "ExamenFinal": 1,
    "ExamenSustitutorio": 1,
    "Monografias": 0
}
```

`TipoCalificacion` define las ponderaciones:

| Tipo | Prácticas | Parcial | Final |
|:----:|:---------:|:-------:|:-----:|
| `B`  | 0         | 1       | 2     |
| `D`  | 1         | 0       | 0     |
| `F`  | 1         | 1       | 2     |
| `G`  | 1         | 1       | 1     |

> Para agregar un curso basta con añadir una entrada al JSON. No hay que tocar código.

---

## 🛠️ Stack

- **Python** — lógica de cálculo
- **Streamlit** — interfaz web
- **JSON** — configuración de los cursos
- Sin dependencias más allá de Streamlit

---

## 👤 Autor

**Rolando Sotomayor Baca**

Estudiante de Ingeniería de Sistemas (FIIS-UNI). Proyecto desarrollado para el área de
IDI del Centro Cultural Avanzada Tecnológica (CCAT).

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?logo=linkedin&logoColor=white)](https://linkedin.com/in/rolando-sotomayor-baca)

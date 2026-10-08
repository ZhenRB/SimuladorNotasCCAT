"""
Simulador de Notas CCAT
Interfaz de la aplicación (Streamlit).

Ejecutar con:  streamlit run View.py
"""

import json
from pathlib import Path

import streamlit as st

from Function import (
    cantidadUsada,
    convertirANumero,
    datosCursos,
    mapaSis,
    matrizSimulacion,
    nombreEvaluacion,
    notaExamen,
    promedioFinalCurso,
    promedioPracticas,
    resolverSustitutorio,
    simularNotaMinima,
)

# ---------------------------------------------------------------- Configuración

st.set_page_config(page_title="Simulador de Notas", page_icon="📊", layout="wide")

NOTA_MINIMA_APROBACION = 10
ESCALA = [str(i) for i in range(0, 21)]
VALORES_ESPECIALES = {
    "NSP": "No se presentó (se reemplaza por 0)",
    "0A": "Ausente (no cuenta para el promedio)",
}
OPCIONES = ESCALA + list(VALORES_ESPECIALES)

# ------------------------------------------------------------------ Encabezado

st.title("Simulador de Notas")
st.caption(
    "Calcula el promedio final de un curso aplicando las reglas de evaluación reales "
    "de la Facultad de Ingeniería de Sistemas (FIIS-UNI)."
)

# ------------------------------------------------------------ Selección curso

nombre_a_codigo = {c["NombreCurso"]: cod for cod, c in datosCursos.items()}

col_curso, col_vacio = st.columns([2, 1])
with col_curso:
    nombre_curso = st.selectbox("Curso", sorted(nombre_a_codigo))

codigo = nombre_a_codigo[nombre_curso]
curso = datosCursos[codigo]

# ------------------------------------------------------- Ficha del curso

n_practicas = curso.get("Practicas", 0)
n_laboratorios = curso.get("Laboratorios", 0)
n_monografias = curso.get("Monografias", 0)
tiene_parcial = curso.get("ExamenParcial", 0) == 1
tiene_final = curso.get("ExamenFinal", 0) == 1
tiene_sustitutorio = curso.get("ExamenSustitutorio", 0) == 1

peso_practicas, peso_parcial, peso_final = mapaSis[curso["TipoCalificacion"]]

with st.container(border=True):
    st.markdown("**Reglas de evaluación**")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tipo", curso["TipoCalificacion"])
    c2.metric("Prácticas", n_practicas or "—")
    c3.metric("Laboratorios", n_laboratorios or "—")
    c4.metric("Monografías", n_monografias or "—")

    st.caption(
        f"Ponderación: continuas ×{peso_practicas} · "
        f"parcial ×{peso_parcial} · final ×{peso_final}"
    )

    # Cuántas notas se toman en cuenta realmente
    detalle = []
    for etiqueta, total in (
        ("prácticas", n_practicas),
        ("laboratorios", n_laboratorios),
    ):
        if total:
            detalle.append(
                f"de las {total} {etiqueta} solo se promedian las "
                f"{cantidadUsada[total]} mejores"
            )
    if detalle:
        st.caption("Nota: " + " · ".join(detalle) + ".")

# --------------------------------------------------------- Captura de notas

st.subheader("Ingresa tus notas")

OPCIONES_SIN_CERO = [o for o in OPCIONES if o not in ("0",)]


def pedir_notas(etiqueta, cantidad, con_ausencia=True):
    """Muestra los campos de una evaluación y devuelve las notas ingresadas."""
    if not cantidad:
        return []

    opciones = OPCIONES_SIN_CERO if con_ausencia else ESCALA
    st.markdown(f"**{etiqueta}** ({cantidad})")

    columnas = st.columns(min(4, cantidad))
    notas = []
    for i in range(cantidad):
        with columnas[i % len(columnas)]:
            notas.append(
                st.selectbox(
                    f"{etiqueta} {i + 1}",
                    opciones,
                    index=OPCIONES_SIN_CERO.index("10") if "10" in OPCIONES_SIN_CERO else 0,
                    key=f"{etiqueta}_{i}_{codigo}",
                    label_visibility="collapsed",
                )
            )
    return notas


practicas = pedir_notas("Práctica", n_practicas)
laboratorios = pedir_notas("Laboratorio", n_laboratorios)
monografias = pedir_notas("Monografía", n_monografias)

examen_parcial = examen_final = examen_sustitutorio = 0

if tiene_parcial or tiene_final or tiene_sustitutorio:
    st.markdown("**Exámenes**")
    c1, c2, c3 = st.columns(3)
    with c1:
        examen_parcial = (
            st.selectbox("Parcial", OPCIONES, index=10, key=f"parcial_{codigo}")
            if tiene_parcial
            else "NSP"
        )
    with c2:
        examen_final = (
            st.selectbox("Final", OPCIONES, index=10, key=f"final_{codigo}")
            if tiene_final
            else "NSP"
        )
    with c3:
        examen_sustitutorio = (
            st.selectbox("Sustitutorio", OPCIONES, index=10, key=f"susti_{codigo}")
            if tiene_sustitutorio
            else "NSP"
        )

st.divider()

# ------------------------------------------------------------------ Resultado

if st.button("Calcular promedio", type="primary", width="stretch"):
    promedio = promedioFinalCurso(
        practicas,
        laboratorios,
        monografias,
        codigo,
        examen_parcial,
        examen_final,
        examen_sustitutorio,
    )

    # Qué nota de examen se usó realmente tras aplicar el sustitutorio
    parcial_efectivo, final_efectivo, sustitucion = resolverSustitutorio(
        practicas,
        laboratorios,
        monografias,
        codigo,
        examen_parcial,
        examen_final,
        examen_sustitutorio,
    )

    izquierda, derecha = st.columns([1, 2])

    with izquierda:
        st.metric("Promedio final", f"{promedio:.2f}")
        if promedio >= NOTA_MINIMA_APROBACION:
            st.success("Aprobaste el curso.")
        else:
            st.error(
                f"Te faltan **{NOTA_MINIMA_APROBACION - promedio:.2f}** puntos "
                "para aprobar."
            )

    with derecha:
        promedio_continuas = promedioPracticas(
            practicas, laboratorios, monografias, codigo
        )
        st.markdown("**Cómo se calculó**")

        # Aviso del examen sustitutorio, si se usó
        nota_sustitutorio = convertirANumero(examen_sustitutorio)
        if sustitucion and nota_sustitutorio > 0:
            no_rendido = -2 in (convertirANumero(examen_parcial), convertirANumero(examen_final))
            if no_rendido:
                faltante = "parcial" if convertirANumero(examen_parcial) == -2 else "final"
                st.info(
                    f"No pudiste rendir el **examen {faltante}** (0A), así que el "
                    f"**sustitutorio ({notaExamen(nota_sustitutorio)})** ocupó el lugar "
                    f"del **examen {sustitucion}**."
                )
            else:
                st.info(
                    f"El **examen sustitutorio ({notaExamen(nota_sustitutorio)})** "
                    f"reemplazó al **examen {sustitucion}**, porque es el que más "
                    "conviene para el promedio. El otro examen se conserva."
                )
        elif nota_sustitutorio == -2:
            st.warning("Te presentaste al sustitutorio pero figuras como **ausente (0A)**.")
        elif nota_sustitutorio == 0:
            st.caption("No te presentaste al examen sustitutorio.")

        filas = [
            {
                "Componente": "Prácticas / labs / monografías",
                "Nota": f"{promedio_continuas:.2f}",
                "Peso": str(peso_practicas),
                "Aporte": f"{promedio_continuas * peso_practicas:.2f}",
            }
        ]
        if peso_parcial:
            filas.append(
                {
                    "Componente": "Examen parcial",
                    "Nota": notaExamen(parcial_efectivo),
                    "Peso": str(peso_parcial),
                    "Aporte": f"{parcial_efectivo * peso_parcial:.2f}",
                }
            )
        if peso_final:
            filas.append(
                {
                    "Componente": "Examen final",
                    "Nota": notaExamen(final_efectivo),
                    "Peso": str(peso_final),
                    "Aporte": f"{final_efectivo * peso_final:.2f}",
                }
            )

        peso_total = peso_practicas + peso_parcial + peso_final
        filas.append(
            {
                "Componente": "Total",
                "Nota": "",
                "Peso": str(peso_total),
                "Aporte": f"{promedio:.2f}",
            }
        )

        st.dataframe(
            filas,
            hide_index=True,
            width="stretch",
            column_config={
                "Componente": st.column_config.TextColumn("Componente", width="medium"),
                "Nota": st.column_config.TextColumn("Nota", width="small"),
                "Peso": st.column_config.TextColumn("Peso", width="small"),
                "Aporte": st.column_config.TextColumn("Aporte", width="small"),
            },
        )

with st.expander("Referencias de la escala"):
    st.markdown(
        "- **NSP** — No se presentó: equivale a 0.\n"
        "- **0A** — Ausente: no se promedia, pero tampoco se elimina la nota.\n"
        f"- La nota mínima para aprobar es **{NOTA_MINIMA_APROBACION}**."
    )

# ------------------------------------------------------- Simulación: ¿qué falta?

st.divider()
st.subheader("¿Qué nota necesitas?")

# Se listan todas las evaluaciones del curso; el usuario marca cuáles aún no ha rindido.
opciones_pendientes = []
for tipo, total in (
    ("Practicas", n_practicas),
    ("Laboratorios", n_laboratorios),
    ("Monografias", n_monografias),
):
    for indice in range(total):
        opciones_pendientes.append((f"{tipo}:{indice}", nombreEvaluacion(tipo, indice)))
if tiene_parcial:
    opciones_pendientes.append(("ExamenParcial:0", "Examen parcial"))
if tiene_final:
    opciones_pendientes.append(("ExamenFinal:0", "Examen final"))

etiquetas = dict(opciones_pendientes)

c1, c2 = st.columns(2)
with c1:
    objetivo = st.number_input(
        "Nota que quieres alcanzar",
        min_value=0,
        max_value=20,
        value=NOTA_MINIMA_APROBACION,
        step=1,
    )
with c2:
    pendientes_elegidas = st.multiselect(
        "Evaluaciones que aún no rindes",
        [clave for clave, _ in opciones_pendientes],
        format_func=lambda clave: etiquetas[clave],
        max_selections=5,
        key=f"pendientes_{codigo}",
    )

if not pendientes_elegidas:
    st.info("Marca al menos una evaluación pendiente para simular.")
    st.caption(
        "Se recorre la matriz de combinaciones posibles (M pendientes × N = 21 valores) "
        "y se muestran las que llegan al objetivo, de menor esfuerzo a mayor."
    )
else:
    pendientes = []
    for clave in pendientes_elegidas:
        tipo, indice = clave.split(":")
        pendientes.append((tipo, int(indice)))

    etiquetas_orden = [nombreEvaluacion(t, i) for t, i in pendientes]
    matriz = matrizSimulacion(
        practicas,
        laboratorios,
        monografias,
        codigo,
        examen_parcial,
        examen_final,
        examen_sustitutorio,
        pendientes,
        objetivo=objetivo,
    )

    if matriz["demasiado"]:
        # Con 5 o más pendientes la matriz es demasiado grande: se usa el método directo
        st.warning(
            f"Con {len(pendientes)} pendientes habría "
            f"{matriz['combinaciones']:,} combinaciones, demasiado para recorrerlas todas. "
            "Se calcula solo la combinación mínima."
        )
        resultado = simularNotaMinima(
            practicas, laboratorios, monografias, codigo,
            examen_parcial, examen_final, examen_sustitutorio,
            pendientes, objetivo=objetivo,
        )
        if resultado is None:
            st.error(f"No es posible alcanzar {objetivo} en este curso.")
        else:
            solucion, promedio = resultado
            st.success(
                f"Con estas notas llegarías a **{promedio:.2f}**: "
                + " · ".join(f"{e} {n}" for e, n in solucion)
            )

    elif not matriz["alcanzable"]:
        st.error(
            f"No es posible alcanzar {objetivo} en {curso['NombreCurso']}, "
            "aunque saques 20 en todo lo pendiente."
        )
        st.caption(
            f"Se evaluaron las {matriz['combinaciones']:,} combinaciones posibles "
            "y ninguna llega al objetivo."
        )

    else:
        mejor = matriz["mejor"]
        notas_recomendadas = " · ".join(
            f"**{etiquetas_orden[i]}: {mejor[et]}**" for i, et in enumerate(etiquetas_orden)
        )
        st.success(
            f"Combinación de menor esfuerzo para llegar a {objetivo} "
            f"→ **{mejor['_promedio']:.2f}** de promedio."
        )
        st.markdown(notas_recomendadas)

        st.caption(
            f"Se recorrieron las **{matriz['combinaciones']:,}** combinaciones de la matriz "
            f"({len(pendientes)} pendientes × 21 valores posibles); "
            f"**{len(matriz['filas']):,}** alcanzan el objetivo."
            + (" Se muestran las de menor esfuerzo." if matriz["truncado"] else "")
        )

        filas_tabla = [
            {et: mejor[et] for et in etiquetas_orden}
            | {"Promedio": round(mejor["_promedio"], 2)}
        ]
        st.dataframe(filas_tabla, hide_index=True, width="stretch")

        with st.expander(f"Ver las {len(matriz['filas'])} combinaciones que alcanzan el objetivo"):
            st.dataframe(
                [
                    {et: fila[et] for et in etiquetas_orden}
                    | {"Promedio": round(fila["_promedio"], 2),
                       "Suma de notas": fila["_esfuerzo"]}
                    for fila in matriz["filas"][:300]
                ],
                hide_index=True,
                width="stretch",
            )
            st.caption(
                "Ordenadas de menor a mayor suma de notas; a igual suma, "
                "se prioriza el reparto más parejo entre las evaluaciones."
            )

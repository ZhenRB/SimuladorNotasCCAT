import json
from Function import promedioPracticas, promedioFinalCurso, convertir_a_numero
import streamlit as st

# Cargar datos desde el archivo JSON
with open('datos_cursos.json', 'r') as file:
    datosCursos = json.load(file)

# Número de prácticas que se usarán
CantidadUsada = [0, 0, 0, 0, 3, 4, 5, 5, 6, 7, 7, 8, 8]

# PesoPrácticas, PesoParcial, PesoFinal
mapa_sis = {
    'B': (0, 1, 2),
    'D': (1, 0, 0),
    'F': (1, 1, 2),
    'G': (1, 1, 1)
}


from PIL import Image
# Cargar imagen local
image = Image.open("/Users/jmon2103/Desktop/logo_cmichiPNG.png")

# Añadir estilos CSS para posicionar la imagen en la esquina superior izquierda
st.markdown("""
    <style>
    .reportview-container {
        position: relative;
    }
    .header-img {
        position: fixed;
        top: 50px;
        left: 50px;
        width: 60px;
        height: auto;
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)

# Mostrar la imagen en la interfaz en una pequeña esquina
st.image(image, use_column_width=False, caption=None, output_format="PNG", width=100)

# Resto del contenido de la aplicación
st.title("Simulador de Notas")
st.write("Esta aplicación te permite simular tus notas.")


# Título
st.markdown("<h1 style='text-align: center; color: #1694f7;'>Simulador de Notas </h1>", unsafe_allow_html=True)

# Descripción de la aplicación
st.markdown("<p style='text-align: center;'>Esta aplicación te permite simular tus notas y calcular tu promedio final para verificar si pasas el curso.</p>", unsafe_allow_html=True)

# Crear un diccionario que mapea nombres de cursos a códigos
codigo_a_nombre = {curso["NombreCurso"]: codigo for codigo, curso in datosCursos.items()}
nombre_a_codigo = {nombre: codigo for nombre, codigo in codigo_a_nombre.items()}

# Extraer los nombres de los cursos
nombresCursos = list(codigo_a_nombre.keys())

# Crear el selectbox para seleccionar el nombre del curso
st.markdown("<h4 style='color: #2196F3;'>1. Selecciona un curso:</h4>", unsafe_allow_html=True)
nombreCursoSeleccionado = st.selectbox(
    "Selecciona un curso:",
    nombresCursos
)

# Obtener el código del curso basado en el nombre seleccionado
codigoCursoSeleccionado = nombre_a_codigo[nombreCursoSeleccionado]

# Obtener el curso seleccionado usando el código
curso_seleccionado = datosCursos[codigoCursoSeleccionado]

# Mostrar campos para ingresar datos solo si están en el JSON
st.markdown("<h4 style='color: #2196F3;'>2. Ingrese las notas para el curso seleccionado:</h4>", unsafe_allow_html=True)

def mostrar_campos(campo, cantidad):
    """Muestra una serie de campos de entrada selectbox con opciones numéricas y especiales."""
    if cantidad <= 0:
        return []
    
    num_columnas = min(3, max(1, cantidad))  # Asegurarse de que al menos 1 columna se use
    columnas = st.columns(num_columnas)
    entradas = []
    
    opciones = [str(i) for i in range(1, 21)] + ["NSP", "0A"]  # Opciones del 1 al 20, NSP y 0A
    
    for i in range(cantidad):
        col = columnas[i % len(columnas)]  # Selecciona la columna correspondiente
        with col:
            entradas.append(st.selectbox(
                f"{campo} {i+1}",
                options=opciones,
                index=9,  # Default "10"
                help=f"Ingrese la nota para {campo} {i+1} (1-20, NSP, 0A)"
            ))
    return entradas

# Crear campos basados en los valores del JSON
datos_ingresados = {}

if "Practicas" in curso_seleccionado:
    cantidad = curso_seleccionado["Practicas"]
    if cantidad > 0:
        st.write(f"Ingrese las notas para {cantidad} prácticas:")
    datos_ingresados["Practicas"] = mostrar_campos("Practica", cantidad)

if "Laboratorios" in curso_seleccionado:
    cantidad = curso_seleccionado["Laboratorios"]
    if cantidad > 0:
        st.write(f"Ingrese las notas para {cantidad} laboratorios:")
    datos_ingresados["Laboratorios"] = mostrar_campos("Laboratorio", cantidad)

if "Monografias" in curso_seleccionado:
    cantidad = curso_seleccionado["Monografias"]
    if cantidad > 0:
        st.write(f"Ingrese las notas para {cantidad} monografías:")
    datos_ingresados["Monografias"] = mostrar_campos("Monografía", cantidad)

# Convertir las entradas a números
practicas = [convertir_a_numero(n) for n in datos_ingresados.get("Practicas", [])]
laboratorios = [convertir_a_numero(n) for n in datos_ingresados.get("Laboratorios", [])]
monografias = [convertir_a_numero(n) for n in datos_ingresados.get("Monografias", [])]

# Mostrar una sola vez los campos para exámenes
st.markdown("<h4 style='color: #2196F3;'>3. Ingrese las notas de los exámenes:</h4>", unsafe_allow_html=True)
examen_parcial = convertir_a_numero(st.selectbox("Examen Parcial", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
examen_final = convertir_a_numero(st.selectbox("Examen Final", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
examen_sustitutorio = convertir_a_numero(st.selectbox("Examen Sustitutorio", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))

# Botón para calcular
st.markdown("<h4 style='color: #2196F3;'>4. Calcula tu promedio final:</h4>", unsafe_allow_html=True)
if st.button("Calcular Promedio"):
    promedio_final = promedioFinalCurso(practicas, laboratorios, monografias, codigoCursoSeleccionado, examen_parcial, examen_final, examen_sustitutorio)
    if promedio_final>=10:
        st.markdown(f"<h2 style='color: #4CAF50;'>Tu promedio final es: {promedio_final:.2f} 🎉</h2>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h2 style='color: #f32929;'>Tu promedio final es:  {promedio_final:.2f} ☠️</h2>", unsafe_allow_html=True)
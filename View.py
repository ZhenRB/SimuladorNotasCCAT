import json
<<<<<<< HEAD
from Function import promedioPracticas, promedioFinalCurso, convertirANumero
=======
from Function import promedioPracticas, promedioFinalCurso, convertir_a_numero
from PIL import Image
>>>>>>> 0f595f6a1903d895586afe2c3b8fda52d1f94f3e
import streamlit as st

# Cargar datos desde el archivo JSON
with open('datos_cursos.json', 'r') as file:
    datosCursos = json.load(file)

# Número de prácticas que se usarán
CantidadUsada = [0, 1, 2, 3, 3, 4, 5, 5, 6, 7, 7, 8, 8]

#* PesoPracticas, PesoParcial, PesoFinal
mapa_sis = {
    'B' : (0,         1,         2),
    'D' : (1,         0,         0),
    'F' : (1,         1,         2), 
    'G' : (1,         1,         1)
}


# Logo en la esquina
st.markdown("""<style>
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

# Mostrar logo en la interfaz 
st.image("Images/LogoCmichi.png", use_column_width=False, caption=None, output_format="PNG", width=100)



# Título
st.markdown("""<h1 style='text-align: center; color: #1694f7; font-family: "Times New Roman", Times, serif;'>Simulador de Notas</h1>""", unsafe_allow_html=True)

# Descripción de la aplicación
st.markdown("""<p style='text-align: center; font-family: "Times New Roman", Times, serif; '>Esta aplicación te permite simular tus notas y calcular tu promedio final para verificar si pasas el curso.</p>""", unsafe_allow_html=True)


# Crear un diccionario que mapea nombres de cursos a códigos
codigo_a_nombre = {curso["NombreCurso"]: codigo for codigo, curso in datosCursos.items()}
nombre_a_codigo = {nombre: codigo for nombre, codigo in codigo_a_nombre.items()}

# Extraer los nombres de los cursos
nombresCursos = list(codigo_a_nombre.keys())

# Crear el selectbox para seleccionar el nombre del curso
st.markdown("""<h4 style='color: #2196F3; font-family: "Times New Roman", Times, serif;'>1. Selecciona un curso:</h4>""", unsafe_allow_html=True)
nombreCursoSeleccionado = st.selectbox(
    "Selecciona un curso:",
    nombresCursos
)

# Obtener el código del curso basado en el nombre seleccionado
codigoCursoSeleccionado = nombre_a_codigo[nombreCursoSeleccionado]

# Obtener el curso seleccionado usando el código
curso_seleccionado = datosCursos[codigoCursoSeleccionado]

if ("Imagen" in curso_seleccionado and curso_seleccionado["Imagen"] != 0):
    sticker_prof = curso_seleccionado["Imagen"]
    if sticker_prof: 
        st.image(sticker_prof, width=150)
else:
    st.write(" ")

# Mostrar campos para ingresar datos solo si están en el JSON
st.markdown("""<h4 style='color: #2196F3; font-family: "Times New Roman", Times, serif;'>2. Ingrese las notas para el curso seleccionado:</h4>""", unsafe_allow_html=True)

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
        st.image("Images/informe_lab.jpg", width=150)    


if "Monografias" in curso_seleccionado:
    cantidad = curso_seleccionado["Monografias"]
    if cantidad > 0:
        st.write(f"Ingrese las notas para {cantidad} monografías:")
    datos_ingresados["Monografias"] = mostrar_campos("Monografía", cantidad)


# Convertir las entradas a números
<<<<<<< HEAD
practicas = [convertirANumero(n) for n in datos_ingresados.get("Practicas", [])]
laboratorios = [convertirANumero(n) for n in datos_ingresados.get("Laboratorios", [])]
monografias = [convertirANumero(n) for n in datos_ingresados.get("Monografias", [])]
examen_parcial = convertirANumero(st.selectbox("Examen Parcial", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
examen_final = convertirANumero(st.selectbox("Examen Final", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
examen_sustitutorio = convertirANumero(st.selectbox("Examen Sustitutorio", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
=======
practicas = [convertir_a_numero(n) for n in datos_ingresados.get("Practicas", [])]
laboratorios = [convertir_a_numero(n) for n in datos_ingresados.get("Laboratorios", [])]
monografias = [convertir_a_numero(n) for n in datos_ingresados.get("Monografias", [])]
>>>>>>> 0f595f6a1903d895586afe2c3b8fda52d1f94f3e

examen_parcial = convertir_a_numero(datos_ingresados.get("ExamenParcial", [])[0] if datos_ingresados.get("ExamenParcial", []) else 0)
examen_final = convertir_a_numero(datos_ingresados.get("ExamenFinal", [])[0] if datos_ingresados.get("ExamenFinal", []) else 0)
examen_sustitutorio = convertir_a_numero(datos_ingresados.get("ExamenSustitutorio", [])[0] if datos_ingresados.get("ExamenSustitutorio", []) else 0)

# examen_parcial = convertir_a_numero(st.selectbox("Examen Parcial", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
# examen_final = convertir_a_numero(st.selectbox("Examen Final", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))
# examen_sustitutorio = convertir_a_numero(st.selectbox("Examen Sustitutorio", options=[str(i) for i in range(1, 21)] + ["NSP", "0A"], index=9))

# here's my idea (by Rolly)
# PARA 0A:
# contar la cantida de 0A o pcs que no se eliminan
# dividir las listas, hacer sort, luego merge y finalmente usar las necesarias
# una nueva funcion puede ser creada...
# PARA SIMULACION
# 1  : mostrar la nota necesaria minima cuando se falta una nota, de manera inmediata
# averiguar como se hace eso :v
# 2  : primero pasar mis pcs xd, y vender las polladas XD
#      es más complicado cuando se combina con susti y finales o parciales
#      simular por fuerza bruta como primera version
#      mostrar 20 pares de resultados?
#      creo que sirve sobre todo cuanto falta final y susti (porque jalaste parcial xd)
# 3  : no quiero
#                               MORE UPDATES TOMORROW

# Botón para calcular
st.markdown("""<h4 style='color: #2196F3; font-family: "Times New Roman", Times, serif;'>4. Calcula tu promedio final:</h4>""", unsafe_allow_html=True)
    
if st.button("Calcular Promedio"):
    promedio_final = promedioFinalCurso(practicas, laboratorios, monografias, codigoCursoSeleccionado, examen_parcial, examen_final, examen_sustitutorio)
<<<<<<< HEAD
    st.write(f"El promedio final es: {promedio_final:.2f}")
=======
    if promedio_final>=10:
        st.markdown(f"""<h2 style='color: #4CAF50; font-family: "Times New Roman", Times, serif;'>Tu promedio final es: {promedio_final:.2f} 🎉</h2>""", unsafe_allow_html=True)
        # Agregar imagen aprobado en base al json
        if("Aprobado" in curso_seleccionado and curso_seleccionado["Aprobado"] != 0):
            aprobado = curso_seleccionado["Aprobado"]
            if aprobado: 
                st.image(aprobado, width=200)
        else:
            st.image("Images/patito_aprobado_default.jpg", width=200)

    else:
        st.markdown(f"""<h2 style='color: #f32929; font-family: "Times New Roman", Times, serif;'>Tu promedio final es: {promedio_final:.2f} ☠️</h2>""",unsafe_allow_html=True)
        # Agregar imagen jalado en base al json
        if("Jalado" in curso_seleccionado and curso_seleccionado["Jalado"] != 0):
            jalado = curso_seleccionado["Jalado"]
            if jalado: 
                st.image(jalado, width=200)
        else:
            st.image("Images/gato_jalado_default.jpg", width=200)




>>>>>>> 0f595f6a1903d895586afe2c3b8fda52d1f94f3e


import json

#* Extrae los datos del json para usarlos
with open('datos_cursos.json', 'r') as file:
    datosCursos = json.load(file)

#* N° de Practicas que se usaran respecto al total que haya
#* PCs:          0  1  2  3  4  5  6  7  8  9  10 11 12 
cantidadUsada = [0, 0, 0, 0, 3, 4, 5, 5, 6, 7, 7, 8, 8]

#* PesoPracticas, PesoParcial, PesoFinal
mapaSis = {
    'B' : (0, 1, 2),
    'D' : (1, 0, 0),
    'F' : (1, 1, 2), 
    'G' : (1, 1, 1)
}

def convertirANumero(valor):
    """Convierte una cadena a número, manejando valores especiales."""
    if valor == "NSP":
        return 0
    if valor == "0A":
        return -2
    try:
        return int(valor)
    except ValueError:
        return 0

def promedioPracticas(practicas, laboratorios, monografias, codigoCurso):
    # Convierte valores a números manejando valores especiales
    practicas = [convertirANumero(p) for p in practicas]
    laboratorios = [convertirANumero(l) for l in laboratorios]
    monografias = [convertirANumero(m) for m in monografias]

    # Cuenta las notas "0A" que se interpretan como ausencias
    ceroAPracticas = practicas.count(-2)
    ceroALaboratorios = laboratorios.count(-2)
    ceroAMonografias = monografias.count(-2)

    # Define cuántas prácticas, laboratorios y monografías se usarán
    practicasUsadas = cantidadUsada[datosCursos[codigoCurso].get("Practicas")]
    laboratoriosUsadas = cantidadUsada[datosCursos[codigoCurso].get("Laboratorios")]
    monografiasUsadas = datosCursos[codigoCurso]["Monografias"]

    # Ajusta el número de elementos contables si hay ausencias
    if ceroAPracticas > 0:
        practicasUsadas -= 1 * ceroAPracticas
    if ceroALaboratorios > 0:
        laboratoriosUsadas -= 1 * ceroALaboratorios
    if ceroAMonografias > 0:
        monografiasUsadas -= 1 * ceroAMonografias

    # Selecciona las mejores notas contables
    practicasContables = sorted(practicas)[-practicasUsadas:] + [0] * ceroAPracticas
    laboratoriosContables = sorted(laboratorios)[-laboratoriosUsadas:] + [0] * ceroALaboratorios
    monografiasContables = monografias

    # Ajustes especiales para ciertos cursos
    if codigoCurso in ["SI101", "SW101"]:
        practicasContables = sorted(practicas[:3]) + practicas[-1:] 
        practicasContables = practicasContables[-practicasUsadas:] + [0] * ceroAPracticas

    # Calcula el promedio considerando prácticas, laboratorios y monografías
    sumaTotal = sum(practicasContables) + sum(laboratoriosContables) + sum(monografiasContables)
    numeroTotal = len(practicasContables) + len(laboratoriosContables) + len(monografiasContables)

    return sumaTotal / numeroTotal

def promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenParcial, examenFinal, examenSustitutorio):
    promedioDePracticas = promedioPracticas(practicas, laboratorios, monografias, codigoCurso)
    tipoCalificacion = datosCursos[codigoCurso].get("TipoCalificacion")
    pesoPracticas, pesoParcial, pesoFinal = mapaSis[tipoCalificacion]
    pesoTotal = pesoPracticas + pesoParcial + pesoFinal

    # Validar la mejor nota cuando existe sustitutorio
    if examenSustitutorio > 0:
        promedioEpEs = promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenSustitutorio, examenFinal, 0)
        promedioEfEs = promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenParcial, examenSustitutorio, 0)
        if promedioEpEs > promedioEfEs:
            examenParcial = examenSustitutorio
        else:
            examenFinal = examenSustitutorio

    # Calcula el promedio final ponderado
    promedioFinal = (promedioDePracticas * pesoPracticas + examenParcial * pesoParcial + examenFinal * pesoFinal) / pesoTotal
    
    return promedioFinal

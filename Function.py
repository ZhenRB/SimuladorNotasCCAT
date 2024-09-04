import json

with open('datos_cursos.json', 'r') as file:
    datosCursos = json.load(file)

#* N° de Practicas que se usaran respecto al total que haya
#* PCs:          0  1  2  3  4  5  6  7  8  9  10 11 12 
CantidadUsada = [0, 0, 0, 0, 3, 4, 5, 5, 6, 7, 7, 8, 8]

#* PesoPracticas, PesoParcial, PesoFinal
mapa_sis = {
    'B' : (0,         1,         2),
    'D' : (1,         0,         0),
    'F' : (1,         1,         2), 
    'G' : (1,         1,         1)
}

def convertir_a_numero(valor):
    """Convierte una cadena a número, manejando valores especiales."""
    if valor == "NSP" or valor == "0A":
        return 0
    try:
        return int(valor)
    except ValueError:
        return 0

def promedioPracticas(practicas, laboratorios, monografias, codigoCurso):
    practicas = [convertir_a_numero(p) for p in practicas]
    laboratorios = [convertir_a_numero(l) for l in laboratorios]
    monografias = [convertir_a_numero(m) for m in monografias]
    
    practicasUsadas = CantidadUsada[datosCursos[codigoCurso].get("Practicas")]
    laboratoriosUsadas = CantidadUsada[datosCursos[codigoCurso].get("Laboratorios")]
    monografiasUsadas = datosCursos[codigoCurso]["Monografias"]

    practicasContables = sorted(practicas)[-practicasUsadas:]
    laboratoriosContables = sorted(laboratorios)[-laboratoriosUsadas:]
    monografiasContables = monografias

    if codigoCurso in ["SI101", "SW101"]:
        practicasContables = sorted(practicas[:practicasUsadas]) + practicas[-1:]
        practicasContables = practicasContables[-practicasUsadas:]

    sumaTotalDePracticas = sum(practicasContables) + sum(laboratoriosContables) + sum(monografiasContables)
    numeroTotalDePracticas = len(practicasContables) + len(laboratoriosContables) + len(monografiasContables)

    return sumaTotalDePracticas / numeroTotalDePracticas

def promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenParcial, examenFinal, examenSustitutorio):
    promedioDePracticas = promedioPracticas(practicas, laboratorios, monografias, codigoCurso)
    tipoCalificacion = datosCursos[codigoCurso].get("TipoCalificacion")
    pesoPracticas, pesoParcial, pesoFinal = mapa_sis[tipoCalificacion]
    pesoTotal = pesoPracticas + pesoParcial + pesoFinal

    # Validar Nota cuando existe sustitutorio
    if examenSustitutorio > 0:
        promedio_ep_es = promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenSustitutorio, examenFinal, 0)
        promedio_ef_es = promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenParcial, examenSustitutorio, 0)
        if promedio_ep_es > promedio_ef_es:
            examenParcial = examenSustitutorio
        else:
            examenFinal = examenSustitutorio

    promedioFinal = (promedioDePracticas * pesoPracticas + examenParcial * pesoParcial + examenFinal * pesoFinal) / pesoTotal
    
    return promedioFinal

import json
from pathlib import Path

#* Extrae los datos del json para usarlos
RUTA_DATOS = Path(__file__).resolve().parent / "datos_cursos.json"
with open(RUTA_DATOS, "r", encoding="utf-8") as file:
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

#* Manejo de valores pa notas especiales
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
    monografiasUsadas = datosCursos[codigoCurso].get("Monografias")

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
    monografiasContables = sorted(monografias)[-monografiasUsadas:] + [0] * ceroAMonografias

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

    examenParcial = convertirANumero(examenParcial)
    examenFinal = convertirANumero(examenFinal)
    examenSustitutorio = convertirANumero(examenSustitutorio)
    
    if(examenParcial != -2 and examenFinal != -2):
        # Validar la mejor nota cuando existe sustitutorio
        if (examenSustitutorio > 0 or examenSustitutorio == -2):
            promedioEpEs = promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenSustitutorio, examenFinal, 0)
            promedioEfEs = promedioFinalCurso(practicas, laboratorios, monografias, codigoCurso, examenParcial, examenSustitutorio, 0)
            if promedioEpEs > promedioEfEs:
                examenParcial = examenSustitutorio
            else:
                examenFinal = examenSustitutorio
        if(examenSustitutorio == -2):
            examenSustitutorio = 0

    elif((examenParcial == -2 and examenFinal != -2)):
        examenFinal = examenSustitutorio
        examenParcial = 0
    elif((examenFinal == -2 and examenParcial != -2)):
        examenParcial = examenSustitutorio 
        examenFinal = 0
    elif((examenParcial == -2 and examenFinal == -2)):
        examenParcial = 0
        examenFinal = 0
    
    # Calcula el promedio final ponderado
    promedioFinal = (promedioDePracticas * pesoPracticas + examenParcial * pesoParcial + examenFinal * pesoFinal) / pesoTotal
    
    return promedioFinal

def notaExamen(valor):
    """Devuelve una nota lista para mostrar: reemplaza los códigos especiales por su texto."""
    if valor == -2:
        return "0A"
    if valor == 0:
        return "0"
    return str(valor)

def resolverSustitutorio(practicas, laboratorios, monografias, codigoCurso, examenParcial, examenFinal, examenSustitutorio):
    """Determina qué nota de examen se usó realmente en el promedio final.

    No vuelve a implementar las reglas: comprueba qué combinación de notas reproduce el
    promedio que realmente devolvió promedioFinalCurso, de modo que el desglose que se
    muestra en la interfaz nunca puede contradecir al resultado.

    Devuelve (parcial, final, sustitucion) con "sustitucion" en {"parcial", "final"} o None.
    """
    epIngresado = convertirANumero(examenParcial)
    efIngresado = convertirANumero(examenFinal)
    es = convertirANumero(examenSustitutorio)

    promedioReal = promedioFinalCurso(
        practicas, laboratorios, monografias, codigoCurso,
        examenParcial, examenFinal, examenSustitutorio
    )

    promedioContinuas = promedioPracticas(practicas, laboratorios, monografias, codigoCurso)
    pesoPracticas, pesoParcial, pesoFinal = mapaSis[datosCursos[codigoCurso].get("TipoCalificacion")]
    pesoTotal = pesoPracticas + pesoParcial + pesoFinal

    def pondera(parcial, final):
        return (promedioContinuas * pesoPracticas + parcial * pesoParcial + final * pesoFinal) / pesoTotal

    # Valores que un examen puede tomar tras la resolución:
    # la nota ingresada, la del sustitutorio, 0 (no se presentó) o -2 (ausente)
    candidatos = {epIngresado, efIngresado, es, 0, -2}
    for parcial in candidatos:
        for final in candidatos:
            if abs(pondera(parcial, final) - promedioReal) < 1e-9:
                # Determinamos qué nota quedó afuera: la que no coincide con lo ingresado
                if es != 0 and (parcial == es or final == es):
                    sustitucion = "parcial" if parcial == es else "final"
                elif (parcial != epIngresado or final != efIngresado):
                    # el ausente no se presentó: el sustitutorio ocupa su lugar
                    if efIngresado == -2:
                        sustitucion = "final"
                    elif epIngresado == -2:
                        sustitucion = "parcial"
                    else:
                        sustitucion = "final"
                else:
                    sustitucion = None
                return parcial, final, sustitucion

    # Sin coincidencia: mostramos lo ingresado
    return epIngresado, efIngresado, None

#* Etiquetas de las evaluaciones, para identificar cuáles son "pendientes"
TIPOS_CONTINUAS = ("Practicas", "Laboratorios", "Monografias")

def nombreEvaluacion(tipo, indice):
    """Devuelve la etiqueta legible de una evaluación pendiente."""
    singular = {"Practicas": "Práctica", "Laboratorios": "Laboratorio", "Monografias": "Monografía"}
    if tipo in TIPOS_CONTINUAS:
        return f"{singular[tipo]} {indice + 1}"
    return {
        "ExamenParcial": "Examen parcial",
        "ExamenFinal": "Examen final",
        "ExamenSustitutorio": "Examen sustitutorio",
    }[tipo]

def _composiciones(suma, partes, maximo, prefijo=()):
    """Genera todas las listas de `partes` valores en [0, maximo] que suman `suma`."""
    if partes == 1:
        if 0 <= suma <= maximo:
            yield prefijo + (suma,)
        return
    for valor in range(max(0, suma - maximo * (partes - 1)), min(maximo, suma) + 1):
        yield from _composiciones(suma - valor, partes - 1, maximo, prefijo + (valor,))

def simularNotaMinima(practicas, laboratorios, monografias, codigoCurso,
                      examenParcial, examenFinal, examenSustitutorio,
                      pendientes, objetivo=10):
    """Calcula la nota mínima necesaria en cada evaluación pendiente para alcanzar un objetivo.

    `pendientes` es una lista de tuplas (tipo, indice) con las evaluaciones aún no rendidas.
    Se prueban combinaciones ordenadas por suma total creciente, así que la primera que
    alcanza el objetivo es la de menor esfuerzo: las notas son lo más bajas posibles y
    lo más parejas posible entre sí.

    Devuelve (lista de (etiqueta, nota), promedio alcanzado), o None si es imposible.
    """
    if not pendientes:
        return None

    # Cada pendiente parte de "no presentado" (0) y se busca su nota mínima
    base = {
        "Practicas": [convertirANumero(p) for p in practicas],
        "Laboratorios": [convertirANumero(l) for l in laboratorios],
        "Monografias": [convertirANumero(m) for m in monografias],
    }
    for tipo, indice in pendientes:
        if tipo in base:
            base[tipo][indice] = 0

    def promedia(asignacion):
        """Calcula el promedio final con la asignación de notas propuesta."""
        p = list(base["Practicas"])
        l = list(base["Laboratorios"])
        m = list(base["Monografias"])
        parcial, final, susti = examenParcial, examenFinal, examenSustitutorio

        for (tipo, indice), nota in zip(pendientes, asignacion):
            if tipo == "Practicas":
                p[indice] = nota
            elif tipo == "Laboratorios":
                l[indice] = nota
            elif tipo == "Monografias":
                m[indice] = nota
            elif tipo == "ExamenParcial":
                parcial = nota
            elif tipo == "ExamenFinal":
                final = nota
            elif tipo == "ExamenSustitutorio":
                susti = nota

        return promedioFinalCurso(p, l, m, codigoCurso, parcial, final, susti)

    # Se prueban sumas de 0 hacia arriba (20 es la nota máxima de la UNI).
    # La primera combinación que alcanza el objetivo es la de menor esfuerzo total.
    totalPartes = len(pendientes)
    for suma in range(totalPartes * 20 + 1):
        for asignacion in _composiciones(suma, totalPartes, 20):
            promedio = promedia(asignacion)
            if promedio is not None and promedio + 1e-9 >= objetivo:
                return (
                    [(nombreEvaluacion(t, i), nota)
                     for (t, i), nota in zip(pendientes, asignacion)],
                    promedio,
                )

    return None

# --------------------------------------------------------- Matriz de simulación

#* Valores posibles de una nota en la escala de la UNI (0 a 20)
VALORES_NOTA = list(range(0, 21))

#* Tope de combinaciones por llamada: N^M crece rápido (21^5 = 4.1 millones)
TOPE_COMBINACIONES = 2_000_000

def _construirNota(practicas, laboratorios, monografias, pendientes, asignacion, parcial, final, susti):
    """Arma la lista de notas del curso aplicando la fila de la matriz que se está probando."""
    p = list(practicas)
    l = list(laboratorios)
    m = list(monografias)
    for (tipo, indice), nota in zip(pendientes, asignacion):
        if tipo == "Practicas":
            p[indice] = nota
        elif tipo == "Laboratorios":
            l[indice] = nota
        elif tipo == "Monografias":
            m[indice] = nota
        elif tipo == "ExamenParcial":
            parcial = nota
        elif tipo == "ExamenFinal":
            final = nota
        elif tipo == "ExamenSustitutorio":
            susti = nota
    return p, l, m, parcial, final, susti

def matrizSimulacion(practicas, laboratorios, monografias, codigoCurso,
                     examenParcial, examenFinal, examenSustitutorio,
                     pendientes, objetivo=10, maximoFilas=300):
    """Recorre la matriz de combinaciones posibles y guarda las que alcanzan el objetivo.

    La matriz tiene M filas por cada una de las N combinaciones posibles: M son las
    evaluaciones pendientes y N = 21 los valores posibles de cada una (0 a 20).
    Se recorren las N^M combinaciones y en cada una se calcula el promedio final,
    conservando las que llegan al objetivo pedido.

    Devuelve un diccionario con:
      combinaciones  -> cuántas filas se evaluaron
      filas          -> las filas que alcanzan el objetivo (menor esfuerzo primero)
      mejor          -> la fila de menor esfuerzo total
      alcanzable     -> False si ninguna combinación llega al objetivo
      truncado       -> True si se superaron las filas guardadas
    """
    import itertools

    if not pendientes:
        return None

    baseP = [convertirANumero(x) for x in practicas]
    baseL = [convertirANumero(x) for x in laboratorios]
    baseM = [convertirANumero(x) for x in monografias]
    epBase, efBase, esBase = examenParcial, examenFinal, examenSustitutorio

    total = len(VALORES_NOTA) ** len(pendientes)
    if total > TOPE_COMBINACIONES:
        return {"combinaciones": total, "filas": [], "mejor": None,
                "alcanzable": None, "truncado": False, "demasiado": True}

    etiquetas = [nombreEvaluacion(t, i) for t, i in pendientes]
    filas = []
    combinaciones = 0

    for asignacion in itertools.product(VALORES_NOTA, repeat=len(pendientes)):
        combinaciones += 1
        p, l, m, parcial, final, susti = _construirNota(
            baseP, baseL, baseM, pendientes, asignacion, epBase, efBase, esBase
        )
        promedio = promedioFinalCurso(p, l, m, codigoCurso, parcial, final, susti)
        if promedio is None:
            continue
        if promedio + 1e-9 >= objetivo:
            fila = dict(zip(etiquetas, asignacion))
            fila["_promedio"] = promedio
            fila["_esfuerzo"] = sum(asignacion)
            fila["_desviacion"] = max(asignacion) - min(asignacion)
            filas.append(fila)

    # Menos esfuerzo primero; a igual esfuerzo, la combinación menos desviada
    # (la que reparte más parejo las notas entre las evaluaciones pendientes).
    filas.sort(key=lambda f: (f["_esfuerzo"], f["_desviacion"], -f["_promedio"]))
    truncado = len(filas) > maximoFilas

    return {
        "combinaciones": combinaciones,
        "filas": filas[:maximoFilas],
        "mejor": filas[0] if filas else None,
        "alcanzable": bool(filas),
        "truncado": truncado,
        "demasiado": False,
    }

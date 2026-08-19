# Diccionario para traducir palabras a operadores de Python
operadores = {
    "inter": "&",           # Intersección
    "&": "&",               # Intersección
    "union": "|",           # Unión
    "|": "|",               # Unión
    "menos": "-",           # Diferencia
    "-": "-",               # Diferencia (símbolo)
    "\\": "-",              # Diferencia (símbolo alternativo)
    "simdiff": "^",         # Diferencia simétrica
    "^": "^"                # Diferencia simétrica (símbolo)
}


def resolver_operación[T, U](expresión, set_namespace: dict[T, set[U]]) -> set[U]:
    """
    Toma una expresión de texto y un diccionario de conjuntos, 
    la traduce a sintaxis de Python y devuelve el conjunto resultante.
    """
    
    # PASO 1: Crear nombres de variables seguras para Python
    variables_seguras = {}
    mapa_nombres = {}
    
    for i, (nombre, valor) in enumerate(set_namespace.items()):
        var_name = f"conjunto_{i}"
        variables_seguras[var_name] = valor
        mapa_nombres[nombre] = var_name

    # PASO 2: Dar formato a la expresión
    # Añadimos espacios alrededor de los paréntesis y símbolos para 
    # asegurarnos de que no se queden pegados a los nombres de los conjuntos.
    símbolos_a_separar = ["(", ")", "\\", "-"]
    for sím in símbolos_a_separar:
        expresión = expresión.replace(sím, f" {sím} ")
        
    # Dividimos la expresión en una lista de palabras/símbolos
    tokens = expresión.split()

    # PASO 3: Traducir la expresión a sintaxis de Python
    expresión_traducida = []
    
    for token in tokens:
        if token in mapa_nombres:
            # Si es un conjunto, usamos nuestro nombre seguro
            expresión_traducida.append(mapa_nombres[token])
        elif token in operadores:
            # Si es un operador, usamos el símbolo correspondiente en Python
            expresión_traducida.append(operadores[token])
        elif token in ["(", ")"]:
            # Los paréntesis se quedan exactamente igual
            expresión_traducida.append(token)
        else:
            print(f"Error: No reconozco el elemento '{token}' en tu operación.")
            return None

    # Unimos la lista para formar una línea de código válida en Python
    código_a_evaluar = " ".join(expresión_traducida)

    # PASO 4: Evaluar la expresión
    try:
        # eval() ejecuta la cadena de texto como si fuera código Python real.
        # Le pasamos nuestras variables seguras para que pueda hacer el cálculo.
        resultado = eval(código_a_evaluar, {"__builtins__": None}, variables_seguras)
        return resultado
    except SyntaxError:
        print("Error: La sintaxis de la operación no es válida. Revisa los paréntesis y operadores.")
        return None

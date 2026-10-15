"""Cálculo secuencial y con procesos de una suma de cuadrados."""

from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import os


def _validar_configuracion(tamano_lote, max_workers):
    if isinstance(tamano_lote, bool) or not isinstance(tamano_lote, int) or tamano_lote <= 0:
        raise ValueError("tamano_lote debe ser un entero positivo")
    if isinstance(max_workers, bool) or not isinstance(max_workers, int) or max_workers <= 0:
        raise ValueError("max_workers debe ser un entero positivo")


def crear_lotes(numeros, tamano_lote, max_workers=1):
    """Divide los datos en lotes consecutivos; max_workers se valida aquí."""
    _validar_configuracion(tamano_lote, max_workers)
    datos = list(numeros)
    return [
        (indice, datos[inicio:inicio + tamano_lote])
        for indice, inicio in enumerate(range(0, len(datos), tamano_lote))
    ]


def calcular_lote(lote):
    """Procesa un lote y devuelve (id, pid, cantidad, suma_parcial)."""
    id_lote, numeros = lote
    pid = os.getpid()
    total = 0
    for numero in numeros:
        if isinstance(numero, bool) or not isinstance(numero, int) or numero < 0:
            raise ValueError(
                f"Dato invalido en lote {id_lote}, PID {pid}: {numero!r}"
            )
        total += numero ** 2
    return (id_lote, pid, len(numeros), total)


def ejecutar_secuencial(numeros, tamano_lote, max_workers=1):
    lotes = crear_lotes(numeros, tamano_lote, max_workers)
    return _ejecutar_secuencial_lotes(lotes)


def _ejecutar_secuencial_lotes(lotes):
    return [calcular_lote(lote) for lote in lotes]


def ejecutar_procesos(numeros, tamano_lote, max_workers=2):
    lotes = crear_lotes(numeros, tamano_lote, max_workers)
    return _ejecutar_procesos_lotes(lotes, max_workers)


def _ejecutar_procesos_lotes(lotes, max_workers):
    if not lotes:
        return []
    contexto = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=max_workers, mp_context=contexto) as pool:
        return list(pool.map(calcular_lote, lotes))


def agregar_resultados(resultados, lotes):
    """Valida identidad y cantidades antes de sumar, sin depender del orden."""
    esperados = {id_lote: len(datos) for id_lote, datos in lotes}
    vistos = {}
    for resultado in resultados:
        if not isinstance(resultado, tuple) or len(resultado) != 4:
            raise ValueError(f"Formato de resultado invalido: {resultado!r}")
        id_lote, pid, cantidad, parcial = resultado
        campos = (id_lote, pid, cantidad, parcial)
        if any(isinstance(campo, bool) or not isinstance(campo, int) for campo in campos):
            raise ValueError(f"Los campos del resultado deben ser enteros: {resultado!r}")
        if id_lote not in esperados:
            raise ValueError(f"ID de lote desconocido: {id_lote}")
        if id_lote in vistos:
            raise ValueError(f"Resultado repetido para lote {id_lote}")
        if cantidad != esperados[id_lote]:
            raise ValueError(
                f"Cantidad incorrecta en lote {id_lote}: {cantidad}, esperada {esperados[id_lote]}"
            )
        vistos[id_lote] = parcial
    faltan = set(esperados) - set(vistos)
    if faltan:
        raise ValueError(f"Faltan resultados de los lotes: {sorted(faltan)}")
    cantidad_recibida = sum(resultado[2] for resultado in resultados)
    cantidad_planificada = sum(esperados.values())
    if cantidad_recibida != cantidad_planificada:
        raise ValueError("El total de elementos planificados no coincide")
    return sum(vistos.values())

"""Comprobaciones del contrato de suma_cuadrados."""

import multiprocessing
from suma_cuadrados import (
    agregar_resultados,
    calcular_lote,
    crear_lotes,
    ejecutar_procesos,
    ejecutar_secuencial,
)


def comprobar_error(funcion, *args):
    try:
        funcion(*args)
    except ValueError:
        return
    raise AssertionError(f"Se esperaba ValueError en {funcion.__name__}")


def main():
    datos = list(range(1, 51))
    lotes = crear_lotes(datos, 7, 2)
    assert len(lotes) == 8 and sum(map(lambda x: len(x[1]), lotes)) == 50
    sec = ejecutar_secuencial(datos, 7, 2)
    assert agregar_resultados(sec, lotes) == 42925
    proc = ejecutar_procesos(datos, 7, 2)
    assert agregar_resultados(proc, lotes) == 42925
    assert ejecutar_secuencial([], 7, 2) == []
    assert agregar_resultados([], []) == 0
    lotes_pequenos = crear_lotes([1, 2, 3], 2, 1)
    assert [l[1] for l in lotes_pequenos] == [[1, 2], [3]]
    assert agregar_resultados(ejecutar_secuencial([1, 2, 3], 2), lotes_pequenos) == 14
    assert agregar_resultados(ejecutar_secuencial([0], 2), crear_lotes([0], 2)) == 0
    for tamano, workers in ((0, 1), (-1, 1), (True, 1), (1, 0), (1, -1), (1, True)):
        comprobar_error(crear_lotes, [], tamano, workers)
    for malo in (-1, True, 1.5):
        comprobar_error(calcular_lote, (0, [malo]))
    comprobar_error(ejecutar_procesos, [1, -1, 3], 2, 2)
    assert not [proceso for proceso in multiprocessing.active_children() if proceso.is_alive()]
    assert agregar_resultados(list(reversed(sec)), lotes) == 42925
    comprobar_error(agregar_resultados, sec + [sec[0]], lotes)
    comprobar_error(agregar_resultados, sec[:-1], lotes)
    desconocido = list(sec)
    desconocido[0] = (1000, *desconocido[0][1:])
    comprobar_error(agregar_resultados, desconocido, lotes)
    incoherente = list(sec)
    incoherente[0] = (incoherente[0][0], incoherente[0][1], 99, incoherente[0][3])
    comprobar_error(agregar_resultados, incoherente, lotes)
    assert agregar_resultados(ejecutar_procesos([1, 2, 3], 2, 2), lotes_pequenos) == 14
    assert not [proceso for proceso in multiprocessing.active_children() if proceso.is_alive()]
    print("Todas las pruebas han terminado correctamente.")


if __name__ == "__main__":
    main()

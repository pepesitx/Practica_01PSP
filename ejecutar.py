"""Lanzador de las variantes secuencial y multiproceso."""

import argparse
import json
import statistics
import sys
from time import perf_counter

from suma_cuadrados import (
    agregar_resultados,
    crear_lotes,
    ejecutar_procesos,
    ejecutar_secuencial,
    _ejecutar_procesos_lotes,
    _ejecutar_secuencial_lotes,
)


def ejecutar_medida(modo, datos, lote, workers):
    inicio = perf_counter()
    lotes = crear_lotes(datos, lote, workers)
    if modo == "secuencial":
        resultados = _ejecutar_secuencial_lotes(lotes)
    else:
        resultados = _ejecutar_procesos_lotes(lotes, workers)
    total = agregar_resultados(resultados, lotes)
    return total, perf_counter() - inicio, lotes, resultados


def main(argv=None):
    parser = argparse.ArgumentParser(description="Suma cuadrados de un lote de numeros")
    parser.add_argument("--modo", choices=("ambos", "secuencial", "procesos"), default="ambos")
    parser.add_argument("--datos", default="[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]")
    parser.add_argument("--lote", type=int, default=7)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--repeticiones", type=int, default=1)
    parser.add_argument("--detalle", action="store_true")
    args = parser.parse_args(argv)
    datos = json.loads(args.datos)
    if not isinstance(datos, list):
        raise ValueError("--datos debe ser una lista JSON")
    if isinstance(args.repeticiones, bool) or args.repeticiones <= 0:
        raise ValueError("repeticiones debe ser un entero positivo")
    modos = [args.modo] if args.modo != "ambos" else ["secuencial", "procesos"]
    tiempos = {modo: [] for modo in modos}
    referencia = None
    for repeticion in range(args.repeticiones):
        orden = modos if repeticion % 2 == 0 else list(reversed(modos))
        for modo in orden:
            total, duracion, lotes, resultados = ejecutar_medida(
                modo, datos, args.lote, args.workers
            )
            tiempos[modo].append(duracion)
            if referencia is None:
                referencia = total
            elif total != referencia:
                raise ValueError(f"Total distinto del otro modo: {total} != {referencia}")
            if args.detalle:
                print(f"{modo}: lotes={len(lotes)}, elementos={len(datos)}, total={total}")
                print(f"  resultados={resultados}")
            else:
                print(f"{modo}: total={total}")
            print(f"  tiempo={duracion:.9f} s")
    for modo, muestras in tiempos.items():
        print(f"Mediana {modo}: {statistics.median(muestras):.9f} s")
    if "secuencial" in tiempos and "procesos" in tiempos:
        mediana_seq = statistics.median(tiempos["secuencial"])
        mediana_proc = statistics.median(tiempos["procesos"])
        razon = mediana_seq / mediana_proc if mediana_proc else float("inf")
        print(f"Aceleracion (secuencial/procesos): {razon:.6f}")
    if datos == list(range(1, 51)) and referencia != 42925:
        raise ValueError(f"El caso de referencia debe sumar 42925, no {referencia}")
    return 0


if __name__ == "__main__":
    # Con spawn cada proceso importa este modulo; la proteccion evita relanzar
    # el programa completo en cada trabajador.
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        raise SystemExit(1)

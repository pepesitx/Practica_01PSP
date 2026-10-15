# P1.1 · Procesador de lotes

## Requisitos

Python 3.14.x y Git. No se utilizan bibliotecas externas. Los comandos de abajo
son para PowerShell en Windows; actívalos desde la carpeta del proyecto.

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -c "import sys; print(sys.executable)"
git init
```

Anota la versión exacta y la ruta que imprimen los dos comandos. Las rutas
dependen del ordenador y no deben inventarse.

## Uso

```powershell
python pruebas.py
python ejecutar.py --lote 7 --workers 2 --repeticiones 5 --detalle
python ejecutar.py --modo procesos --datos "[1,-1,3]" --lote 2 --repeticiones 1
```

El último comando debe terminar con código distinto de cero y mostrar el lote y
el PID que detectó el dato inválido.

## Diseño

`crear_lotes` asigna IDs consecutivos a listas de datos. `calcular_lote` recorre
los datos y devuelve `(id_lote, pid, cantidad, suma_parcial)`. La versión
secuencial llama a esa misma función en el coordinador. La versión con procesos
crea un único `ProcessPoolExecutor` con contexto `spawn`; `map` conserva el
orden de entrada y entregar los resultados también recoge las excepciones de
los trabajadores. El bloque `if __name__ == "__main__"` evita que al importar
el lanzador los procesos vuelvan a iniciar el programa entero. El contexto del
pool espera a sus tareas y cierra los trabajadores al salir del bloque `with`.

Los trabajadores devuelven tuplas porque cada proceso tiene memoria propia: no
puede actualizar directamente una variable global del coordinador. El
coordinador comprueba los resultados en `agregar_resultados` y allí calcula el
total final. Puede haber ocho lotes y solo hasta dos trabajadores; no se
requiere que cada uno obtenga el mismo número de tareas o que se vean dos PID
distintos en un trabajo tan corto.

## Medición e interpretación

El lanzador alterna el orden de las variantes y usa `perf_counter`. Registra
cada muestra en segundos, las medianas y la razón `mediana secuencial / mediana
con procesos`. La medición incluye particionado, cálculo, agregación y, para
procesos, creación y cierre del pool; deja fuera las impresiones de detalle.
Completa la tabla con la salida real de cinco repeticiones:

| Variante | Cinco tiempos (s) | Mediana (s) |
|---|---|---|
| Secuencial | 0.000080900, 0.000058200, 0.000032800, 0.000061200, 0.000038200 | 0.000058200 |
| Procesos | 0.285547700, 0.264678900, 0.257426500, 0.248961500, 0.252557500 | 0.257426500 |

Razón de aceleración observada: 0.000226. Los procesos tardaron más, algo esperable para una operación tan pequeña por el coste de
crear y coordinar procesos. Un experimento futuro podría aumentar el rango de
datos o hacer que cada dato implicara un cálculo útil más costoso. No se debe
presentar una salida esperada como medición real.

La ejecución disponible fue Python 3.13.14 (ruta: `.venv\\Scripts\\python.exe`),
no la versión 3.14.x solicitada. Debe repetirse en Python 3.14.x para la entrega
final; las mediciones de arriba son reales y se obtuvieron con 3.13.14.

## Memoria y entrega

En la memoria añade nombre del autor, versión/ruta de Python, tabla de tiempos,
resultados reales, salida de las pruebas, del fallo controlado y estado básico
de Git. Explica los cuatro temas del enunciado: modelo, memoria/comunicación,
arranque/finalización y orden/rendimiento. Indica como ayuda: asistencia de IA
para preparar y revisar la implementación. No se ha consultado documentación
externa.

Para el ZIP de entrega, incluye los `.py`, este README, la memoria PDF y la
carpeta `evidencias/`. Excluye `.venv/` y `__pycache__/`.

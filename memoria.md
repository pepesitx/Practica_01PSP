# P1.1 · Procesador de lotes

**Autor:** completar nombre y apellidos  
**Entorno medido:** Python 3.13.14 en Windows; intérprete `.venv\Scripts\python.exe`  
**Aviso:** el enunciado pide Python 3.14.x. Esta memoria debe volver a medirse en esa versión antes de la entrega final.

## Reparto y comprobaciones

El caso usa 50 datos, 1 a 50, divididos en 8 lotes: siete contienen 7 datos y el último contiene 1. Se configura un máximo de 2 procesos trabajadores. Cada lote es una tarea; los datos son los valores que procesa esa tarea. La prueba obtuvo 42925 tanto en secuencial como en multiproceso.

Cada trabajador devuelve `(id_lote, pid, cantidad, suma_parcial)`. El PID identifica el proceso que ejecutó el cálculo. En la ejecución breve se observó un único PID trabajador para varios lotes; no se exigen dos PIDs distintos porque el pool reutiliza procesos y la cola de trabajo es muy corta.

El trabajador devuelve una tupla porque cada proceso tiene su propio espacio de memoria y una variable global del coordinador no sería compartida automáticamente. El coordinador recoge las tuplas; `agregar_resultados` comprueba IDs, duplicados, ausencias y cantidades y calcula allí el total final.

## Arranque, finalización y orden

El contexto `spawn` inicia procesos limpios e importa el módulo trabajador. La protección `if __name__ == "__main__"` impide que esos imports vuelvan a lanzar el programa completo. El coordinador crea un pool por ejecución, consume `pool.map` dentro de un bloque `with` y este espera y cierra los trabajadores incluso si una tarea comunica una excepción.

`map` entrega resultados en el orden de las entradas aunque las tareas puedan terminar en otro orden. La agregación además identifica por ID y acepta una lista invertida. El fallo con `-1` se propagó al coordinador y una ejecución válida posterior terminó correctamente sin trabajadores propios activos.

## Tiempos

| Variante | Muestras (s) | Mediana (s) |
|---|---|---|
| Secuencial | 0.000080900; 0.000058200; 0.000032800; 0.000061200; 0.000038200 | 0.000058200 |
| Procesos | 0.285547700; 0.264678900; 0.257426500; 0.248961500; 0.252557500 | 0.257426500 |

Aceleración (mediana secuencial / mediana procesos): **0.000226**. La variante con procesos tardó más porque crear, coordinar y cerrar el pool cuesta mucho más que elevar 50 enteros al cuadrado. Añadir trabajadores no garantiza reducir el tiempo: incrementa el coste de arranque y coordinación, y esta carga no permite amortizarlo. Merecería estudiar un rango de datos mucho mayor o más trabajo útil por dato.

Las pruebas obligatorias ejecutadas terminaron correctamente con el Python disponible. Para esta implementación se utilizó asistencia de IA como apoyo para elaborar el código y revisar el contrato; el enunciado permite ese uso. No se consultaron fuentes externas.


# Solver Funnys Company

Sistema de optimización para la localización de plantas y distribución de productos de **Funnys Company**, desarrollado en Python utilizando **PuLP** y **pandas**.  

El modelo se resuelve con el solver **CBC (Coin-or Branch and Cut)** a través de la librería PuLP y permite determinar la configuración óptima de apertura de plantas y asignación de flujos de transporte en un horizonte de 3 años, minimizando costos de apertura, operación, producción y transporte.


## Grupo 
* **Syntax Terror**
 

## Ejecución del modelo

1. **Clonar el repositorio**:

   EAbre tu terminal o línea de comandos y clona el repositorio:

   ```bash
   git clone https://github.com/lmellan/Solver_funnys.git
   cd Solver_funnys
   ````

2. **Instalar dependencias**:

   Asegúrate de tener Python 3.9+ instalado. Luego, instala las librerías necesarias:

   ```bash
   pip install pulp pandas
   ```

3. **Ejecutar el solver**:

   Dentro de la carpeta del proyecto, corre el script:

   ```bash
   python solve_funnys.py
   ```

   Esto realizará las siguientes acciones:

   * Construirá y resolverá el modelo matemático de localización y distribución.
   * Mostrará en consola:

     * Estado de la solución.
     * Valor de la función objetivo.
     * Apertura de plantas seleccionadas.
     * Flujos de transporte asignados por región y año.
   * Generará dos archivos CSV:
     * `solucion_plantas.csv` → Configuración de plantas abiertas.
     * `solucion_flujos.csv` → Plan de transporte con detalle de volúmenes, regiones y años.

 
## Instrucciones de uso de la aplicación

Una vez ejecutado el solver (`solve_funnys.py`), aparecerá una salida en consola similar a la siguiente:

```
Estado: Optimal
Valor de la función objetivo: 445,611,774.16

=== Apertura de plantas ===
x[Rancagua,pequena] = 1.0
x[Rancagua,grande] = 0.0
x[Antofagasta,pequena] = 1.0
...

=== Flujos de transporte ===
y[Rancagua,r1,AT2,1] = 951776.0
y[Rancagua,r2,AT1,1] = 967364.0
...
```

Estos resultados también estarán guardados en los archivos `.csv` generados en la carpeta del proyecto.

 
 

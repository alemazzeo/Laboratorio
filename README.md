# Laboratorio
## Cámara
### camara.py
Contiene la clase Camara. Permite conectar, calibrar y obtener patrones de intensidad en función de la distancia. Tiene funciones tales como calibrar directamente sobre el video, ver una animación en tiempo real del perfil obtenido y guardar capturas. Puede articularse con el módulo de difracción contenido en el archivo analisis.py para realizar un estudio dinámico.
### analisis.py
Contiene la clase Difraccion utilizada en la práctica de Módulo de Young para medir una flexión muy pequeña. El método requiere un patrón de intensidad sobre el cual se realiza la detección de franjas y se calcula el tamaño de la rendija. Cuenta con una función que dado un origen de datos puede realizar un análisis dinámico y graficar en forma continua los resultados.
## Instrumentos
### instrumentos.py
Contiene hasta el momento la clase Lockin para el manejo de un Amplificador Lock-In SR830. Dicho objeto encapsula las propiedades del instrumento facilitando el control del mismo y cuenta con funciones para la adquisición tales como la captura simultánea de valores, el barrido de frecuencias y la creación de registros de estado. El objeto cuenta con un modo de simulación que permite probar el código sin la necesidad de tener conectado el instrumento.
### ejemplos.py
Contiene hasta el momento ejemplos de la utilización del objeto Lockin contenido en el archivo instrumentos.py. El ejemplo trabaja con el modo simulador de dicho objeto pero puede ser utilizado (cambiando el parámetro modo_simulador) con el propio instrumento.
## Resistividad
### adquisicion.py
Contiene las rutinas utilizadas para la adquisición de datos durante la práctica correspondiente a Susceptibilidad y Magnetismo, en la cual se midió la resistividad eléctrica por un método no inductivo.
### analisis.py
Contiene la carga de los datos obtenidos mediante el archivo adquisición.py y el análisis de los mismos.

# Sistema de Monitoreo y Detección de Ataques DDoS en Redes Industriales utilizando FPGA Nexys Video

Este repositorio tiene el código y los resultados de un sistema creado para detectar ataques DDoS sin interrumpir el funcionamiento de la red. Está pensado para proteger redes de fábricas o industrias que se comunican con el protocolo Modbus/TCP. 

El sistema funciona combinando dos cosas: un programa en el computador (Python) que mira el tráfico de la red, y una placa física (FPGA Nexys Video) que hace los cálculos matemáticos a toda velocidad para detectar el ataque en tiempo real.

## Estructura de las Carpetas

### `Software_preprocesamiento/`
Aquí están los programas de computador (en Python) que revisan la red y conversan con la placa FPGA.
* **`preprocesador.py`**: Es el programa principal. Captura los datos de la red de forma invisible. Cada segundo, cuenta cuántos paquetes de datos llegan (C1), cuántas direcciones IP distintas hay (C2) y qué tan variadas son (C3). Luego manda estos números a la placa FPGA, espera a ver si la placa responde con una alarma ("ALERTA_DDOS") y guarda los resultados en archivos.
* **`perfil_normal.py`**: Este programa analiza cómo se comporta la red sin ataques. Saca los promedios para enseñarle al sistema qué es seguro y define un umbral para que suene la alarma.
* **`perfil_normal.json`**: Un archivo de texto que guarda los valores "normales" que calculó el programa anterior. El sistema lee esto antes de empezar a vigilar la red.

### `Hardware_FPGA/`
Aquí están los archivos de código que van instalados dentro de la placa física (FPGA Nexys Video).
* **`Detector.xpr`**: Es el archivo que debes abrir en el programa Vivado para poder cargar todo a la placa.
* **`integrador.v`**: Es la pieza principal que conecta y organiza todas las partes del código dentro de la placa.
* **`nahid.v`**: Aquí está la fórmula matemática que compara el tráfico actual con el tráfico normal para decidir si hay un ataque.
* **`th.v`**: Se encarga de ajustar el umbral de sensibilidad para que las alarmas no suenen por error.
* **`parser.v`**: Traduce los textos que manda el computador a números que la placa pueda entender y procesar.
* **`conexionUART.v`**: Recibe los datos que llegan desde el computador a través del cable USB.
* **`uart_tx.v`**: Envía información desde la placa de vuelta al computador.
* **`alerta_ddos.v`**: Cuando NaHiD detecta un ataque, esta pieza se encarga de enviarle el mensaje de "ALERTA_DDOS" al computador.
* **`fisico.xdc`**: Conecta el código que escribimos con las partes físicas de la placa, como sus pines, botones y luces LED.

### `Entorno_industrial/`
Aquí están los archivos para hacer funcionar los equipos físicos que simulan ser la fábrica.
* **`lectura_sensor.ino`**: Es el programa que va dentro del equipo industrial (PLC Arduino Opta). Lee la temperatura de un sensor real y la comparte por la red.
* **`Mbpoll1.mbp`**: Una configuración para simular ser la sala de control de la fábrica, pidiéndole datos al PLC cada 1ms de forma ordenada.
* **`switch configuration.txt`**: Es la configuración del equipo de red (switch Cisco 3560). Su trabajo es hacer "Port Mirroring" de los datos para que nuestro computador pueda revisarlos sin estorbar ni poner lenta a la fábrica.

### `Resultados/`
Aquí se guardan todos los datos recolectados durante las pruebas y los programas que dibujan los gráficos finales.

**Archivos de Datos:**
* **`datos_normales.csv`**: Datos guardados de la red funcionando tranquila, para usarlos de ejemplo.
* **`vectores_capturados.csv`**: Una lista que guarda segundo a segundo lo que está pasando en la red (esté normal o bajo ataque).
* **`archivo_impacto.csv`**: Guarda cuánto tarda en responder el equipo de la fábrica, para ver si el ataque logró desconectarlo.
* **`historial_ataques.csv`**: Un registro de las horas exactas en que sonaron las alarmas y cuánto se demoró el sistema en reaccionar.
* **`metricas.csv`**: Guarda los aciertos y las falsas alarmas para evaluar qué tan bueno es el sistema.

**Programas para Gráficos y Análisis:**
* **`metricas.py`**: Junta todos los datos y te da la nota final del sistema (como su latencia y su precisión).
* **`c1graf.py`, `c2graf.py`, `c3graf.py`**: Programas que dibujan gráficos para comparar visualmente cómo se ve la red normal frente a un ataque cibernético.
* **`disponibilidadgraf.py`**: Dibuja el gráfico que muestra cómo el equipo de la fábrica se "cae" y deja de responder cuando recibe el ataque.

## Requisitos para hacerlo funcionar
* Una placa física FPGA Digilent Nexys Video.
* El programa Xilinx Vivado instalado en el computador.
* Tener Python instalado (versión 3.10 o más nueva) con las herramientas `pyshark` y `pyserial`.
* Tener el programa Wireshark instalado en el computador.

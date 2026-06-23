# Sistema de Monitoreo y Detección de Ataques DDoS en Redes Industriales utilizando FPGA Nexys Video

Este repositorio contiene el código fuente, los esquemas y los resultados de las pruebas de un sistema de detección pasiva de ataques volumétricos (DDoS) diseñado para entornos de *Operational Technology* (OT), específicamente para proteger redes industriales basadas en el protocolo Modbus/TCP. 

El sistema utiliza un enfoque de hardware/software: extrae características del tráfico mediante Python/Pyshark y deja la detección en tiempo real a una FPGA (Artix-7 Nexys Video) implementando el algoritmo NaHiD.

## Estructura del Repositorio

### `Software_preprocesamiento/`
Contiene los scripts de Python encargados de capturar el tráfico de red, extraer las características temporales y comunicarse con la placa FPGA mediante UART.
* **`preprocesador.py`**: Script principal que utiliza `pyshark` para la captura pasiva (*Port Mirroring*). Calcula la tasa de paquetes (C1), el índice de variación de IPs de origen (C2) y la entropía de IPs de origen (C3) en ventanas de 1 segundo. También gestiona el envío de las métricas (C1, C2, C3) en formato ASCII hacia la FPGA y recibe la señal de `ALERTA_DDOS`.

### `Hardware_FPGA/`
Contiene los archivos de descripción de hardware (Verilog) utilizados para programar la FPGA Nexys Video a través de Vivado.
* **`nahid_core.v`**: Implementación lógica del algoritmo *Neighbor Histogram-based DDoS Attack Detection* (NaHiD).
* **`uart_rx.v` / `uart_tx.v`**: Módulos de recepción y transmisión serial para la comunicación a 9600 bps con el PC.
* **`parser_ascii.v`**: Módulo que convierte los datos estadísticos recibidos en ASCII a valores enteros procesables por el algoritmo.
* **`top_module.v`**: Archivo de nivel superior (Top Level) que interconecta todos los submódulos.
* **`nexys_video_constraints.xdc`**: Archivo de restricciones que mapea los puertos físicos (Pines RX/TX, LEDs de alerta y reloj).

### `Entorno_Industrial/`
Archivos relacionados con el entorno industrial simulado bajo el modelo Purdue.
* **`plc_arduino_opta.ino`**: Código cargado en el PLC Arduino Opta para la lectura del sensor de temperatura RTD (PT100) y la habilitación del servidor Modbus/TCP en el puerto 502.
* **`maestro_modbus.py`**: Script en Python (utilizando `pymodbus` con `ModbusDeviceContext` en su versión 3.11.3) para simular el tráfico legítimo (*polling* determinista cada 1 ms).
* **`scripts_ataque_hping3.sh`**: Comandos de Bash utilizados en la máquina Kali Linux para generar las inundaciones SYN, UDP e ICMP (*flood* y *rand-source*).

### `Resultados/`
Archivos de datos (CSV y JSON) generados durante la evaluación del sistema, utilizados para calcular latencia, precisión y la matriz de confusión.
* **`perfil_normal.json`**: Archivo base con los promedios históricos de tráfico (C1n, C2n, C3n) y el umbral de sensibilidad (`th`).
* **`vectores_capturados.csv`**: Registro segundo a segundo de las métricas extraídas durante las pruebas (Normal vs Ataque).
* **`metricas.csv`**: Log automático de evaluación de desempeño (Verdaderos Positivos, Falsos Positivos, Falsos Negativos, Precisión y FNR).
* **`historial_ataques.csv`**: Registro del timestamp exacto y la latencia calculada por cada evento de detección.
* **`archivo_impacto.csv`**: Datos del RTT (Round Trip Time) de los paquetes Modbus para evidenciar la caída de disponibilidad a 0 rps durante el ataque.

## 🚀 Requisitos de Ejecución
* Placa FPGA Digilent Nexys Video (Artix-7).
* Xilinx Vivado (Para síntesis y carga del bitstream).
* Python 3.10+ con las librerías: `pyshark`, `pyserial`.
* Wireshark / TShark instalado en el sistema operativo anfitrión.

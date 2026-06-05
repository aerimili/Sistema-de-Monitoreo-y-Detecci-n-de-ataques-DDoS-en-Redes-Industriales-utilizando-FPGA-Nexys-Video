import time
import random
import serial
import threading
import collections

# Configuración del puerto COM
ser = serial.Serial("COM3", 9600, timeout=0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()

# Hilo seguro para almacenar "paquetes simulados" (direcciones IP de origen)
buffer_paquetes = []
lock_buffer = threading.Lock()

ataque_activo = False

def enviar_valor(modo, identificador, valor):
    msg = f"{modo}{identificador}{int(valor)}\n"
    ser.write(msg.encode("ascii"))

def conexionFPGA(c1, c2, c3, modo="D"):
    enviar_valor(modo, "A", c1)
    enviar_valor(modo, "B", c2)
    enviar_valor(modo, "C", c3)

def escuchar_fpga():
    buffer = ""
    while True:
        try:
            if ser.in_waiting > 0:
                dato = ser.read(ser.in_waiting).decode("ascii", errors="ignore")
                buffer += dato
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    if linea:
                        # Marcamos la alerta con un timestamp preciso para debuggear el desfase
                        print(f"[{time.strftime('%H:%M:%S')}] [RX FPGA] >>> {linea} <<<")
            time.sleep(0.01)
        except Exception as e:
            print("Error leyendo FPGA:", e)
            time.sleep(1)

def entropia(lista_ip):
    if not lista_ip:
        return 0
    conteo = collections.Counter(lista_ip)
    total = len(lista_ip)
    ent = 0
    for ip in conteo:
        p = conteo[ip] / total
        ent -= p * (p.__float__().as_integer_ratio()[1]) # Aproximación rápida para simulación
    return ent

# ==============================================================================
# PROCESO 1: SIMULADOR DE TRÁFICO INDUSTRIAL (Generador de Eventos de Red)
# ==============================================================================
def generador_trafico_red():
    global ataque_activo
    print("[HILO RED] Generador de tráfico iniciado...")
    
    while True:
        if ataque_activo:
            # En DDoS entran MILES de paquetes por segundo de IPs aleatorias
            # Simulamos ráfagas rápidas inyectando ruidos al buffer instantáneamente
            ip_atacante = f"192.168.40.{random.randint(100, 254)}"
            with lock_buffer:
                buffer_paquetes.append(ip_atacante)
            time.sleep(0.002) # Frecuencia masiva de ataque (500 paquetes/seg)
        else:
            # Tráfico Modbus legítimo: Determinista (1 petición/respuesta constante)
            with lock_buffer:
                buffer_paquetes.append("192.168.40.70") # PC Master Modbus fijo
            time.sleep(0.05) # Frecuencia normal controlada

# ==============================================================================
# PROCESO 2: PREPROCESADOR POR VENTANAS DE TIEMPO (Idéntico al código Real)
# ==============================================================================
def preprocesador_ventanas():
    global ataque_activo
    print("[HILO VENTANAS] Procesador de ventanas de 1s activo...")
    
    inicio_ventana = time.time()
    
    while True:
        tiempo_actual = time.time()
        
        # Monitoreo estricto del reloj del sistema (Ventana de 1 segundo absoluto)
        if tiempo_actual - inicio_ventana >= 1.0:
            # Secuestramos el buffer actual de paquetes para procesarlo de forma aislada
            with lock_buffer:
                ventana_actual = list(buffer_paquetes)
                buffer_paquetes.clear()
            
            inicio_ventana = tiempo_actual # Reiniciamos la ventana de inmediato
            
            total_paquetes = len(ventana_actual)
            
            if total_paquetes > 0:
                c1 = total_paquetes
                ip_unicas = len(set(ventana_actual))
                
                # Fórmulas exactas de tu informe de tesis
                c2 = int((ip_unicas / total_paquetes) * 100)
                c3 = int(entropia(ventana_actual) * 100)
                
                estado_str = "[ATAQUE]" if ataque_activo else "[NORMAL]"
                print(f"\n[{time.strftime('%H:%M:%S')}] {estado_str} Ventana cerrada. {total_paquetes} paq procesados.")
                print(f" -> Vectores calculados: C1={c1}, C2={c2}, C3={c3}")
                
                # Enviar directo a la FPGA sin interrupción
                conexionFPGA(c1, c2, c3, modo="D")
            else:
                print(f"\n[{time.strftime('%H:%M:%S')}] Ventana vacía. Sin tráfico.")

        time.sleep(0.01) # Alivia la carga de la CPU en el bucle de reloj

# ==============================================================================
# PROCESO 3: ORQUESTADOR DEL ESCENARIO (Controlador del Ataque)
# ==============================================================================
def orquestador_escenario():
    global ataque_activo
    time.sleep(5) # Espera inicial
    
    while True:
        # 10 segundos de calma normal
        ataque_activo = False
        time.sleep(10)
        
        # 3 segundos de tormenta DDoS masiva
        print("\n!!! GATILLANDO ATAQUE DDOS EN LA RED INDUSTRIAL SIMULADA !!!")
        ataque_activo = True
        time.sleep(3)
        print("\n--- ATAQUE FINALIZADO. RETORNANDO RED A OPERACIÓN NORMAL ---")

# ==============================================================================
# MAIN
# ==============================================================================
if __name__ == "__main__":
    time.sleep(1)
    # Inicialización manual del perfil estático base (Modbus estable)
    # Ponemos valores coherentes con la tasa de refresco del Modbus (20 paq/seg)
    conexionFPGA(20, 5, 0, modo="N") 
    print("Perfil de Calibración Normal inyectado. Iniciando entorno asíncrono...\n")
    time.sleep(1)

    # Lanzamos los hilos independientes concurrentes
    threading.Thread(target=escuchar_fpga, daemon=True).start()
    threading.Thread(target=generador_trafico_red, daemon=True).start()
    threading.Thread(target=orquestador_escenario, daemon=True).start()
    
    # El hilo principal ejecuta el despachador de ventanas de tiempo
    preprocesador_ventanas()
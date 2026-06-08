import time
import random
import serial
import threading
import collections
import math
import os

interface = 'Ethernet'
filter = 'tcp port 502'

# Configuración del puerto COM
ser = serial.Serial("COM3", 9600, timeout=0.1)
ser.reset_input_buffer()
ser.reset_output_buffer()

buffer_paquetes = []
lock_buffer = threading.Lock()

# Variables globales para métricas de evaluación
ataque_activo = False
t_evento = 0.0
alerta_detectada_en_este_ataque = False

TP = 0
FP = 0
FN = 0

def imprimir_metricas():
    precision = (TP / (TP + FP)) if (TP + FP) > 0 else 0.0
    fnr = (FN / (FN + TP)) if (FN + TP) > 0 else 0.0
    print(f" [MÉTRICAS] Precisión: {precision:.4f} | FNR: {fnr:.4f}")

def enviar_valor(modo, identificador, valor):
    msg = f"{modo}{identificador}{int(valor)}\n"
    ser.write(msg.encode("ascii"))

def conexionFPGA(c1, c2, c3, th=None, modo="D"):
    enviar_valor(modo, "A", c1)
    time.sleep(0.01)
    
    enviar_valor(modo, "B", c2)
    time.sleep(0.01)
    
    enviar_valor(modo, "C", c3)
    time.sleep(0.01)
    
    if th is not None:
        enviar_valor(modo, "T", th)
        time.sleep(0.01)

def escuchar_fpga():
    global TP, FP, alerta_detectada_en_este_ataque
    buffer = ""
    archivo_historial = "historial_ataques.csv"
    
    if not os.path.exists(archivo_historial):
        with open(archivo_historial, "w") as f:
            f.write("Timestamp_Epoch,Fecha_Hora,Mensaje,Latencia_Segundos\n")

    while True:
        try:
            if ser.in_waiting > 0:
                t_llegada = time.time()
                fecha_hora = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t_llegada))

                dato = ser.read(ser.in_waiting).decode("ascii", errors="ignore")
                buffer += dato
                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()
                    
                    if linea:
                        if linea == "ALERTA_DDOS":
                            latencia = 0.0
                            
                            if ataque_activo:
                                TP += 1
                                if not alerta_detectada_en_este_ataque:
                                    latencia = t_llegada - t_evento
                                    alerta_detectada_en_este_ataque = True
                                    print(f"{linea} (Verdadero Positivo)")
                                    print(f"Latencia de detección: {latencia:.4f} s")
                                else:
                                    print(f"{linea} (Verdadero Positivo Continuo)")
                            else:
                                FP += 1
                                print(f"{linea} (¡FALSO POSITIVO!)")
                            
                            imprimir_metricas()
                            
                            with open(archivo_historial, "a") as f:
                                f.write(f"{t_llegada:.4f},{fecha_hora},{linea},{latencia:.4f}\n")
                                
            time.sleep(0.01)
        except Exception:
            time.sleep(1)

def entropia(lista_ip):
    if not lista_ip:
        return 0
    conteo = collections.Counter(lista_ip)
    total = len(lista_ip)
    ent = 0
    for ip in conteo:
        p = conteo[ip] / total
        ent -= p * math.log2(p) 
    return ent

def generador_trafico_red():
    global ataque_activo
    
    while True:
        if ataque_activo:
            ip_atacante = f"192.168.40.{random.randint(100, 254)}"
            with lock_buffer:
                buffer_paquetes.append(ip_atacante)
            time.sleep(0.0015) 
        else:
            ip_normal = random.choice(["192.168.40.70", "192.168.40.20"])
            with lock_buffer:
                buffer_paquetes.append(ip_normal)
            time.sleep(0.0074) 

def preprocesador_ventanas():
    inicio_ventana = time.time()
    
    while True:
        tiempo_actual = time.time()
        
        if tiempo_actual - inicio_ventana >= 1.0:
            with lock_buffer:
                ventana_actual = list(buffer_paquetes)
                buffer_paquetes.clear()
            
            inicio_ventana = tiempo_actual 
            total_paquetes = len(ventana_actual)
            
            if total_paquetes > 0:
                c1 = total_paquetes
                ip_unicas = len(set(ventana_actual))
                
                c2 = int((ip_unicas / total_paquetes) * 100)
                c3 = int(entropia(ventana_actual) * 100)
                
                conexionFPGA(c1, c2, c3, modo="D")
                
        time.sleep(0.01) 

def orquestador_escenario():
    global ataque_activo, t_evento, alerta_detectada_en_este_ataque, FN
    time.sleep(5) 
    
    while True:
        ataque_activo = False
        time.sleep(10)
        
        ataque_activo = True
        t_evento = time.time()
        alerta_detectada_en_este_ataque = False
        time.sleep(3)
        
        if not alerta_detectada_en_este_ataque:
            FN += 1
            print(f"\n[{time.strftime('%H:%M:%S')}] [!] El ataque finalizó sin respuesta de la FPGA -> Falso Negativo (FN)")
            imprimir_metricas()

if __name__ == "__main__":
    time.sleep(1)
    
    conexionFPGA(131, 1, 99, th=79, modo="N") 
    time.sleep(2)

    threading.Thread(target=escuchar_fpga, daemon=True).start()
    threading.Thread(target=generador_trafico_red, daemon=True).start()
    threading.Thread(target=orquestador_escenario, daemon=True).start()
    
    preprocesador_ventanas()
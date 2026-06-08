import pyshark
import math
import time
import collections
import asyncio
import serial
import json
import threading
import os

interface = 'Ethernet'
filter = 'tcp port 502'

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

ser = serial.Serial('COM4', 9600, timeout=0.1)

# =========================================================
# VARIABLES GLOBALES PARA MÉTRICAS
# =========================================================
# Pon aquí la dirección MAC real de tu máquina Kali Linux (en minúsculas)
MAC_KALI = "00:0c:29:xx:xx:xx" 

estado_ataque_real = False
t_evento = 0.0
alerta_detectada_en_este_ataque = False
ultimo_paquete_kali = 0.0

TP = 0
FP = 0
FN = 0

with open("perfil_normal.json", "r") as i:
    perfil_normal = json.load(i)

C1n = perfil_normal["C1n"]
C2n = perfil_normal["C2n"]
C3n = perfil_normal["C3n"]
th = perfil_normal["th"]

print(f"Perfil cargado: C1={C1n}, C2={C2n}, C3={C3n}, th={th}")

def imprimir_metricas():
    precision = (TP / (TP + FP)) if (TP + FP) > 0 else 0.0
    fnr = (FN / (FN + TP)) if (FN + TP) > 0 else 0.0
    print(f"[MÉTRICAS] TP:{TP} | FP:{FP} | FN:{FN} | Precisión:{precision:.4f} | FNR:{fnr:.4f}")

def enviar_valor(modo, identificador, valor):
    msg = f"{modo}{identificador}{int(valor)}\n"
    ser.write(msg.encode('ascii'))

def conexionFPGA(c1, c2, c3, modo="D", th=None):
    if modo == "N":
        print("Enviando perfil normal...")
        if th is not None:
            enviar_valor(modo, "T", th)
            
    enviar_valor(modo, "A", c1)
    enviar_valor(modo, "B", c2)
    enviar_valor(modo, "C", c3)

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
                        print(f"[RX FPGA] {linea}")
                        
                        if linea == "ALERTA_DDOS":
                            latencia = 0.0
                            
                            # Validamos contra el estado automático
                            if estado_ataque_real:
                                TP += 1
                                if not alerta_detectada_en_este_ataque:
                                    latencia = t_llegada - t_evento
                                    alerta_detectada_en_este_ataque = True
                            else:
                                FP += 1
                                
                            imprimir_metricas()
                            
                            with open(archivo_historial, "a") as f:
                                f.write(f"{t_llegada:.4f},{fecha_hora},{linea},{latencia:.4f}\n")

            time.sleep(0.05)
        except Exception as e:
            time.sleep(1)

time.sleep(2)
conexionFPGA(C1n, C2n, C3n, modo="N", th=th)

def entropia(lista_ip):
    if not lista_ip: return 0
    conteo = collections.Counter(lista_ip)
    total = len(lista_ip)
    ent = 0
    for ip in conteo:
        p = conteo[ip] / total
        ent -= p * math.log2(p)
    return ent

def preprocesador():
    global estado_ataque_real, t_evento, alerta_detectada_en_este_ataque, ultimo_paquete_kali, FN
    print(f"Iniciando captura en {interface}...")

    capture = pyshark.LiveCapture(interface=interface,bpf_filter=filter,tshark_path=r"D:\Program Files (x86)\Wireshark\tshark.exe")

    ventana_ip = []
    inicio_ventana = time.time()

    try:
        for paquete in capture.sniff_continuously():
            tiempo_actual = time.time()

            # -------------------------------------------------------------
            # LÓGICA DE PRECISIÓN MILIMÉTRICA: Detección Física por MAC
            # -------------------------------------------------------------
            try:
                mac_origen = paquete.eth.src
                if mac_origen == MAC_KALI:
                    ultimo_paquete_kali = tiempo_actual
                    
                    # Si recibimos un paquete de Kali y no estábamos en ataque, ¡empezó el ataque!
                    if not estado_ataque_real:
                        estado_ataque_real = True
                        alerta_detectada_en_este_ataque = False
                        # Usamos sniff_timestamp, que es la hora EXACTA en que la tarjeta de red vio el paquete
                        t_evento = float(paquete.sniff_timestamp) 
                        print(f"\n[!] INICIO DE ATAQUE DETECTADO FÍSICAMENTE EN LA RED: {time.strftime('%H:%M:%S', time.localtime(t_evento))}")
            except AttributeError:
                pass # Paquetes sin capa Ethernet

            # Evaluador de FIN de ataque: Si pasaron 2 segundos sin que Kali mande nada, el ataque acabó
            if estado_ataque_real and (tiempo_actual - ultimo_paquete_kali > 2.0):
                estado_ataque_real = False
                print(f"\n[!] FIN DE ATAQUE DETECTADO. Retornando a normalidad.")
                if not alerta_detectada_en_este_ataque:
                    FN += 1
                    print(" -> [!] La FPGA no detectó este ataque (Falso Negativo).")
                    imprimir_metricas()

            # -------------------------------------------------------------
            # LÓGICA ORIGINAL DE VENTANAS PARA LA FPGA
            # -------------------------------------------------------------
            try:
                src_ip = paquete.ip.src
                ventana_ip.append(src_ip)
            except AttributeError:
                pass

            if tiempo_actual - inicio_ventana >= 1.0:
                total_paquetes = len(ventana_ip)

                if total_paquetes > 0:
                    c1 = total_paquetes
                    ip_unicas = len(set(ventana_ip))
                    c2 = int((ip_unicas / total_paquetes) * 100)
                    c3 = int(entropia(ventana_ip) * 100)

                    print(f"[vector] C1={c1}, C2={c2}, C3={c3}")
                    conexionFPGA(c1, c2, c3, modo="D")

                ventana_ip = []
                inicio_ventana = tiempo_actual

    except KeyboardInterrupt:
        print("\nCaptura detenida manualmente.")

if __name__ == "__main__":
    hilo_rx = threading.Thread(target=escuchar_fpga, daemon=True)
    hilo_rx.start()
    
    try:
        preprocesador()
    except KeyboardInterrupt:
        print("\n[SISTEMA] Cerrando proceso de forma segura.")
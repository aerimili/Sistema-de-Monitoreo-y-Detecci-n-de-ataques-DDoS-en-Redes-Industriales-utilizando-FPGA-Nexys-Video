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
filter = 'tcp port 502 or udp or icmp'

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

ser = serial.Serial('COM4', 9600, timeout=0.1)

mac_kali = "08:00:27:ad:25:87" 
ip_maestro = "192.168.40.70"
ip_esclavo = "192.168.40.20"  

estado_ataque_real = False
t_evento = 0
alerta_detectada_en_este_ataque = False
ultimo_paquete_kali = 0
ultimo_modbus = time.time()
estado_modbus = 1

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

tipo_ataque = "UDP_flood" #agregar según el ataque simulado (solo para guardar en archivos csv)
ultima_alerta = 0

if not os.path.exists("vectores_capturados.csv"):
    with open("vectores_capturados.csv", "w") as f:
        f.write("Timestamp,Estado,TipoAtaque,C1,C2,C3,FPGA_Alerta\n")

if not os.path.exists("metricas.csv"):
    with open("metricas.csv", "w") as f:
        f.write("Timestamp,TP,FP,FN,Precision,FNR\n")

if not os.path.exists("historial_ataques.csv"):
    with open("historial_ataques.csv", "w") as f:
        f.write("Timestamp_Epoch,Fecha_Hora,TipoAtaque,Mensaje,Latencia_segundos\n")

if not os.path.exists("archivo_impacto.csv"):
    with open("archivo_impacto.csv", "w") as f:
        f.write("Timestamp,RTT,Ataque\n")

def guardar_metricas():
    precision = (TP / (TP + FP)) if (TP + FP) > 0 else 0.0
    fnr = (FN / (FN + TP)) if (FN + TP) > 0 else 0.0

    with open("metricas.csv", "a") as f:
        f.write(f"{time.time()},"f"{TP},"f"{FP},"f"{FN},"f"{precision:.4f},"f"{fnr:.4f}\n")

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
    global TP, FP, alerta_detectada_en_este_ataque, ultima_alerta
    buffer = ""
    
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
                        print(f"FPGA: {linea}")
                        
                        if linea == "ALERTA_DDOS":
                            ultima_alerta = 1
                            latencia = 0.0
                            
                            if estado_ataque_real:
                                TP += 1
                                if not alerta_detectada_en_este_ataque:
                                    latencia = t_llegada - t_evento
                                    alerta_detectada_en_este_ataque = True
                            else:
                                FP += 1
                                
                            guardar_metricas()
                            
                            with open("historial_ataques.csv", "a") as f:
                                f.write(
                                    f"{t_llegada:.4f},"f"{fecha_hora},"f"{tipo_ataque if estado_ataque_real else 'NONE'},"f"{linea},"f"{latencia:.6f}\n")

            time.sleep(0.05)
        except Exception as e:
            print(f"Error en rx: {e}")
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
    global estado_ataque_real, t_evento, alerta_detectada_en_este_ataque, ultimo_paquete_kali, FN, ultima_alerta
    print(f"Iniciando captura en {interface}...")

    capture = pyshark.LiveCapture(interface=interface,bpf_filter=filter,tshark_path=r"D:\Program Files (x86)\Wireshark\tshark.exe")
    tiempo_ultimo_request = 0
    ventana_ip = []
    inicio_ventana = time.time()

    try:
        for paquete in capture.sniff_continuously():
            tiempo_actual = time.time()


            try:
                mac_origen = paquete.eth.src
                if mac_origen == mac_kali:
                    ultimo_paquete_kali = tiempo_actual
                    
                    if not estado_ataque_real:
                        estado_ataque_real = True
                        alerta_detectada_en_este_ataque = False
             
                        t_evento = float(paquete.sniff_timestamp) 
            except AttributeError:
                pass

            if estado_ataque_real and (tiempo_actual - ultimo_paquete_kali > 2.0):
                estado_ataque_real = False
                if not alerta_detectada_en_este_ataque:
                    FN += 1
                    guardar_metricas()

            try:    
                src_ip = paquete.ip.src
                dst_ip = paquete.ip.dst

                if src_ip == ip_maestro and dst_ip == ip_esclavo:
                    tiempo_ultimo_request = float(paquete.sniff_timestamp)

                elif src_ip == ip_esclavo and dst_ip == ip_maestro:
                    if tiempo_ultimo_request > 0:
                        rtt = float(paquete.sniff_timestamp) - tiempo_ultimo_request
                        with open("archivo_impacto.csv", "a") as f:
                            f.write(f"{tiempo_actual:.4f}, {rtt:.6f},{estado_ataque_real}\n")
                        tiempo_ultimo_request = 0.0
            except AttributeError:
                pass

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

                    print(f"Vector: C1={c1}, C2={c2}, C3={c3}")
                    conexionFPGA(c1, c2, c3, modo="D")

                    estado = "ATAQUE" if estado_ataque_real else "NORMAL"
                    
                    with open("vectores_capturados.csv", "a") as f:
                        f.write(f"{time.time()},"f"{estado},"f"{tipo_ataque if estado_ataque_real else 'NONE'},"f"{c1},"f"{c2},"f"{c3},"f"{ultima_alerta}\n")

                    
                    ultima_alerta = 0    

                ventana_ip = []
                inicio_ventana = tiempo_actual

    except KeyboardInterrupt:
        print("\nFin captura.")

if __name__ == "__main__":
    hilo_rx = threading.Thread(target=escuchar_fpga, daemon=True)
    hilo_rx.start()
    
    try:
        preprocesador()
    except KeyboardInterrupt:
        print("\nCerrando proceso.")
        guardar_metricas()
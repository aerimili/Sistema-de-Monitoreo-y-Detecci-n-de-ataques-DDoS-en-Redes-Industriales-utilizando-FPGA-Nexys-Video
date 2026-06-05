import pyshark
import math
import time
import collections
import serial
import json
import threading

interface = 'Ethernet'
filter = 'tcp port 502'

ser = serial.Serial('COM4', 9600, timeout=0.1)

buffer_ips = []
lock_buffer = threading.Lock()

estado_ataque_real = False
timestamp_inicio_ataque = 0.0
alerta_detectada_en_este_ataque = False

TP = 0
FP = 0
FN = 0
TN = 0

with open("perfil_normal.json", "r") as i:
    perfil_normal = json.load(i)

C1n = perfil_normal["C1n"]
C2n = perfil_normal["C2n"]
C3n = perfil_normal["C3n"]
th = perfil_normal["th"]

print("Perfil cargado:", C1n, C2n, C3n, th)


def guardar_reporte():
    precision = (TP / (TP + FP)) if (TP + FP) > 0 else 0.0
    fnr = (FN / (FN + TP)) if (FN + TP) > 0 else 0.0
    
    reporte = {
        "TP": TP, "FP": FP, "FN": FN, "TN": TN,
        "Precision": round(precision, 4),
        "FNR": round(fnr, 4)
    }
    with open("reporte_desempeno.json", "w") as f:
        json.dump(reporte, f, indent=4)


def enviar_valor(modo, identificador, valor):
    msg = f"{modo}{identificador}{int(valor)}\n"
    ser.write(msg.encode('ascii'))
    print(f"[TX] {msg.strip()}")


def conexionFPGA(c1, c2, c3, modo="D", th=None):
    if modo == "N":
        print("Enviando perfil normal")
        if th is not None:
            enviar_valor("N", "T", th)
    else:
        print("Enviando datos")

    enviar_valor(modo, "A", c1)
    enviar_valor(modo, "B", c2)
    enviar_valor(modo, "C", c3)


def escuchar_fpga():
    global TP, FP, alerta_detectada_en_este_ataque
    buffer = ""

    while True:
        try:
            if ser.in_waiting > 0:
                t_alerta = time.time()
                dato = ser.read(ser.in_waiting).decode("ascii", errors="ignore")
                buffer += dato

                while "\n" in buffer:
                    linea, buffer = buffer.split("\n", 1)
                    linea = linea.strip()

                    if linea:
                        print(f"[RX FPGA] {linea}")
                        
                        if linea == "ALERTA_DDOS":
                            latencia = 0.0
                            if estado_ataque_real:
                                TP += 1
                                if not alerta_detectada_en_este_ataque:
                                    latencia = t_alerta - timestamp_inicio_ataque
                                    print(f"[METRICA] Latencia: {latencia:.4f} s")
                                    alerta_detectada_en_este_ataque = True
                            else:
                                FP += 1
                                print("[METRICA] Falso Positivo detectado")
                                
                            with open("registro_alertas.csv", "a") as f:
                                f.write(f"{t_alerta},{linea},{latencia:.4f}\n")
                                
                            guardar_reporte()

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
        ent -= p * math.log2(p)

    return ent


def captura_pyshark():
    print(f"Iniciando captura en {interface}...")
    capture = pyshark.LiveCapture(
        interface=interface,
        bpf_filter=filter,
        tshark_path=r"D:\Program Files (x86)\Wireshark\tshark.exe"
    )

    try:
        for paquete in capture.sniff_continuously():
            try:
                src_ip = paquete.ip.src

                with lock_buffer:
                     buffer_ips.append(src_ip)
            except AttributeError:
                continue
    
    except Exception as e:
         print("Error en el bucle de captura Pyshark:", e)


def preprocesador():
    global TN
    inicio_ventana = time.time()

    while True:
        tiempo_actual = time.time()   

        if tiempo_actual - inicio_ventana >= 1.0:
                
            with lock_buffer:
                ventana_actual = list(buffer_ips)
                buffer_ips.clear()

            inicio_ventana = tiempo_actual
            total_paquetes = len(ventana_actual)

            if total_paquetes > 0:
                c1 = total_paquetes
                ip_unicas = len(set(ventana_actual))
                c2 = int((ip_unicas / total_paquetes) * 100)
                c3 = int(entropia(ventana_actual) * 100)

                if not estado_ataque_real:
                    TN += 1

                print(f"[vector] C1={c1}, C2={c2}, C3={c3}")

                conexionFPGA(c1, c2, c3, modo="D")

                with open("datos_normales.csv", "a") as f:
                    f.write(f"{time.time()},"f"{c1},"f"{c2},"f"{c3}\n")

        time.sleep(0.005)


def controlador_manual():
    global estado_ataque_real, timestamp_inicio_ataque, FN, alerta_detectada_en_este_ataque
    print("\n--- CONTROLADOR INTERNO DE MARCAS ACTIVADO ---")
    print("ENTER para iniciar ataque / ENTER para terminar\n")
    
    while True:
        input()
        if not estado_ataque_real:
            estado_ataque_real = True
            timestamp_inicio_ataque = time.time()
            alerta_detectada_en_este_ataque = False
            print(f">>> EVENTO REGISTRADO: Inicio ataque ({timestamp_inicio_ataque})")
        else:
            estado_ataque_real = False
            print(">>> EVENTO REGISTRADO: Fin ataque")
            if not alerta_detectada_en_este_ataque:
                FN += 1
                print("[METRICA] Falso Negativo detectado")
                guardar_reporte()


if __name__ == "__main__":

    time.sleep(1)
    conexionFPGA(C1n, C2n, C3n, modo="N", th=th)
    print("Perfil normal cargado en FPGA")
    time.sleep(2)

    threading.Thread(target=escuchar_fpga, daemon=True).start()
    threading.Thread(target=captura_pyshark, daemon=True).start()
    threading.Thread(target=controlador_manual, daemon=True).start()

    preprocesador()
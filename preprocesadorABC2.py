import pyshark
import math
import time
import collections
import asyncio
import serial
import json


interface = 'Ethernet'
filter = 'tcp port 502'

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

ser = serial.Serial('COM4', 9600, timeout=0.1)

ser.reset_input_buffer()
ser.reset_output_buffer()

# =========================
# métricas
# =========================
TP = 0
FP = 0
FN = 0

latencias = []

# =========================
# cargar perfil normal
# =========================
with open("perfil_normal.json", "r") as i:
    perfil_normal = json.load(i)

C1n = perfil_normal["C1n"]
C2n = perfil_normal["C2n"]
C3n = perfil_normal["C3n"]

print("Perfil cargado:", C1n, C2n, C3n)


# =========================
# UART FPGA
# =========================
def enviar_valor(modo, ident, valor):
    msg = f"{modo}{ident}{int(valor)}\n"
    ser.write(msg.encode('ascii'))
    print(f"[TX] {msg.strip()}")


def conexionFPGA(c1, c2, c3, modo="D"):

    if modo == "N":
        print("Enviando perfil normal")
    else:
        print("Enviando datos")

    enviar_valor(modo, "A", c1)
    time.sleep(0.01)

    enviar_valor(modo, "B", c2)
    time.sleep(0.01)

    enviar_valor(modo, "C", c3)
    time.sleep(0.01)


# =========================
# leer FPGA
# =========================
def revisar_mensaje():

    while ser.in_waiting:

        raw = ser.readline()

        msg = raw.decode(
            errors="ignore"
        ).strip()

        if msg:
            print("[FPGA]", msg)

            if msg == "ALERTA_DDOS":
                return True

    return False


# =========================
# entropía
# =========================
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


# =========================
# enviar perfil normal
# =========================
time.sleep(2)

conexionFPGA(
    C1n,
    C2n,
    C3n,
    modo="N"
)


# =========================
# captura
# =========================
def preprocesador():

    global TP
    global FP
    global FN
    global latencias

    print(f"Iniciando captura en {interface}...")

    capture = pyshark.LiveCapture(
        interface=interface,
        bpf_filter=filter,
        tshark_path=r"D:\Program Files (x86)\Wireshark\tshark.exe"
    )

    ventana_ip = []

    inicio_ventana = time.time()

    try:
        for paquete in capture.sniff_continuously():

            tiempo_actual = time.time()

            try:
                src_ip = paquete.ip.src
                ventana_ip.append(src_ip)

            except AttributeError:
                continue

            # cada 1 segundo
            if tiempo_actual - inicio_ventana >= 1.0:

                total_paquetes = len(ventana_ip)

                if total_paquetes > 0:

                    c1 = total_paquetes

                    ip_unicas = len(set(ventana_ip))

                    c2 = int(
                        (ip_unicas / total_paquetes) * 100
                    )

                    c3 = int(
                        entropia(ventana_ip) * 100
                    )

                    print(
                        f"[vector] "
                        f"C1={c1} "
                        f"C2={c2} "
                        f"C3={c3}"
                    )

                    # =====================
                    # enviar vector
                    # =====================
                    t0 = time.time()

                    conexionFPGA(
                        c1,
                        c2,
                        c3
                    )

                    alerta = revisar_mensaje()

                    # =====================
                    # lógica detección
                    # =====================
                    ataque_real = (
                        c1 > C1n * 2
                    )

                    if alerta:

                        lat_ms = (
                            time.time() - t0
                        ) * 1000

                        latencias.append(lat_ms)

                        print(
                            f"Latencia: "
                            f"{lat_ms:.2f} ms"
                        )

                        if ataque_real:
                            TP += 1
                        else:
                            FP += 1

                    else:

                        if ataque_real:
                            FN += 1

                    # =====================
                    # métricas
                    # =====================
                    precision = 0

                    if TP + FP > 0:
                        precision = (
                            TP / (TP + FP)
                        ) * 100

                    fnr = 0

                    if TP + FN > 0:
                        fnr = (
                            FN / (TP + FN)
                        ) * 100

                    lat_prom = 0

                    if latencias:
                        lat_prom = (
                            sum(latencias)
                            / len(latencias)
                        )

                    print(
                        f"Precision: "
                        f"{precision:.2f}%"
                    )

                    print(
                        f"Falsos negativos: "
                        f"{fnr:.2f}%"
                    )

                    print(
                        f"Latencia promedio: "
                        f"{lat_prom:.2f} ms"
                    )

                ventana_ip = []

                inicio_ventana = tiempo_actual

    except KeyboardInterrupt:
        print("Captura detenida")


preprocesador()
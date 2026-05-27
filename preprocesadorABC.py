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

ser = serial.Serial('COM4', 9600)


with open("perfil_normal.json", "r") as i:
    perfil_normal = json.load(i)

C1n = perfil_normal["C1n"]
C2n = perfil_normal["C2n"]
C3n = perfil_normal["C3n"]

print("Perfil cargado:", C1n, C2n, C3n)


def enviar_valor(modo, identificador, valor):

    msg = f"{modo}{identificador}{int(valor)}\n"

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


time.sleep(2)
conexionFPGA(C1n, C2n, C3n, modo="N")

 
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


def preprocesador():

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

            # Cada 1 segundo
            if tiempo_actual - inicio_ventana >= 1.0:

                total_paquetes = len(ventana_ip)

                if total_paquetes > 0:

                    c1 = total_paquetes
                    ip_unicas = len(set(ventana_ip))
                    c2 = int((ip_unicas / total_paquetes) * 100)
                    c3 = int(entropia(ventana_ip) * 100)

                    print(f"[vector] C1={c1}, C2={c2}, C3={c3}")

                    
                    conexionFPGA(c1, c2, c3, modo="D")

                    
                    with open("datos_ataqueTCPSYN.csv", "a") as f:
                        f.write(f"{time.time()},{c1},{c2},{c3}\n")

                ventana_ip = []
                inicio_ventana = tiempo_actual

    except KeyboardInterrupt:
        print("Captura detenida")


if __name__ == "__main__":
    preprocesador()
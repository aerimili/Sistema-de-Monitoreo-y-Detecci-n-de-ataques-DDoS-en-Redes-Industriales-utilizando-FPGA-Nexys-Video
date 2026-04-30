import random
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
th = perfil_normal["th"]

print("Perfil cargado:", C1n, C2n, C3n, th)

time.sleep(2)

data_perfil = f"N,{C1n},{C2n},{C3n},{th}\n"
ser.write(data_perfil.encode())

print("Perfil enviado:", data_perfil)


def entropia(lista_ip):
  if not lista_ip:
    return 0
  conteo = collections.Counter(lista_ip)
  total = len(lista_ip)
  entropia = 0
  for ip in conteo:
    probabilidad = conteo[ip] / total
    entropia -= probabilidad * math.log2(probabilidad)
  return entropia


def preprocesador():
  print (f"Iniciando captura en {interface}...")
  capture = pyshark.LiveCapture(
    interface=interface,
    bpf_filter=filter,
    tshark_path=r"C:\Program Files\Wireshark\tshark.exe")

  ventana_ip = []
  inicio_ventana = time.time()
  ultimo_ataque = time.time()

  try:
    for paquete in capture.sniff_continuously():
      tiempo_actual = time.time()

      try:
        src_ip = paquete.ip.src
        ventana_ip.append(src_ip)
      except AttributeError:
        continue

      # cada 1 segundo → calcular métricas reales
      if tiempo_actual - inicio_ventana >= 1.0:
        total_paquetes = len(ventana_ip)

        if total_paquetes > 0:

          # =========================
          # CALCULO NORMAL (REAL)
          # =========================
          c1_real = total_paquetes
          ip_unicas = len(set(ventana_ip))
          c2_real = int((ip_unicas / total_paquetes) * 100)
          c3_real = int(entropia(ventana_ip) * 100)

          # =========================
          # ATAQUE CADA 5 SEGUNDOS
          # =========================
          if tiempo_actual - ultimo_ataque >= 5:

            print("🚨 ATAQUE SIMULADO 🚨")

            c1 = 300   # alto volumen
            c2 = 1000    # muchas IPs
            c3 = 3000  # alta entropía

            ultimo_ataque = tiempo_actual

          else:
            # usar valores reales
            c1 = c1_real
            c2 = c2_real
            c3 = c3_real

          vector = [c1, c2, c3]
          print(f"Vector enviado a FPGA: {vector}")

          data = f"D,{c1},{c2},{c3}\n"
          ser.write(data.encode())

          # guardar SOLO normales
          if c1 == c1_real:
            with open("datos_normales.csv", "a") as f:
              f.write(f"{c1},{c2},{c3}\n")

        ventana_ip = []
        inicio_ventana = tiempo_actual

  except KeyboardInterrupt:
    print("Captura detenida por el usuario")


if __name__ == "__main__":
  preprocesador()
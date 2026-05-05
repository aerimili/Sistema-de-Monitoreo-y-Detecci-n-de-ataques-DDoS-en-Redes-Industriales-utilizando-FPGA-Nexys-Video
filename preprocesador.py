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

def conexionFPGA(c1, c2, c3, modo = "D"):
  if modo == "N":
    data = f"N,{c1},{c2},{c3}\n"
  
  else:
    data = f"D,{c1},{c2},{c3}\n"

  ser.write(data.encode('ascii'))
  print(f"Enviando a FPGA: {data.strip()}")

time.sleep(2)
conexionFPGA(C1n, C2n, C3n, modo = "N")


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
    tshark_path=r"D:\Program Files (x86)\Wireshark\tshark.exe")
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

      if tiempo_actual - inicio_ventana >= 1.0:
        total_paquetes = len(ventana_ip)

        if total_paquetes > 0:

          c1 = total_paquetes #Tasa de paquetes
          ip_unicas = len(set(ventana_ip))
          c2 = int((ip_unicas / total_paquetes)*100) #Índice de variación de IPs de origen
          c3 = int(entropia(ventana_ip)*100) #Entropía


          conexionFPGA(c1, c2, c3, modo = "D")

          with open("datos_normales.csv", "a") as f:
            f.write(f"{time.time()},{c1},{c2},{c3}\n")
        

        ventana_ip = []
        inicio_ventana = tiempo_actual

  except KeyboardInterrupt:
    print("Captura detenida por el usuario")


if __name__ == "__main__":
  preprocesador()


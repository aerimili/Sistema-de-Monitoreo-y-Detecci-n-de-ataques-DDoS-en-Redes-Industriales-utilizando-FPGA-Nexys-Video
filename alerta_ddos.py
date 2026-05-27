import serial
import time
import csv

ser = serial.Serial('COM3', 9600, timeout=1)

with open("alertas_ddos.csv", "a", newline="") as f:

    writer = csv.writer(f)

    while True:

        if ser.in_waiting:

            msg = ser.readline().decode().strip()

            if msg == "ALERTA_DDOS":

                timestamp = time.time()

                print(f"[ALERTA] DDoS detectado -> {timestamp}")

                writer.writerow([timestamp, msg])

                f.flush()
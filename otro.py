import time
import random
import serial

ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

def enviar_valor(id, valor):
    msg = f"{id}{valor}\n"
    ser.write(msg.encode('ascii'))
    print(f"[TX] {msg.strip()}")

while True:

    c1 = random.randint(5, 10)
    c2 = random.randint(20, 30)
    c3 = random.randint(80, 110)

    enviar_valor('A', c1)
    time.sleep(0.2)

    enviar_valor('B', c2)
    time.sleep(0.2)

    enviar_valor('C', c3)
    time.sleep(2)

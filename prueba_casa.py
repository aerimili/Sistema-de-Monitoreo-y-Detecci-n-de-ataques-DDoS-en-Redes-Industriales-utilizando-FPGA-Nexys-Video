import time
import random
import serial


ser = serial.Serial('COM3', 9600, timeout=1)


def enviar_valor(modo, id, valor):
    msg = f"{modo}{id}{int(valor)}\n"
    ser.write(msg.encode("ascii"))
    print(f"Enviando a FPGA: {msg.strip()}")

def enviarFPGA(c1, c2, c3, modo="D"):
    
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

    print("-" * 30)

# =========================
# PERFIL NORMAL
# =========================
C1n = 49
C2n = 3
C3n = 97


time.sleep(2)

# Enviar perfil
enviarFPGA(C1n, C2n, C3n, modo="N")

print("Perfil enviado correctamente\n")



ultimo_ataque = time.time()

while True:

    tiempo_actual = time.time()

    # ATAQUE cada 5s
#    if tiempo_actual - ultimo_ataque >= 5:

#        print("🚨 ATAQUE SIMULADO 🚨")

#        c1 = random.randint(300, 800)
#        c2 = random.randint(80, 90)
#        c3 = random.randint(700, 900)

#        ultimo_ataque = tiempo_actual

#    else:
        # NORMAL
    c1 = random.randint(40, 60)
    c2 = random.randint(1, 5)
    c3 = random.randint(80, 100)

    print(f"Vector generado: {[c1, c2, c3]}")

    # Enviar usando función
    enviarFPGA(c1, c2, c3)

    time.sleep(2)
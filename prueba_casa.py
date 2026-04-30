import time
import random
import serial

# =========================
# CONFIGURACIÓN UART
# =========================
ser = serial.Serial('COM3', 9600, timeout=1)

# =========================
# FUNCIÓN DE ENVÍO
# =========================
def enviarFPGA(c1, c2, c3, modo="D", th=None):
    if modo == "N":
        data = f"N,{c1},{c2},{c3},{th}\n"
    else:
        data = f"D,{c1},{c2},{c3}\n"

    ser.write(data.encode())

    # DEBUG IMPORTANTE
    print(f"[TX] {data.strip()}")
    print(f"[BYTES] {data.encode()}")
    print("-" * 30)


# =========================
# PERFIL NORMAL
# =========================
C1n = 7
C2n = 28
C3n = 92
th  = 879

time.sleep(2)

# Enviar perfil
enviarFPGA(C1n, C2n, C3n, modo="N", th=th)

print("Perfil enviado correctamente\n")


# =========================
# LOOP PRINCIPAL
# =========================
ultimo_ataque = time.time()

while True:

    tiempo_actual = time.time()

    # ATAQUE cada 5s
    if tiempo_actual - ultimo_ataque >= 5:

        print("🚨 ATAQUE SIMULADO 🚨")

        c1 = random.randint(200, 500)
        c2 = random.randint(50, 100)
        c3 = random.randint(200, 400)

        ultimo_ataque = tiempo_actual

    else:
        # NORMAL
        c1 = random.randint(5, 10)
        c2 = random.randint(20, 30)
        c3 = random.randint(80, 110)

    print(f"Vector generado: {[c1, c2, c3]}")

    # Enviar usando función
    enviarFPGA(c1, c2, c3)

    time.sleep(2)
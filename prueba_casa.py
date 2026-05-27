import time
import random
import serial

ser = serial.Serial("COM3", 9600, timeout=0.1)

ser.reset_input_buffer()
ser.reset_output_buffer()

# =========================
# métricas
# =========================
TP = 0
FP = 0
FN = 0

latencias = []

# para medir latencia de ataque
ataque_enviado = False
tiempo_ataque = 0


# =========================
# UART
# =========================
def enviar_valor(modo, ident, valor):
    msg = f"{modo}{ident}{int(valor)}\n"
    ser.write(msg.encode("ascii"))


def enviarFPGA(c1, c2, c3, modo="D"):

    enviar_valor(modo, "A", c1)
    time.sleep(0.01)

    enviar_valor(modo, "B", c2)
    time.sleep(0.01)

    enviar_valor(modo, "C", c3)
    time.sleep(0.01)


# =========================
# revisar mensaje FPGA
# =========================
def revisar_mensaje():

    while ser.in_waiting:

        raw = ser.readline()

        msg = raw.decode(
            errors="ignore"
        ).strip()

        if msg:

            print(msg)

            if msg == "ALERTA_DDOS":
                return True

    return False


# =========================
# perfil inicial normal
# =========================
enviarFPGA(49, 3, 97, modo="N")

ultimo_ataque = time.time()

# =========================
# loop principal
# =========================
while True:

    ahora = time.time()

    ataque = False

    # =====================
    # ATAQUE DE PRUEBA
    # descomenta cuando quieras
    # =====================

    if ahora - ultimo_ataque >= 5:
    
        c1 = random.randint(300, 800)
        c2 = random.randint(80, 90)
        c3 = random.randint(700, 900)
    
        ataque = True
    
        tiempo_ataque = time.time()
        ataque_enviado = True
    #
        ultimo_ataque = ahora
    
    else:

        c1 = random.randint(40, 60)
        c2 = random.randint(1, 5)
        c3 = random.randint(80, 100)

    print(
        "Vector:",
        c1,
        c2,
        c3
    )

    enviarFPGA(c1, c2, c3)

    alerta = revisar_mensaje()

    # =====================
    # métricas
    # =====================
    if ataque:

        if alerta:

            TP += 1

            if ataque_enviado:

                latencia = (
                    time.time() - tiempo_ataque
                ) * 1000

                latencias.append(latencia)

                print(
                    "Latencia:",
                    round(latencia, 2),
                    "ms"
                )

                ataque_enviado = False

        else:
            FN += 1

    else:

        if alerta:
            FP += 1

    # =====================
    # mostrar resultados
    # =====================
    precision = (
        TP / (TP + FP)
        if (TP + FP) > 0
        else 0
    )

    tasa_fn = (
        FN / (TP + FN)
        if (TP + FN) > 0
        else 0
    )

    lat_prom = (
        sum(latencias) / len(latencias)
        if len(latencias) > 0
        else 0
    )

    print(
        "TP:", TP,
        "| FP:", FP,
        "| FN:", FN
    )

    print(
        "Precisión:",
        round(precision * 100, 2),
        "%"
    )

    print(
        "Falsos negativos:",
        round(tasa_fn * 100, 2),
        "%"
    )

    print(
        "Latencia promedio:",
        round(lat_prom, 2),
        "ms"
    )

    print("-------------------")

    time.sleep(2)
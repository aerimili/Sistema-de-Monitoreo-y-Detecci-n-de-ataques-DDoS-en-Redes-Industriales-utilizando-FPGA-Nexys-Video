import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("vectores_capturados.csv")

t0 = df["Timestamp"].iloc[0]
df["Tiempo"] = df["Timestamp"] - t0

plt.figure(figsize=(12,5))
plt.plot(df["Tiempo"], df["C1"], linewidth=2)

en_ataque = False

for i, estado in enumerate(df["Estado"]):

    if estado == "ATAQUE" and not en_ataque:
        inicio = df["Tiempo"].iloc[i]
        en_ataque = True

    elif estado == "NORMAL" and en_ataque:
        fin = df["Tiempo"].iloc[i]
        plt.axvspan(inicio, fin, alpha=0.3, label="Ataque")
        en_ataque = False

if en_ataque:
    plt.axvspan(inicio, df["Tiempo"].iloc[-1], alpha=0.3, label="Ataque")

plt.title("Característica C1")
plt.xlabel("Tiempo (s)")
plt.ylabel("Paquetes por segundo")
plt.xlim([0,100])
plt.grid()

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys())

plt.show()
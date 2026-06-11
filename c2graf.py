import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("vectores_capturados.csv")

plt.figure(figsize=(12,5))
plt.plot(df["C2"])

plt.title("Característica C2")
plt.xlabel("Ventana de observación")
plt.ylabel("Índice de variación IP (%)")
plt.grid()

plt.show()
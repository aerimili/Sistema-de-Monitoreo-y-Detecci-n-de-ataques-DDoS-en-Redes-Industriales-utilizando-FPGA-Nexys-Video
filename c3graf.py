import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("vectores_capturados.csv")

plt.figure(figsize=(12,5))
plt.plot(df["C3"])

plt.title("Característica C3")
plt.xlabel("Ventana de observación")
plt.ylabel("Entropía x100")
plt.grid()

plt.show()
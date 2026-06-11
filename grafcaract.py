import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("vectores_capturados.csv")

plt.figure(figsize=(12,5))
plt.plot(df["C1"], label="C1")
plt.plot(df["C2"], label="C2")
plt.plot(df["C3"], label="C3")

plt.legend()
plt.xlabel("Ventana")
plt.ylabel("Valor")
plt.xlim([0, 100])
plt.title("Evolución temporal de características")
plt.grid()
plt.show()




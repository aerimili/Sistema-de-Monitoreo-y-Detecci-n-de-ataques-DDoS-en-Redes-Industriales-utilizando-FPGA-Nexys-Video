import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("datos_normales.csv", names=["t","C1","C2","C3"])

t0 = data["t"][0]
data["t"] = data["t"] - t0

plt.figure()
plt.plot(data["t"], data["C1"])
plt.xlabel("Tiempo [s]")
plt.ylabel("Tasa de paquetes [pps]")
plt.grid()

plt.figure()
plt.plot(data["t"], data["C2"])
plt.xlabel("Tiempo [s]")
plt.ylabel("Índice de variación de IPs")
plt.grid()

plt.figure()
plt.plot(data["t"], data["C3"])
plt.xlabel("Tiempo [s]")
plt.ylabel("Entropía")
plt.grid()

plt.show()



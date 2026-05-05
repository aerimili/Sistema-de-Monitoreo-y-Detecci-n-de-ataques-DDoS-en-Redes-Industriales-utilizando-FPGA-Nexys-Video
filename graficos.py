import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("datos_normales.csv", names=["t","C1","C2","C3"])

t0 = data["t"][0]
data["t"] = data["t"] - t0

plt.figure()
plt.plot(data["t"], data["C1"], label="C1 [pps]")
plt.plot(data["t"], data["C2"], label="C2")
plt.plot(data["t"], data["C3"], label="C3")

plt.xlabel("Tiempo [s]")
plt.ylabel("Valor")
plt.legend()
plt.grid()
plt.show()
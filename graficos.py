import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv("datos_normales.csv", names=["t","C1","C2","C3"])
data_ataqueTCP = pd.read_csv("datos_ataqueTCPSYN.csv", names=["ta","C1a","C2a","C3a"])


t0 = data["t"][0]
data["t"] = data["t"] - t0

t1 = data_ataqueTCP["ta"][0]
data_ataqueTCP["ta"] = data_ataqueTCP["ta"] - t1


data = data[data["t"] <= 300]
data_ataqueTCP = data_ataqueTCP[data_ataqueTCP["ta"] <= 300]

#C1
plt.figure()
plt.plot(data["t"], data["C1"], color="g", label="Normal")
plt.plot(data_ataqueTCP["ta"], data_ataqueTCP["C1a"], color="r", label="Ataque TCP SYN")
plt.xlabel("Tiempo [s]")
plt.ylabel("Tasa de paquetes [pps]")
plt.title("Tasa de paquetes (C1) Normal v/s Ataque TCP SYN")
plt.legend()
plt.grid()

#C2
plt.figure()
plt.plot(data["t"], data["C2"], color="g", label="Normal")
plt.plot(data_ataqueTCP["ta"], data_ataqueTCP["C2a"], color="r", label="Ataque TCP SYN")
plt.xlabel("Tiempo [s]")
plt.ylabel("Índice de variación de IPs")
plt.title("Variación de direcciones IP (C2) Normal v/s Ataque TCP SYN")
plt.legend()
plt.grid()

#C3
plt.figure()
plt.plot(data["t"], data["C3"], color="g", label="Normal")
plt.plot(data_ataqueTCP["ta"], data_ataqueTCP["C3a"], color="r", label="Ataque TCP SYN")
plt.xlabel("Tiempo [s]")
plt.ylabel("Entropía de IPs")
plt.title("Entropía del tráfico (C3) Normal v/s Ataque TCP SYN")
plt.legend()
plt.grid()

plt.show()


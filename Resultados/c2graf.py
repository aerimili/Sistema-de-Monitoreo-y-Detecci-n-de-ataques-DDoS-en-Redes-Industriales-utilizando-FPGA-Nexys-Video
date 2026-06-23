import pandas as pd
import matplotlib.pyplot as plt


normal = pd.read_csv("datos_normales.csv",names=["Timestamp", "C1", "C2", "C3"])

df = pd.read_csv("vectores_capturados.csv")

normal["Tiempo"] = normal["Timestamp"] - normal["Timestamp"].iloc[0]
tcp = df[df["TipoAtaque"] == "TCP_SYN"].copy()
udp = df[df["TipoAtaque"] == "UDP_flood"].copy()
icmp = df[df["TipoAtaque"] == "ICMP_flood"].copy()

for grupo in [tcp, udp, icmp]:
    if len(grupo) > 0:
        grupo["Tiempo"] = grupo["Timestamp"] - grupo["Timestamp"].iloc[0]


plt.figure(figsize=(8,6))

plt.plot(normal["Tiempo"], normal["C2"],linestyle="-",linewidth=2,label="Normal")
plt.plot(tcp["Tiempo"], tcp["C2"],linestyle="--",linewidth=2,label="TCP SYN Flood")
plt.plot(udp["Tiempo"], udp["C2"],linestyle=":",linewidth=2,label="UDP Flood")
plt.plot(icmp["Tiempo"], icmp["C2"],linestyle="-.",linewidth=2,label="ICMP Flood")

plt.xlabel("Tiempo [s]")
plt.ylabel("Índice de variación de IPs de origen [%]")
plt.title("Índice de variación de IPs de origen (C2) Normal v/s Ataques DDoS")
plt.xlim([0,100])
plt.grid(True, linestyle='--')
plt.legend()

plt.show()
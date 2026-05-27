from scapy.all import rdpcap
import pandas as pd
import matplotlib.pyplot as plt

pcap = rdpcap("trafico.pcapng")

time = [float(pkt.time) for pkt in pcap]

df = pd.DataFrame(time, columns=["timestamp"])

df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

trafico = df.groupby(pd.Grouper(key="timestamp", freq = "1s")).size()

plt.figure()
plt.plot(trafico.index, trafico.values)
plt.xlabel("Tiempo")
plt.ylabel("Paquetes por segundo")
plt.title("Tráfico de red")
plt.show()
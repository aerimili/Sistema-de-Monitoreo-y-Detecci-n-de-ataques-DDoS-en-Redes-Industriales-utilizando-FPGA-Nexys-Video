import pandas as pd 
import matplotlib.pyplot as plt 

df = pd.read_csv("archivo_impacto.csv", names=["Tiempo", "RTT", "Ataque"], skipinitialspace=True) 

df["Ataque"] = df["Ataque"].astype(str).str.strip().str.upper() == "TRUE"

t0 = df["Tiempo"].iloc[0] 
df["Tiempo"] = df["Tiempo"] - t0 
df["Segundo"] = df["Tiempo"].astype(int) 
offset = 335105
df = df[df["Segundo"] >= offset].copy()
df["Segundo_Grafico"] = df["Segundo"] - offset

respuestas = df.groupby("Segundo_Grafico").size() 
ataques = df.groupby("Segundo_Grafico")["Ataque"].any()

segundos = range(0, df["Segundo_Grafico"].max() + 1) 
respuestas = respuestas.reindex(segundos, fill_value=0) 
ataques = ataques.reindex(segundos, fill_value=False)

desconexion = (respuestas == 0)
normal = (respuestas > 0) & (ataques == False)

plt.figure(figsize=(8, 6)) 

plt.plot(respuestas.index, respuestas.values, linewidth=2) 
plt.plot(respuestas.index[normal], respuestas.values[normal], marker='o', linestyle='', color='b', markersize=4, label="Tráfico Normal")
plt.plot(respuestas.index[desconexion], respuestas.values[desconexion], marker='x', linestyle='', color='r', markersize=7, label="Desconexión por ataque")

plt.title("Impacto de ataque DDoS en la disponibilidad de la comunicación Modbus/TCP") 
plt.xlabel("Tiempo [s]") 
plt.ylabel("Tasa de respuesta [rps]") 
plt.xlim([0, 50]) 
plt.ylim([-1, 50])
plt.grid(True, linestyle='--') 
plt.legend()
plt.show()
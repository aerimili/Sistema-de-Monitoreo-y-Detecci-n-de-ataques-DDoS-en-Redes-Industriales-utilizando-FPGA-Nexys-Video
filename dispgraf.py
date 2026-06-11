import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv(
    "archivo_impacto.csv",
    names=["Tiempo","RTT","Ataque"]
)

df["Segundo"] = df["Tiempo"].astype(int)

respuestas = df.groupby("Segundo").size()

plt.figure(figsize=(12,5))
plt.plot(respuestas.index, respuestas.values)

plt.title("Disponibilidad de respuestas Modbus")
plt.xlabel("Tiempo")
plt.ylabel("Respuestas por segundo")
plt.grid()

plt.show()
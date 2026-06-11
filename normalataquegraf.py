import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("vectores_capturados.csv")

normal = df[df["Estado"] == "NORMAL"]
ataque = df[df["Estado"] == "ATAQUE"]

c1_normal = normal["C1"].mean()
c1_ataque = ataque["C1"].mean()

c2_normal = normal["C2"].mean()
c2_ataque = ataque["C2"].mean()

c3_normal = normal["C3"].mean()
c3_ataque = ataque["C3"].mean()

plt.figure(figsize=(10,5))

plt.plot(
    ["C1","C2","C3"],
    [c1_normal,c2_normal,c3_normal],
    marker="o",
    label="Normal"
)

plt.plot(
    ["C1","C2","C3"],
    [c1_ataque,c2_ataque,c3_ataque],
    marker="o",
    label="Ataque"
)

plt.title("Comparación de características")
plt.ylabel("Valor")
plt.legend()
plt.grid()

plt.show()
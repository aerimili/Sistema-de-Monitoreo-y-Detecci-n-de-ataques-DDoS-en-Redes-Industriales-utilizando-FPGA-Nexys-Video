import pandas as pd

df = pd.read_csv("historial_ataques.csv")

latencias = df[df["Latencia_segundos"] > 0]["Latencia_segundos"]

print("Latencias detectadas:")
print(latencias.tolist())

print("\nResumen:")
print(f"Cantidad de ataques detectados: {len(latencias)}")
print(f"Latencia mínima: {latencias.min():.6f} s")
print(f"Latencia máxima: {latencias.max():.6f} s")
print(f"Latencia promedio: {latencias.mean():.6f} s")
print(f"Desviación estándar: {latencias.std():.6f} s")
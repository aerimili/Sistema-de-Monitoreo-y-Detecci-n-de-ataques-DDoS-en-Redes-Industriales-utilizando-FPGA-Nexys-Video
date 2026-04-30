
import numpy as np
import json

data = np.loadtxt("datos_normales.csv", delimiter=",")

C1n = int(np.mean(data[:,0]))
C2n = int(np.mean(data[:,1]))
C3n = int(np.mean(data[:,2]))

std = np.std(data, axis=0)


datos = {
    "C1n": C1n,
    "C2n": C2n,
    "C3n": C3n
}

# Escribir al archivo JSON
with open("perfil_normal.json", "w") as f:
    json.dump(datos, f, indent=4)

print("C1n =", C1n)
print("C2n =", C2n)
print("C3n =", C3n)


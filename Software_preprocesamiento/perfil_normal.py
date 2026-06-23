
import numpy as np
import json

data = np.loadtxt("datos_normales.csv", delimiter=",")

C1n = int(np.mean(data[:,1]))
C2n = int(np.mean(data[:,2]))
C3n = int(np.mean(data[:,3]))

th = 79;

std = np.std(data, axis=0)


datos = {
    "C1n": C1n,
    "C2n": C2n,
    "C3n": C3n,
    "th": th
}

with open("perfil_normal.json", "w") as f:
    json.dump(datos, f, indent=4)

print("C1n =", C1n)
print("C2n =", C2n)
print("C3n =", C3n)
print("th =", th)


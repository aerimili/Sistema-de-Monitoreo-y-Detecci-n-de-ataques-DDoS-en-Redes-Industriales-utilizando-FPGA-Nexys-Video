import seaborn as sns

data["estado"] = ["normal" if t < 60 else "ataque" for t in data["t"]]

sns.boxplot(x="estado", y="C1", data=data)
plt.show()
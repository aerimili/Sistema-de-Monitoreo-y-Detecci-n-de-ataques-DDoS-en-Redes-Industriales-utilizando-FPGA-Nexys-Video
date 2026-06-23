import pandas as pd


df_historial = pd.read_csv("historial_ataques.csv")
latencias = df_historial[df_historial["Latencia_segundos"] > 0]["Latencia_segundos"]
    
cantidad_ataques = len(latencias)
latencia_promedio = latencias.mean() if cantidad_ataques > 0 else 0.0

df_metricas = pd.read_csv("metricas.csv")
df_metricas["Total_Eventos"] = df_metricas["TP"] + df_metricas["FP"] + df_metricas["FN"]
df_metricas["Run_ID"] = (df_metricas["Total_Eventos"] < df_metricas["Total_Eventos"].shift(1)).cumsum()
maximos_por_sesion = df_metricas.groupby("Run_ID")[["TP", "FP", "FN"]].max()

tp_total = int(maximos_por_sesion["TP"].sum())
fp_total = int(maximos_por_sesion["FP"].sum())
fn_total = int(maximos_por_sesion["FN"].sum())
    
precision_global = (tp_total / (tp_total + fp_total)) if (tp_total + fp_total) > 0 else 0.0
fnr_global = (fn_total / (fn_total + tp_total)) if (fn_total + tp_total) > 0 else 0.0

print(f"• Alertas válidas en latencia: {cantidad_ataques}")
print(f"• Latencia promedio: {latencia_promedio:.6f} s")

print(f"• Verdaderos Positivos Totales (TP): {tp_total}")
print(f"• Falsos Positivos Totales (FP): {fp_total}")
print(f"• Falsos Negativos Totales (FN): {fn_total}")
print(f"• Precisión Global: {precision_global * 100:.2f} %")
print(f"• Tasa de Falsos Negativos (FNR): {fnr_global * 100:.2f} %")

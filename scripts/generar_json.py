import pandas as pd
import json

# =========================
# LEER ARCHIVO
# =========================
df = pd.read_excel("output/calendario_comparado.xlsx")

# =========================
# FILTRAR COLUMNAS
# =========================
df_resumen = df[[
    "Sucursal",
    "Proyecto",

    "DiaIntermedia",
    "PosibleIntermedia",
    "RealIntermedia",
    "CoincidenciasIntermedia",
    "ConteoCoincidenciasIntermedia",
    "CumplimientoIntermedia",

    "DiaSemanal",
    "PosibleSemanal",
    "RealSemanal",
    "CoincidenciasSemanal",
    "ConteoCoincidenciasSemanal",
    "CumplimientoSemanal"
]]

# =========================
# GUARDAR EXCEL LIMPIO
# =========================
df_resumen.to_excel("output/resumen_filtrado.xlsx", index=False)

print("✅ Archivo resumen_filtrado.xlsx generado")

# =========================
# CREAR JSON
# =========================
df_resumen = df_resumen.fillna("")

data = []

for _, row in df_resumen.iterrows():

    # INTERMEDIA
    data.append({
        "sucursal": str(row["Sucursal"]).strip().lower(),
        "proyecto": row["Proyecto"],
        "tipo": "Intermedia",
        "dia": row["DiaIntermedia"],
        "posible": str(row["PosibleIntermedia"]),
        "real": str(row["RealIntermedia"]),
        "coincidencias": str(row["CoincidenciasIntermedia"]),
        "conteo": row["ConteoCoincidenciasIntermedia"],
        "cumplimiento": row["CumplimientoIntermedia"]
    })

    # SEMANAL
    data.append({
        "sucursal": str(row["Sucursal"]).strip().lower(),
        "proyecto": row["Proyecto"],
        "tipo": "Semanal",
        "dia": row["DiaSemanal"],
        "posible": str(row["PosibleSemanal"]),
        "real": str(row["RealSemanal"]),
        "coincidencias": str(row["CoincidenciasSemanal"]),
        "conteo": row["ConteoCoincidenciasSemanal"],
        "cumplimiento": row["CumplimientoSemanal"]
    })

# =========================
# GUARDAR JSON
# =========================
with open("output/detalle.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ JSON generado correctamente")

import pandas as pd
import numpy as np
from datetime import timedelta
from parametros import festivos, mapa_dias, MES, ANIO

# =========================
# LIMPIEZA
# =========================
def limpiar_texto(texto):
    if pd.isna(texto):
        return texto
    return str(texto).strip().upper()

# =========================
# FUNCIONES BASE
# =========================
def es_habil(fecha):
    if fecha.weekday() == 6:
        return False
    if fecha in festivos:
        return False
    return True

def obtener_dos_siguientes(fecha):
    return [fecha + timedelta(days=i) for i in range(1,3) if (fecha + timedelta(days=i)).month == MES]

def siguiente_habil(fecha):
    siguiente = fecha + timedelta(days=1)
    while not es_habil(siguiente):
        siguiente += timedelta(days=1)
    return siguiente

# =========================
# CALCULO POSIBLES
# =========================
def calcular_posibles(dia_base, fechas_mes):
    if pd.isna(dia_base):
        return ""

    dia_base = str(dia_base).upper().strip()
    if dia_base not in mapa_dias:
        return ""

    numero_dia = mapa_dias[dia_base]
    posibles = []

    for fecha in fechas_mes:
        fecha = pd.to_datetime(fecha).normalize()

        if fecha.weekday() == numero_dia:

            if fecha in festivos:
                siguiente = siguiente_habil(fecha)
                if siguiente.month == MES:
                    posibles.append(siguiente)

                    siguiente_2 = siguiente_habil(siguiente)
                    if siguiente_2.month == MES:
                        posibles.append(siguiente_2)

            else:
                posibles.append(fecha)

                siguiente = siguiente_habil(fecha)
                if siguiente.month == MES:
                    posibles.append(siguiente)

    posibles = sorted(set(posibles))
    return ", ".join([f.strftime("%Y-%m-%d") for f in posibles])

# =========================
# CONTEOS
# =========================
def contar_fechas(valor):
    if pd.isna(valor) or valor == "":
        return 0
    return len([x for x in str(valor).split(",") if x.strip() != ""])

def contar_fechas_y_dividir(valor):
    if pd.isna(valor) or valor == "":
        return 0
    return len([x for x in str(valor).split(",") if x.strip() != ""]) / 2

# =========================
# COINCIDENCIAS
# =========================
def coincidencias_por_semana(lista_teorica, lista_real):
    if pd.isna(lista_teorica) or pd.isna(lista_real):
        return ""

    teoricas = sorted(set(pd.to_datetime(x.strip()).normalize()
                    for x in str(lista_teorica).split(",") if x.strip()))

    reales = sorted(set(pd.to_datetime(x.strip()).normalize()
                  for x in str(lista_real).split(",") if x.strip()))

    coincidencias = []

    for i in range(0, len(teoricas), 2):

        try:
            inicio = teoricas[i]
            fin = teoricas[i + 1]
        except IndexError:
            fin = inicio  # ✅ par incompleto: usa inicio como fin

        # ✅ Sin día extra — ventana exacta inicio a fin
        holgura = fin

        match = None
        for r in reales:
            if inicio <= r <= holgura:
                match = r
                break

        if match:
            coincidencias.append(match)

    return ", ".join([f.strftime("%Y-%m-%d") for f in coincidencias])

# =========================
# PROCESO PRINCIPAL
# =========================
def procesar_todo(df_proyectos, df_intermedia, df_semanal, fechas_mes):

    df_proyectos["Proyecto"] = df_proyectos["Proyecto"].apply(limpiar_texto)
    df_intermedia["Proyecto"] = df_intermedia["Proyecto"].apply(limpiar_texto)
    df_semanal["Proyecto"] = df_semanal["Proyecto"].apply(limpiar_texto)

    # CALENDARIO TEORICO
    df_proyectos["PosibleIntermedia"] = df_proyectos["DiaIntermedia"].apply(
        lambda x: calcular_posibles(x, fechas_mes)
    )

    df_proyectos["PosibleSemanal"] = df_proyectos["DiaSemanal"].apply(
        lambda x: calcular_posibles(x, fechas_mes)
    )

    df_proyectos["ConteoIntermedia"] = df_proyectos["PosibleIntermedia"].apply(lambda x: contar_fechas(x) / 2)
    df_proyectos["ConteoSemanal"] = df_proyectos["PosibleSemanal"].apply(lambda x: contar_fechas(x) / 2)

    # =========================
    # DETECTAR COLUMNA DE FECHA
    # =========================
    col_fecha_intermedia = "Fecha de Fin" if "Fecha de Fin" in df_intermedia.columns else [c for c in df_intermedia.columns if "fecha" in c.lower()][0]
    col_fecha_semanal = "Fecha de Fin" if "Fecha de Fin" in df_semanal.columns else [c for c in df_semanal.columns if "fecha" in c.lower()][0]

    # NORMALIZAR
    df_intermedia[col_fecha_intermedia] = pd.to_datetime(
        df_intermedia[col_fecha_intermedia], errors="coerce"
    ).dt.normalize()

    df_semanal[col_fecha_semanal] = pd.to_datetime(
        df_semanal[col_fecha_semanal], errors="coerce"
    ).dt.normalize()

    df_intermedia = df_intermedia.dropna(subset=[col_fecha_intermedia])
    df_semanal = df_semanal.dropna(subset=[col_fecha_semanal])

    # FILTRAR SOLO MES ANALIZADO
    df_intermedia = df_intermedia[
        (df_intermedia[col_fecha_intermedia].dt.year == ANIO) &
        (df_intermedia[col_fecha_intermedia].dt.month == MES)
    ]

    df_semanal = df_semanal[
        (df_semanal[col_fecha_semanal].dt.year == ANIO) &
        (df_semanal[col_fecha_semanal].dt.month == MES)
    ]

    # ELIMINAR DUPLICADOS
    df_intermedia = df_intermedia.drop_duplicates(subset=["Proyecto", col_fecha_intermedia])
    df_semanal = df_semanal.drop_duplicates(subset=["Proyecto", col_fecha_semanal])

    # AGRUPAR
    df_intermedia_group = df_intermedia.groupby("Proyecto")[col_fecha_intermedia].apply(
        lambda x: ", ".join(sorted(set(x.dt.strftime("%Y-%m-%d"))))
    ).reset_index()

    df_semanal_group = df_semanal.groupby("Proyecto")[col_fecha_semanal].apply(
        lambda x: ", ".join(sorted(set(x.dt.strftime("%Y-%m-%d"))))
    ).reset_index()

    df_intermedia_group.rename(columns={col_fecha_intermedia: "RealIntermedia"}, inplace=True)
    df_semanal_group.rename(columns={col_fecha_semanal: "RealSemanal"}, inplace=True)

    # MERGE
    df_detallado = df_proyectos.merge(df_intermedia_group, on="Proyecto", how="left")
    df_detallado = df_detallado.merge(df_semanal_group, on="Proyecto", how="left")

    # COINCIDENCIAS
    df_detallado["CoincidenciasIntermedia"] = df_detallado.apply(
        lambda row: coincidencias_por_semana(row["PosibleIntermedia"], row["RealIntermedia"]), axis=1
    )

    df_detallado["CoincidenciasSemanal"] = df_detallado.apply(
        lambda row: coincidencias_por_semana(row["PosibleSemanal"], row["RealSemanal"]), axis=1
    )

    # CONTEOS
    df_detallado["ConteoCoincidenciasIntermedia"] = df_detallado["CoincidenciasIntermedia"].apply(contar_fechas)
    df_detallado["ConteoCoincidenciasSemanal"] = df_detallado["CoincidenciasSemanal"].apply(contar_fechas)

    # CUMPLIMIENTO
    df_detallado["CumplimientoIntermedia"] = np.where(
        df_detallado["ConteoIntermedia"] == 0, 0,
        df_detallado["ConteoCoincidenciasIntermedia"] / df_detallado["ConteoIntermedia"]
    )

    df_detallado["CumplimientoSemanal"] = np.where(
        df_detallado["ConteoSemanal"] == 0, 0,
        df_detallado["ConteoCoincidenciasSemanal"] / df_detallado["ConteoSemanal"]
    )

    df_detallado["CumplimientoIntermedia"] = df_detallado["CumplimientoIntermedia"].clip(upper=1)
    df_detallado["CumplimientoSemanal"] = df_detallado["CumplimientoSemanal"].clip(upper=1)

    # RESUMEN
    comparacion = df_detallado.copy()

    return comparacion, df_detallado

import pandas as pd

# ARCHIVOS
archivo = "input/Reuniones.xlsx"

salida_teorico = "output/calendario_teorico.xlsx"
salida_real = "output/calendario_real.xlsx"
salida_comparado = "output/calendario_comparado.xlsx"

# PARAMETROS
ANIO = 2026
MES = 3

festivos = [
"2026-03-23", "2026-03-30", "2026-03-31"
]

festivos = set(pd.to_datetime(f).normalize() for f in festivos)

# MAPA DIAS
mapa_dias = {
"LUNES":0,"MARTES":1,"MIERCOLES":2,"MIÉRCOLES":2,
"JUEVES":3,"VIERNES":4,"SABADO":5,"SÁBADO":5,"DOMINGO":6
}

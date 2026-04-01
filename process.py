import pandas as pd
from datetime import datetime

def procesar_archivo1():
    # Leer CSV correctamente
    status_df = pd.read_csv('status_history.csv', sep=';')

    # Eliminar columnas basura (;;;;)
    status_df = status_df.loc[:, ~status_df.columns.str.contains('^Unnamed')]

    # Normalizar nombres de columnas
    status_df.columns = status_df.columns.str.strip().str.lower()

    # Normalizar datos
    status_df['status'] = status_df['status'].astype(str).str.lower().str.strip()

    status_df['status_date'] = pd.to_datetime(
        status_df['status_date'],
        dayfirst=True,
        errors='coerce'
    )

    # Eliminar filas inválidas
    status_df = status_df.dropna(subset=['asset_id', 'status_date'])

    # Obtener último estado por asset
    latest_status = (
        status_df
        .sort_values('status_date')
        .groupby('asset_id')
        .tail(1)
        .copy()
    )

    today = pd.Timestamp(datetime.now())

    # Calcular días en estado
    latest_status['dias_en_estado'] = (
        today - latest_status['status_date']
    ).dt.days

    # Generar alerta
    def calcular_alerta(row):
        status = row['status']
        dias = row['dias_en_estado']

        if "transit" in status:
            if dias > 30:
                return "CRITICO"
            elif dias > 15:
                return "ALTO"
        return None

    latest_status['tipo_alerta'] = latest_status.apply(calcular_alerta, axis=1)

    # Filtrar solo alertas
    resultado = latest_status[latest_status['tipo_alerta'].notna()]

    return resultado[['asset_id', 'status', 'dias_en_estado', 'tipo_alerta']]

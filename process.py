import pandas as pd
from datetime import datetime
import os

def procesar_archivo1():
    ruta = os.path.join('App-Script/status_history.csv')

    status_df = pd.read_csv(ruta, sep=';')

    status_df = status_df.loc[:, ~status_df.columns.str.contains('^Unnamed')]
    status_df.columns = status_df.columns.str.strip().str.lower()

    status_df['status'] = status_df['status'].astype(str).str.lower().str.strip()

    status_df['status_date'] = pd.to_datetime(
        status_df['status_date'],
        dayfirst=True,
        errors='coerce'
    )

    status_df = status_df.dropna(subset=['asset_id', 'status_date'])

    latest_status = (
        status_df
        .sort_values('status_date')
        .groupby('asset_id')
        .tail(1)
        .copy()
    )

    today = pd.Timestamp(datetime.now())

    latest_status['dias_en_estado'] = (
        today - latest_status['status_date']
    ).dt.days

    def calcular_alerta(row):
        if "transit" in row['status']:
            if row['dias_en_estado'] > 30:
                return "CRITICO"
            elif row['dias_en_estado'] > 15:
                return "ALTO"
        return None

    latest_status['tipo_alerta'] = latest_status.apply(calcular_alerta, axis=1)

    resultado = latest_status[latest_status['tipo_alerta'].notna()]

    return resultado[['asset_id', 'status', 'dias_en_estado', 'tipo_alerta']]

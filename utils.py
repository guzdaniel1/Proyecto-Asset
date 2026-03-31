def procesar_archivo2():
    assets = pd.read_csv('Apps-Script/assets.csv')
    status = pd.read_csv('Apps-Script/status_history.csv')
    movements = pd.read_csv('Apps-Script/movements.csv')

    # Normalizar
    assets['status'] = assets['status'].astype(str).str.lower()
    assets['location'] = assets['location'].astype(str).str.lower()

    status['status'] = status['status'].astype(str).str.lower()
    status['status_date'] = pd.to_datetime(status['status_date'], errors='coerce')

    movements['movement_date'] = pd.to_datetime(movements['movement_date'], errors='coerce')

    today = pd.Timestamp(datetime.now())

    # Último estado
    latest_status = status.sort_values('status_date').groupby('asset_id').tail(1)

    # Último movimiento
    latest_move = movements.sort_values('movement_date').groupby('asset_id').tail(1)

    latest_move_dict = dict(zip(latest_move['asset_id'], latest_move['movement_date']))

    resultados = []

    for _, row in assets.iterrows():
        asset_id = row['asset_id']
        status_asset = row['status']
        location = row['location']
        assigned = row['assigned_to']

        status_info = latest_status[latest_status['asset_id'] == asset_id]

        if status_info.empty:
            continue

        status_date = status_info.iloc[0]['status_date']
        diff_days = (today - status_date).days

        last_move = latest_move_dict.get(asset_id)

        # REGRA 1
        if "stock" in status_asset and "warehouse" not in location:
            resultados.append([asset_id, "ubicacion", "In Stock pero fuera de deposito", "MEDIA"])

        # REGRA 2
        if "use" in status_asset and pd.isna(assigned):
            resultados.append([asset_id, "asignacion", "En uso sin asignacion", "ALTA"])

        if "stock" in status_asset and pd.notna(assigned):
            resultados.append([asset_id, "asignacion", "En stock pero asignado", "MEDIA"])

        # REGRA 3
        if "transit" in status_asset:
            if pd.isna(last_move) or (today - last_move).days > 10:
                resultados.append([asset_id, "movimiento", "En transito sin movimiento reciente", "CRITICA"])

        # REGRA 4
        if "transit" in status_asset and diff_days > 30:
            resultados.append([asset_id, "tiempo", "Mas de 30 dias en transito", "CRITICA"])

    df_resultado = pd.DataFrame(resultados, columns=["asset_id", "tipo", "detalle", "prioridad"])

    return df_resultado
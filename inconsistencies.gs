function detectarInconsistencias() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const assetsSheet = ss.getSheetByName("assets");
  const statusSheet = ss.getSheetByName("status_history");
  const movementsSheet = ss.getSheetByName("movements");

  let output = ss.getSheetByName("inconsistencias");
  if (!output) {
    output = ss.insertSheet("inconsistencias");
  } else {
    output.clear();
  }

  output.appendRow(["asset_id", "tipo", "detalle", "prioridad"]);

  const assets = assetsSheet.getDataRange().getValues();
  const status = statusSheet.getDataRange().getValues();
  const movements = movementsSheet.getDataRange().getValues();

  const today = new Date();

  //  índices dinámicos
  const aHeaders = assets[0];
  const sHeaders = status[0];
  const mHeaders = movements[0];

  const aId = aHeaders.indexOf("asset_id");
  const aStatus = aHeaders.indexOf("status");
  const aLocation = aHeaders.indexOf("location");
  const aAssigned = aHeaders.indexOf("assigned_to");

  const sAsset = sHeaders.indexOf("asset_id");
  const sStatus = sHeaders.indexOf("status");
  const sDate = sHeaders.indexOf("status_date");

  const mAsset = mHeaders.indexOf("asset_id");
  const mDate = mHeaders.indexOf("movement_date");

  //  último estado
  let latestStatus = {};
  for (let i = 1; i < status.length; i++) {
    const row = status[i];
    const id = row[sAsset];
    const st = String(row[sStatus]).toLowerCase();
    const dt = new Date(row[sDate]);

    if (!latestStatus[id] || latestStatus[id].date < dt) {
      latestStatus[id] = { status: st, date: dt };
    }
  }

  // último movimiento
  let latestMove = {};
  for (let i = 1; i < movements.length; i++) {
    const row = movements[i];
    const id = row[mAsset];
    const dt = new Date(row[mDate]);

    if (!latestMove[id] || latestMove[id] < dt) {
      latestMove[id] = dt;
    }
  }

  // análisis principal
  for (let i = 1; i < assets.length; i++) {
    const row = assets[i];

    const id = row[aId];
    const statusAsset = String(row[aStatus]).toLowerCase();
    const location = String(row[aLocation]).toLowerCase();
    const assigned = row[aAssigned];

    const statusInfo = latestStatus[id];
    if (!statusInfo) continue;

    const diffDays = Math.floor((today - statusInfo.date) / (1000 * 60 * 60 * 24));
    const lastMove = latestMove[id];

    let prioridad = "BAJA";

    //  regla 1
    if (statusAsset.includes("stock") && !location.includes("warehouse")) {
      prioridad = "MEDIA";
      output.appendRow([id, "ubicacion", "In Stock pero fuera de deposito", prioridad]);
    }

    // regla 2
    if (statusAsset.includes("use") && !assigned) {
      prioridad = "ALTA";
      output.appendRow([id, "asignacion", "En uso sin asignacion", prioridad]);
    }

    if (statusAsset.includes("stock") && assigned) {
      prioridad = "MEDIA";
      output.appendRow([id, "asignacion", "En stock pero asignado", prioridad]);
    }

    // regla 3
    if (statusAsset.includes("transit")) {
      if (!lastMove || (today - lastMove) / (1000*60*60*24) > 10) {
        prioridad = "CRITICA";
        output.appendRow([id, "movimiento", "En transito sin movimiento reciente", prioridad]);
      }
    }

    // regla 4
    if (statusAsset.includes("transit") && diffDays > 30) {
      prioridad = "CRITICA";
      output.appendRow([id, "tiempo", "Mas de 30 dias en transito", prioridad]);
    }
  }
}

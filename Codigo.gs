function analizarActivos() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const assetsSheet = ss.getSheetByName("assets");
  const statusSheet = ss.getSheetByName("status_history");

  let outputSheet = ss.getSheetByName("resultado");
  if (!outputSheet) {
    outputSheet = ss.insertSheet("resultado");
  } else {
    outputSheet.clear();
  }

  outputSheet.appendRow(["asset_id", "estado_actual", "dias_en_estado", "tipo_alerta"]);

  const statusData = statusSheet.getDataRange().getValues();
  const today = new Date();

  let latestStatus = {};

  const headers = statusData[0];
  const assetIndex = headers.indexOf("asset_id");
  const statusIndex = headers.indexOf("status");
  const dateIndex = headers.indexOf("status_date");

  //  Obtener último estado
  for (let i = 1; i < statusData.length; i++) {
    const row = statusData[i];

    const assetId = row[assetIndex];
    const status = String(row[statusIndex]).toLowerCase().trim();
    const date = new Date(row[dateIndex]);

    if (!assetId || isNaN(date)) continue;

    if (!latestStatus[assetId] || latestStatus[assetId].date < date) {
      latestStatus[assetId] = { status, date };
    }
  }

  // Analizar
  Object.keys(latestStatus).forEach(assetId => {
    const { status, date } = latestStatus[assetId];

    const diffDays = Math.floor((today - date) / (1000 * 60 * 60 * 24));

    let alerta = "";

    if (status.includes("transit")) {
      if (diffDays > 30) {
        alerta = "CRITICO";
      } else if (diffDays > 15) {
        alerta = "ALTO";
      }
    }

    if (alerta) {
      outputSheet.appendRow([assetId, status, diffDays, alerta]);
    }
  });
}
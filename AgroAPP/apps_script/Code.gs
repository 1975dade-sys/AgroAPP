/**
 * AgroApp — Estensioni → Apps Script del foglio Google.
 * Colonne diario: A=Inizio (data/ora), … Operatore, … ID in fondo.
 * Dopo ogni modifica: Distribuisci → Gestisci distribuzioni → Modifica → Nuova versione.
 */
var HEADERS_DIARIO = [
  "Inizio",
  "Fine",
  "Stato",
  "Operatore",
  "Campo",
  "Cultura",
  "Prodotto",
  "Mezzo",
  "Attività",
  "Note",
  "Problemi",
  "ID",
];

function jsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(
    ContentService.MimeType.JSON
  );
}

function getDiarioSheet(ss) {
  return ss.getSheets()[0];
}

function colIndex(headers, name) {
  var i = headers.indexOf(name);
  return i >= 0 ? i : -1;
}

function readHeaderRow(sheet) {
  var lc = Math.max(sheet.getLastColumn(), HEADERS_DIARIO.length);
  if (sheet.getLastRow() < 1) return [];
  return sheet
    .getRange(1, 1, 1, lc)
    .getValues()[0]
    .map(function (h) {
      return String(h).trim();
    });
}

/** Migra una riga dati dal vecchio ordine (ID in colonna A) al nuovo (Inizio in A, ID in fondo). */
function tryMigrateOldFormatRow(sheet, row) {
  var maxC = Math.max(sheet.getLastColumn(), 12);
  var vals = sheet.getRange(row, 1, 1, maxC).getValues()[0];
  var a = String(vals[0] || "").trim();
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}/i.test(a)) return false;
  var id = vals[0];
  var inizio = vals[1] != null ? String(vals[1]) : "";
  var fine = vals[2] != null ? String(vals[2]) : "";
  var stato = vals[3] != null ? String(vals[3]) : "";
  var op = vals[4] != null ? String(vals[4]) : "";
  var campo = vals[5] != null ? String(vals[5]) : "";
  var cult = vals[6] != null ? String(vals[6]) : "";
  var prod = vals[7] != null ? String(vals[7]) : "";
  var att = vals[8] != null ? String(vals[8]) : "";
  var note = vals[9] != null ? String(vals[9]) : "";
  var prob = vals[10] != null ? String(vals[10]) : "";
  var newRow = [inizio, fine, stato, op, campo, cult, prod, "", att, note, prob, id];
  sheet.getRange(row, 1, 1, HEADERS_DIARIO.length).setValues([newRow]);
  return true;
}

function migrateDiarioDataRows(sheet) {
  var last = sheet.getLastRow();
  var r;
  for (r = 2; r <= last; r++) {
    tryMigrateOldFormatRow(sheet, r);
  }
}

/** Se manca la colonna Mezzo (fogli creati prima dell'aggiornamento), la inserisce dopo Prodotto. */
function ensureMezzoColumn(sheet) {
  var headers = readHeaderRow(sheet);
  if (colIndex(headers, "Mezzo") >= 0) return;
  var pc = colIndex(headers, "Prodotto");
  var colAfter = pc >= 0 ? pc + 1 : 7;
  sheet.insertColumnAfter(colAfter);
  sheet.getRange(1, 1, 1, HEADERS_DIARIO.length).setValues([HEADERS_DIARIO]);
}

function ensureDiarioHeaders(sheet) {
  if (sheet.getLastRow() < 1) {
    sheet.getRange(1, 1, 1, HEADERS_DIARIO.length).setValues([HEADERS_DIARIO]);
    return;
  }
  var h0 = String(sheet.getRange(1, 1).getValue()).trim();
  if (h0 === "Inizio") {
    migrateDiarioDataRows(sheet);
    ensureMezzoColumn(sheet);
    return;
  }
  var r2 = sheet.getLastRow() >= 2 ? String(sheet.getRange(2, 1).getValue()).trim() : "";
  var r2looksUuid = /^[0-9a-f]{8}-[0-9a-f]{4}/i.test(r2);
  if ((h0 === "Data" || h0 === "ID") && r2looksUuid) {
    sheet.getRange(1, 1, 1, HEADERS_DIARIO.length).setValues([HEADERS_DIARIO]);
    migrateDiarioDataRows(sheet);
    ensureMezzoColumn(sheet);
    return;
  }
  sheet.insertRowBefore(1);
  sheet.getRange(1, 1, 1, HEADERS_DIARIO.length).setValues([HEADERS_DIARIO]);
}

function findRowById(sheet, id) {
  var data = sheet.getDataRange().getValues();
  if (data.length < 2) return -1;
  var headers = data[0].map(function (h) {
    return String(h).trim();
  });
  var idStr = String(id).trim();
  if (!idStr) return -1;

  var idCol = colIndex(headers, "ID");
  if (idCol < 0) idCol = headers.length - 1;
  if (idCol < 0) idCol = 0;

  var r;
  for (r = 1; r < data.length; r++) {
    if (String(data[r][idCol]).trim() === idStr) return r + 1;
  }
  for (r = 1; r < data.length; r++) {
    var c;
    for (c = 0; c < data[r].length; c++) {
      if (String(data[r][c]).trim() === idStr) return r + 1;
    }
  }
  return -1;
}

function findRowInCorso(sheet, inizio, operatore, campo) {
  var data = sheet.getDataRange().getValues();
  if (data.length < 2) return -1;
  var headers = data[0].map(function (h) {
    return String(h).trim();
  });
  var inizioCol = colIndex(headers, "Inizio");
  if (inizioCol < 0) inizioCol = colIndex(headers, "Data");
  if (inizioCol < 0) inizioCol = 0;
  var opCol = colIndex(headers, "Operatore");
  var campoCol = colIndex(headers, "Campo");
  var statoCol = colIndex(headers, "Stato");
  var inizioStr = String(inizio || "").trim();
  var opStr = String(operatore || "").trim();
  var campoStr = String(campo || "").trim();

  for (var r = 1; r < data.length; r++) {
    var stato = statoCol >= 0 ? String(data[r][statoCol]).trim().toLowerCase() : "";
    if (stato.indexOf("corso") < 0) continue;
    if (inizioStr && String(data[r][inizioCol]).trim() !== inizioStr) continue;
    if (opStr && opCol >= 0 && String(data[r][opCol]).trim() !== opStr) continue;
    if (campoStr && campoCol >= 0 && String(data[r][campoCol]).trim() !== campoStr) continue;
    return r + 1;
  }
  return -1;
}

function ensureSheetWithHeaders(ss, sheetName, headers) {
  var sh = ss.getSheetByName(sheetName);
  if (!sh) sh = ss.insertSheet(sheetName);
  if (!headers || !headers.length) return sh;
  if (sh.getLastRow() < 1) {
    sh.appendRow(headers);
    return sh;
  }
  var first = String(sh.getRange(1, 1).getValue()).trim();
  var want = String(headers[0]).trim();
  if (first !== want) {
    sh.insertRowBefore(1);
    sh.getRange(1, 1, 1, headers.length).setValues([headers]);
  }
  return sh;
}

function doPost(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var p = JSON.parse(e.postData.contents);

  if (p.tipo === "operatore") {
    var sheetOp = ss.getSheetByName("Operatori agricoli");
    if (!sheetOp) {
      sheetOp = ss.insertSheet("Operatori agricoli");
      sheetOp.appendRow(["Data", "Nome", "Cognome", "Telefono", "Note", "Attivo"]);
    }
    sheetOp.appendRow([
      p.data,
      p.nome || "",
      p.cognome || "",
      p.telefono || "",
      p.note || "",
      p.attivo || "Si",
    ]);
    return jsonResponse({ ok: true });
  }

  if (p.tipo === "append_sheet") {
    var headers = p.headers || [];
    var values = p.values || [];
    var sh = ensureSheetWithHeaders(ss, p.sheet || "Dati", headers);
    sh.appendRow(values);
    return jsonResponse({ ok: true });
  }

  var sheet = getDiarioSheet(ss);

  if (p.tipo === "attivita_inizio") {
    ensureDiarioHeaders(sheet);
    sheet.appendRow([
      p.inizio,
      "",
      p.stato || "In corso",
      p.operatore || "",
      p.campo || "",
      p.cultura || "",
      p.prodotto || "",
      p.mezzo || "",
      p.attivita || "",
      p.note || "",
      "",
      p.id,
    ]);
    return jsonResponse({ ok: true, id: p.id });
  }

  if (p.tipo === "attivita_fine") {
    ensureDiarioHeaders(sheet);
    var row = findRowById(sheet, p.id);
    if (row < 0) {
      row = findRowInCorso(sheet, p.inizio, p.operatore, p.campo);
    }
    if (row < 0) {
      sheet.appendRow([
        p.inizio || "",
        p.fine || "",
        p.stato || "Conclusa",
        p.operatore || "",
        p.campo || "",
        p.cultura || "",
        p.prodotto || "",
        p.mezzo || "",
        p.attivita || "",
        p.note || "",
        p.problemi || "",
        p.id || "",
      ]);
      return jsonResponse({ ok: true, id: p.id, recovered: true });
    }
    var headers = readHeaderRow(sheet);
    var fineCol = colIndex(headers, "Fine");
    var statoCol = colIndex(headers, "Stato");
    var noteCol = colIndex(headers, "Note");
    var probCol = colIndex(headers, "Problemi");
    if (fineCol >= 0) sheet.getRange(row, fineCol + 1).setValue(p.fine || "");
    if (statoCol >= 0) sheet.getRange(row, statoCol + 1).setValue(p.stato || "Conclusa");
    if (noteCol >= 0 && p.note !== undefined) sheet.getRange(row, noteCol + 1).setValue(p.note || "");
    if (probCol >= 0) sheet.getRange(row, probCol + 1).setValue(p.problemi || "");
    return jsonResponse({ ok: true, id: p.id });
  }

  if (p.tipo === "attivita_completa") {
    ensureDiarioHeaders(sheet);
    sheet.appendRow([
      p.inizio,
      p.fine,
      p.stato || "Conclusa",
      p.operatore || "",
      p.campo || "",
      p.cultura || "",
      p.prodotto || "",
      p.mezzo || "",
      p.attivita || "",
      p.note || "",
      p.problemi || "",
      p.id,
    ]);
    return jsonResponse({ ok: true, id: p.id });
  }

  // Retrocompatibilità: vecchio formato senza tipo
  ensureDiarioHeaders(sheet);
  sheet.appendRow([
    p.data || p.inizio || "",
    p.fine || "",
    p.stato || "Conclusa",
    p.operatore || "",
    p.campo || "",
    p.cultura || "",
    p.prodotto || "",
    p.mezzo || "",
    p.attivita || "",
    p.note || "",
    p.problemi || "",
    p.id || "",
  ]);
  return jsonResponse({ ok: true });
}

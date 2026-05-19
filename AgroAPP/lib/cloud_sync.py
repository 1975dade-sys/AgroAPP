"""
Sincronizzazione dati: copia locale (mirror JSONL) + append su Google Sheets (App web).

Il mirror è sempre scritto su disco. Il cloud richiede `webapp_url` in secrets e uno
script Apps Script aggiornato (vedi `apps_script/Code.gs`, tipo `append_sheet`).
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

MIRROR_DIR = Path(__file__).resolve().parent.parent / "data" / "mirror"


def _ora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _senza_password(d: dict) -> dict:
    return {k: v for k, v in d.items() if "password" not in str(k).lower()}


def mirror_jsonl(entita: str, record: dict) -> None:
    """Append una riga JSON in `data/mirror/{entita}.jsonl` (backup / audit locale)."""
    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    path = MIRROR_DIR / f"{entita}.jsonl"
    line = json.dumps(
        {"_salvato_il": _ora(), **_senza_password(record)},
        ensure_ascii=False,
    )
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def append_sheet_cloud(sheet: str, headers: list[str], values: list[Any]) -> None:
    """POST verso Apps Script: crea il foglio se manca e aggiunge una riga."""
    from lib.gsheet import get_webapp_url

    url = get_webapp_url()
    if not url:
        return
    vals = ["" if v is None else str(v) for v in values]
    while len(vals) < len(headers):
        vals.append("")
    vals = vals[: len(headers)]
    payload = {
        "tipo": "append_sheet",
        "sheet": sheet,
        "headers": headers,
        "values": vals,
    }
    r = requests.post(url, json=payload, timeout=30)
    r.raise_for_status()
    try:
        body = r.json() if r.text else {}
    except ValueError:
        body = {}
    if isinstance(body, dict) and body.get("ok") is False:
        raise RuntimeError(body.get("error", "Errore append_sheet"))
    mirror_jsonl(
        "anagrafica_cloud",
        {"tipo_evento": "append_sheet", "sheet": sheet, "headers": headers, "values": vals},
    )


def try_append_sheet_cloud(sheet: str, headers: list[str], values: list[Any]) -> str | None:
    """Come append_sheet_cloud ma non solleva: ritorna messaggio errore o None."""
    try:
        append_sheet_cloud(sheet, headers, values)
    except Exception as exc:
        return str(exc)
    return None


def sync_campo(voce: dict) -> str | None:
    mirror_jsonl("campi", voce)
    return try_append_sheet_cloud(
        "Anagrafica_Campi",
        ["Data", "ID", "Nome", "Note"],
        [_ora(), voce.get("id", ""), voce.get("nome", ""), voce.get("note", "")],
    )


def sync_cultura(voce: dict) -> str | None:
    mirror_jsonl("colture", voce)
    return try_append_sheet_cloud(
        "Anagrafica_Colture",
        ["Data", "ID", "Nome", "Prodotto_semina", "Note"],
        [
            _ora(),
            voce.get("id", ""),
            voce.get("nome", ""),
            voce.get("prodotto_semina", ""),
            voce.get("note", ""),
        ],
    )


def sync_prodotto(voce: dict) -> str | None:
    mirror_jsonl("prodotti", voce)
    return try_append_sheet_cloud(
        "Anagrafica_Prodotti",
        ["Data", "ID", "Nome", "Categoria", "Note"],
        [
            _ora(),
            voce.get("id", ""),
            voce.get("nome", ""),
            voce.get("categoria", ""),
            voce.get("note", ""),
        ],
    )


def sync_mezzo_agricolo(voce: dict) -> str | None:
    """Trattori, rimorchi, attrezzi: tabella dedicata sul foglio Google."""
    mirror_jsonl("mezzi_agricoli", voce)
    return try_append_sheet_cloud(
        "Anagrafica_Mezzi_Agricoli",
        [
            "Data",
            "ID",
            "Nome",
            "Marca",
            "Modello",
            "Targa_identificativo",
            "Note",
        ],
        [
            _ora(),
            voce.get("id", ""),
            voce.get("nome", ""),
            voce.get("marca", ""),
            voce.get("modello", ""),
            voce.get("targa_identificativo", ""),
            voce.get("note", ""),
        ],
    )


def sync_utente(voce: dict) -> str | None:
    """Account / utente (senza password sul cloud)."""
    mirror_jsonl("account", voce)
    pwd_ok = "Si" if bool(voce.get("password_hash")) else "No"
    return try_append_sheet_cloud(
        "Account_Utenti",
        [
            "Data",
            "ID",
            "Ruolo",
            "Nome",
            "Cognome",
            "Username",
            "Mansione",
            "Telefono",
            "Note",
            "Accesso_attivo",
            "Password_impostata",
        ],
        [
            _ora(),
            voce.get("id", ""),
            voce.get("ruolo", ""),
            voce.get("nome", ""),
            voce.get("cognome", ""),
            voce.get("username", ""),
            voce.get("mansione", ""),
            voce.get("telefono", ""),
            voce.get("note", ""),
            "Si" if voce.get("accesso_attivo") else "No",
            pwd_ok,
        ],
    )


def registra_audit_account(utente: dict, azione: str, dettaglio: str = "") -> str | None:
    """
    Traccia su mirror e sul foglio «Account_Modifiche» password, revoche e disattivazioni.
    """
    record = {
        "azione": azione,
        "dettaglio": dettaglio,
        **_senza_password(dict(utente)),
    }
    mirror_jsonl("account_modifiche", record)
    pwd_ok = "Si" if bool(utente.get("password_hash")) else "No"
    return try_append_sheet_cloud(
        "Account_Modifiche",
        [
            "Data",
            "Azione",
            "ID",
            "Ruolo",
            "Nome",
            "Cognome",
            "Username",
            "Accesso_attivo",
            "Password_impostata",
            "Dettaglio",
        ],
        [
            _ora(),
            azione,
            utente.get("id", ""),
            utente.get("ruolo", ""),
            utente.get("nome", ""),
            utente.get("cognome", ""),
            utente.get("username", ""),
            "Si" if utente.get("accesso_attivo") else "No",
            pwd_ok,
            dettaglio,
        ],
    )


def mirror_evento_attivita(tipo: str, payload: dict) -> None:
    """Registra ogni POST verso Apps Script (attività, operatore foglio, ecc.)."""
    entita = "operatore_foglio" if tipo == "operatore" else "attivita"
    mirror_jsonl(entita, {"tipo_evento": tipo, **payload})

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
import requests
import streamlit as st
from streamlit_gsheets import GSheetsConnection

COLONNE_DIARIO = [
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
]
from lib.stati import (
    STATO_ANNULLATA,
    STATO_CONCLUSA,
    STATO_IN_CORSO,
    STATO_PROBLEMI,
)
from lib.cloud_sync import mirror_evento_attivita, mirror_jsonl

SECRETS_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
FOGLIO_URL = (
    "https://docs.google.com/spreadsheets/d/1E4sTGusQbi0OCAhdb3DFEpBxdfqBXD3bAvnrSeoRSok/edit?usp=sharing"
)

def get_apps_script_ui() -> str:
    path = Path(__file__).resolve().parent.parent / "apps_script" / "Code.gs"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return "// File apps_script/Code.gs non trovato nel progetto."


APPS_SCRIPT_UI = get_apps_script_ui()


@st.cache_resource
def get_conn() -> GSheetsConnection:
    return st.connection("gsheets", type=GSheetsConnection)


def _gs_secrets() -> dict:
    try:
        return dict(st.secrets["connections"]["gsheets"])
    except (KeyError, FileNotFoundError):
        return {}


def get_webapp_url() -> str | None:
    if url := st.session_state.get("webapp_url"):
        return url.strip() or None
    url = _gs_secrets().get("webapp_url")
    return url.strip() if url else None


def scrittura_service_account() -> bool:
    return _gs_secrets().get("type") == "service_account"


def scrittura_abilitata() -> bool:
    return bool(get_webapp_url()) or scrittura_service_account()


def salva_webapp_in_config(url: str) -> None:
    url = url.strip()
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECRETS_PATH.write_text(
        f'[connections.gsheets]\nspreadsheet = "{FOGLIO_URL}"\nwebapp_url = "{url}"\n',
        encoding="utf-8",
    )
    st.session_state["webapp_url"] = url


def _ora_adesso() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _invalida_cache() -> None:
    st.cache_data.clear()


def _post_webapp(payload: dict) -> None:
    response = requests.post(get_webapp_url(), json=payload, timeout=30)
    response.raise_for_status()
    try:
        body = response.json() if response.text else {}
    except ValueError:
        body = {}
    if isinstance(body, dict) and body.get("ok") is False:
        raise RuntimeError(body.get("error", "Errore Apps Script"))
    mirror_evento_attivita(str(payload.get("tipo", "webapp")), payload)
    _invalida_cache()


def _normalizza_dataframe(df: pd.DataFrame, colonne: list[str]) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    if "Data" in df.columns and "Inizio" not in df.columns:
        df["Inizio"] = df["Data"]
    for col in colonne:
        if col not in df.columns:
            df[col] = ""
    return df[colonne]


def carica_gsheet(conn: GSheetsConnection, colonne: list[str] | None = None) -> pd.DataFrame:
    colonne = colonne or COLONNE_DIARIO
    try:
        df = conn.read(ttl=0)
    except Exception as exc:
        st.error(f"Impossibile leggere il foglio Google: {exc}")
        return pd.DataFrame(columns=colonne)

    if df.empty:
        return pd.DataFrame(columns=colonne)

    return _normalizza_dataframe(df, colonne)


def _riga_da_attivita(att: dict, stato: str, inizio: str, fine: str = "") -> dict:
    return {
        "Inizio": inizio,
        "Fine": fine,
        "Stato": stato,
        "Operatore": att.get("operatore", ""),
        "Campo": att.get("campo", ""),
        "Cultura": att.get("cultura", ""),
        "Prodotto": att.get("prodotto", ""),
        "Mezzo": att.get("mezzo", ""),
        "Attività": att.get("attivita", ""),
        "Note": att.get("note", ""),
        "Problemi": att.get("problemi", ""),
        "ID": att.get("id", str(uuid4())),
    }


def _append_riga(conn: GSheetsConnection, riga: dict) -> None:
    df = carica_gsheet(conn)
    nuova = pd.DataFrame([riga])
    conn.update(data=pd.concat([df, nuova], ignore_index=True))
    mirror_jsonl(
        "attivita",
        {
            "tipo_evento": "append_service_account",
            **{str(k): "" if v is None else str(v) for k, v in riga.items()},
        },
    )
    _invalida_cache()


def _mask_attivita(df: pd.DataFrame, attivita_id: str, att: dict | None) -> pd.Series:
    id_str = str(attivita_id).strip()
    if "ID" in df.columns:
        mask = df["ID"].astype(str).str.strip() == id_str
        if mask.any():
            return mask
    if len(df.columns) > 0:
        prima_col = df.columns[0]
        mask = df[prima_col].astype(str).str.strip() == id_str
        if mask.any():
            return mask
    if not att:
        return pd.Series([False] * len(df), index=df.index)

    col_inizio = "Inizio" if "Inizio" in df.columns else "Data"
    if col_inizio not in df.columns:
        return pd.Series([False] * len(df), index=df.index)

    inizio = str(att.get("iniziata_il", "")).strip()
    operatore = str(att.get("operatore", "")).strip()
    campo = str(att.get("campo", "")).strip()
    mask = df[col_inizio].astype(str).str.strip() == inizio
    if "Operatore" in df.columns and operatore:
        mask &= df["Operatore"].astype(str).str.strip() == operatore
    if "Campo" in df.columns and campo:
        mask &= df["Campo"].astype(str).str.strip() == campo
    if "Stato" in df.columns:
        mask &= df["Stato"].astype(str).str.contains("corso", case=False, na=False)
    return mask


def _aggiorna_riga(
    conn: GSheetsConnection,
    attivita_id: str,
    aggiornamenti: dict,
    att: dict | None = None,
) -> None:
    df = carica_gsheet(conn)
    mask = _mask_attivita(df, attivita_id, att)
    if not mask.any():
        if att:
            _append_chiusura_mancante(conn, att, aggiornamenti)
            return
        raise RuntimeError("Attività non trovata sul foglio.")
    for col, val in aggiornamenti.items():
        if col in df.columns:
            df.loc[mask, col] = val
    conn.update(data=df)
    mirror_jsonl(
        "attivita",
        {
            "tipo_evento": "update_service_account",
            "attivita_id": attivita_id,
            **{str(k): "" if v is None else str(v) for k, v in aggiornamenti.items()},
        },
    )
    _invalida_cache()


def _append_chiusura_mancante(conn: GSheetsConnection, att: dict, aggiornamenti: dict) -> None:
    """Se la riga in corso non c'è sul foglio, la registra chiusa."""
    inizio = att.get("iniziata_il") or _ora_adesso()
    fine = aggiornamenti.get("Fine") or _ora_adesso()
    riga = _riga_da_attivita(
        {
            **att,
            "note": aggiornamenti.get("Note", att.get("note", "")),
            "problemi": aggiornamenti.get("Problemi", ""),
        },
        aggiornamenti.get("Stato", STATO_CONCLUSA),
        inizio,
        fine,
    )
    riga["ID"] = att.get("id", riga["ID"])
    _append_riga(conn, riga)


def registra_inizio_attivita(conn: GSheetsConnection, att: dict) -> str:
    """Registra l'attività sul foglio all'avvio (stato In corso)."""
    inizio = att.get("iniziata_il") or _ora_adesso()
    attivita_id = att.get("id") or str(uuid4())

    payload = {
        "tipo": "attivita_inizio",
        "id": attivita_id,
        "inizio": inizio,
        "stato": STATO_IN_CORSO,
        "operatore": att.get("operatore", ""),
        "campo": att.get("campo", ""),
        "cultura": att.get("cultura", ""),
        "prodotto": att.get("prodotto", ""),
        "mezzo": att.get("mezzo", ""),
        "attivita": att.get("attivita", ""),
        "note": att.get("note", ""),
    }

    if get_webapp_url():
        _post_webapp(payload)
        return attivita_id

    if scrittura_service_account():
        _append_riga(conn, _riga_da_attivita(att, STATO_IN_CORSO, inizio))
        return attivita_id

    raise RuntimeError("Scrittura non configurata")


def chiudi_attivita_registro(
    conn: GSheetsConnection,
    attivita_id: str,
    stato: str,
    note: str = "",
    problemi: str = "",
    att: dict | None = None,
) -> None:
    """Aggiorna la riga sul foglio con orario di fine, stato e problemi."""
    fine = _ora_adesso()
    sorgente = att or {}
    payload = {
        "tipo": "attivita_fine",
        "id": attivita_id,
        "fine": fine,
        "stato": stato,
        "note": note,
        "problemi": problemi,
        "inizio": sorgente.get("iniziata_il", ""),
        "operatore": sorgente.get("operatore", ""),
        "campo": sorgente.get("campo", ""),
        "cultura": sorgente.get("cultura", ""),
        "prodotto": sorgente.get("prodotto", ""),
        "mezzo": sorgente.get("mezzo", ""),
        "attivita": sorgente.get("attivita", ""),
    }
    aggiornamenti = {"Fine": fine, "Stato": stato, "Note": note, "Problemi": problemi}

    if get_webapp_url():
        try:
            _post_webapp(payload)
        except RuntimeError as exc:
            if "non trovata" not in str(exc).lower():
                raise
            if scrittura_service_account():
                _aggiorna_riga(conn, attivita_id, aggiornamenti, att)
            elif att:
                _append_chiusura_mancante(conn, att, aggiornamenti)
            else:
                raise
        return

    if scrittura_service_account():
        _aggiorna_riga(conn, attivita_id, aggiornamenti, att)
        return

    raise RuntimeError("Scrittura non configurata")


def registra_attivita_completa(
    conn: GSheetsConnection,
    operatore: str,
    campo: str,
    attivita: str,
    note: str = "",
    cultura: str = "",
    prodotto: str = "",
    mezzo: str = "",
    problemi: str = "",
) -> str:
    """Registra subito inizio e fine (salvataggio immediato dal diario)."""
    ora = _ora_adesso()
    attivita_id = str(uuid4())
    payload = {
        "tipo": "attivita_completa",
        "id": attivita_id,
        "inizio": ora,
        "fine": ora,
        "stato": STATO_PROBLEMI if problemi.strip() else STATO_CONCLUSA,
        "operatore": operatore,
        "campo": campo,
        "cultura": cultura,
        "prodotto": prodotto,
        "mezzo": mezzo,
        "attivita": attivita,
        "note": note,
        "problemi": problemi,
    }

    if get_webapp_url():
        _post_webapp(payload)
        return attivita_id

    if scrittura_service_account():
        att = {
            "id": attivita_id,
            "operatore": operatore,
            "campo": campo,
            "cultura": cultura,
            "prodotto": prodotto,
            "mezzo": mezzo,
            "attivita": attivita,
            "note": note,
            "problemi": problemi,
        }
        _append_riga(conn, _riga_da_attivita(att, payload["stato"], ora, ora))
        return attivita_id

    raise RuntimeError("Scrittura non configurata")


def salva_attivita_diario(
    conn: GSheetsConnection,
    operatore: str,
    campo: str,
    attivita: str,
    note: str,
    cultura: str = "",
    prodotto: str = "",
    mezzo: str = "",
) -> None:
    """Retrocompatibilità: salvataggio immediato concluso."""
    registra_attivita_completa(conn, operatore, campo, attivita, note, cultura, prodotto, mezzo)


def salva_operatore_su_foglio(
    nome: str,
    cognome: str = "",
    telefono: str = "",
    note: str = "",
) -> None:
    payload = {
        "tipo": "operatore",
        "data": _ora_adesso(),
        "nome": nome,
        "cognome": cognome,
        "telefono": telefono,
        "note": note,
        "attivo": "Si",
    }

    if get_webapp_url():
        _post_webapp(payload)
        return

    raise RuntimeError("Scrittura su Google Sheets non configurata")

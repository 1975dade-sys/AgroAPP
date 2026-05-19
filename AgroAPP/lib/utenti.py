"""Gestione utenti: titolare e operatori con accesso."""
import json
import re
import uuid
from datetime import datetime
from pathlib import Path

from lib.password_util import hash_password, verifica_password

UTENTI_PATH = Path(__file__).resolve().parent.parent / "data" / "utenti.json"
OPERATORI_LEGACY = Path(__file__).resolve().parent.parent / "data" / "operatori.json"

RUOLO_TITOLARE = "titolare"
RUOLO_OPERATORE = "operatore"


def _ensure_file() -> None:
    UTENTI_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not UTENTI_PATH.exists():
        UTENTI_PATH.write_text("[]", encoding="utf-8")


def carica_utenti(solo_attivi: bool = True) -> list[dict]:
    _ensure_file()
    utenti: list[dict] = json.loads(UTENTI_PATH.read_text(encoding="utf-8"))
    if solo_attivi:
        return [u for u in utenti if u.get("attivo", True)]
    return utenti


def _salva_tutti(utenti: list[dict]) -> None:
    _ensure_file()
    UTENTI_PATH.write_text(json.dumps(utenti, ensure_ascii=False, indent=2), encoding="utf-8")


def ha_titolare() -> bool:
    return any(u.get("ruolo") == RUOLO_TITOLARE and u.get("attivo", True) for u in carica_utenti(False))


def _normalizza_username(username: str) -> str:
    username = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9._-]{3,32}", username):
        raise ValueError(
            "Username non valido: usa 3-32 caratteri (lettere, numeri, punto, trattino)."
        )
    return username


def _username_libero(username: str, escluso_id: str | None = None) -> bool:
    """True se nessun utente *attivo* usa già questo username (gli eliminati/disattivati non bloccano)."""
    for u in carica_utenti(solo_attivi=False):
        if not u.get("attivo", True):
            continue
        if escluso_id and u["id"] == escluso_id:
            continue
        if u.get("username", "").lower() == username.lower():
            return False
    return True


def etichetta_utente(user: dict) -> str:
    nome = user.get("nome", "").strip()
    cognome = user.get("cognome", "").strip()
    return f"{nome} {cognome}".strip() if cognome else nome


def get_utente(user_id: str) -> dict | None:
    for u in carica_utenti(solo_attivi=False):
        if u["id"] == user_id:
            return u
    return None


def migra_operatori_legacy() -> None:
    """Importa vecchio operatori.json come operatori senza login (il titolare assegnerà accesso)."""
    if not OPERATORI_LEGACY.exists():
        return
    utenti = carica_utenti(solo_attivi=False)
    esistenti = {etichetta_utente(u).lower() for u in utenti}
    for op in json.loads(OPERATORI_LEGACY.read_text(encoding="utf-8")):
        et = f"{op.get('nome', '')} {op.get('cognome', '')}".strip()
        if not et or et.lower() in esistenti:
            continue
        utenti.append(
            {
                "id": op.get("id") or str(uuid.uuid4()),
                "ruolo": RUOLO_OPERATORE,
                "nome": op.get("nome", "").strip(),
                "cognome": op.get("cognome", "").strip(),
                "mansione": "",
                "username": "",
                "password_hash": "",
                "telefono": op.get("telefono", ""),
                "note": op.get("note", ""),
                "attivo": op.get("attivo", True),
                "accesso_attivo": False,
                "creato_il": op.get("creato_il", datetime.now().strftime("%Y-%m-%d %H:%M")),
            }
        )
        esistenti.add(et.lower())
    _salva_tutti(utenti)


def registra_titolare(
    nome: str,
    cognome: str,
    username: str,
    password: str,
    mansione: str = "Titolare",
) -> dict:
    if ha_titolare():
        raise ValueError("Il titolare è già registrato.")

    nome = nome.strip()
    cognome = cognome.strip()
    if not nome:
        raise ValueError("Il nome è obbligatorio.")
    if len(password) < 6:
        raise ValueError("La password deve avere almeno 6 caratteri.")

    username = _normalizza_username(username)
    if not _username_libero(username):
        raise ValueError("Username già in uso.")

    titolare = {
        "id": str(uuid.uuid4()),
        "ruolo": RUOLO_TITOLARE,
        "nome": nome,
        "cognome": cognome,
        "mansione": mansione.strip() or "Titolare",
        "username": username,
        "password_hash": hash_password(password),
        "telefono": "",
        "note": "",
        "attivo": True,
        "accesso_attivo": True,
        "creato_il": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    # Mantiene operatori già presenti (es. dopo reset solo del titolare)
    utenti = [
        u for u in carica_utenti(solo_attivi=False) if u.get("ruolo") != RUOLO_TITOLARE
    ]
    utenti.append(titolare)
    _salva_tutti(utenti)
    migra_operatori_legacy()
    from lib.cloud_sync import sync_utente

    sync_utente(titolare)
    return titolare


def elimina_account_titolare(password: str, titolare_id: str) -> None:
    """
    Rimuove il titolare da `utenti.json` dopo verifica password.
    Gli operatori restano; serve un nuovo titolare (schermata di registrazione).
    """
    password = (password or "").strip()
    if not password:
        raise ValueError("Inserisci la tua password per confermare.")

    utenti = carica_utenti(solo_attivi=False)
    eliminato: dict | None = None
    resto: list[dict] = []
    for u in utenti:
        if u["id"] == titolare_id and u.get("ruolo") == RUOLO_TITOLARE:
            eliminato = dict(u)
            continue
        resto.append(u)
    if eliminato is None:
        raise ValueError("Account titolare non trovato.")

    ph = eliminato.get("password_hash") or ""
    if not ph or not verifica_password(password, ph):
        raise ValueError("Password non corretta.")

    _salva_tutti(resto)
    from lib.cloud_sync import registra_audit_account

    registra_audit_account(
        eliminato,
        "TITOLARE_ELIMINATO",
        "Account titolare eliminato dall'app (conferma password)",
    )


def aggiungi_operatore(
    nome: str,
    cognome: str,
    mansione: str,
    username: str,
    password: str,
    telefono: str = "",
    note: str = "",
) -> dict:
    nome = nome.strip()
    cognome = cognome.strip()
    if not nome:
        raise ValueError("Il nome è obbligatorio.")
    if not mansione.strip():
        raise ValueError("La mansione è obbligatoria.")
    if len(password) < 6:
        raise ValueError("La password deve avere almeno 6 caratteri.")

    username = _normalizza_username(username)
    if not _username_libero(username):
        raise ValueError("Username già in uso.")

    etichetta_nuova = f"{nome} {cognome}".strip().lower()
    for u in carica_utenti(solo_attivi=False):
        if etichetta_utente(u).lower() == etichetta_nuova and u.get("attivo", True):
            raise ValueError("Questo operatore è già presente.")

    nuovo = {
        "id": str(uuid.uuid4()),
        "ruolo": RUOLO_OPERATORE,
        "nome": nome,
        "cognome": cognome,
        "mansione": mansione.strip(),
        "username": username,
        "password_hash": hash_password(password),
        "telefono": telefono.strip(),
        "note": note.strip(),
        "attivo": True,
        "accesso_attivo": True,
        "creato_il": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    utenti = carica_utenti(solo_attivi=False)
    utenti.append(nuovo)
    _salva_tutti(utenti)
    from lib.cloud_sync import sync_utente

    sync_utente(nuovo)
    return nuovo


def imposta_password_operatore(operatore_id: str, nuova_password: str) -> bool:
    if len(nuova_password) < 6:
        raise ValueError("La password deve avere almeno 6 caratteri.")
    utenti = carica_utenti(solo_attivi=False)
    trovato = False
    u_mod: dict | None = None
    for u in utenti:
        if u["id"] == operatore_id and u.get("ruolo") == RUOLO_OPERATORE:
            u["password_hash"] = hash_password(nuova_password)
            u["accesso_attivo"] = True
            if not u.get("username"):
                raise ValueError("Assegna prima uno username all'operatore.")
            trovato = True
            u_mod = u
            break
    if trovato and u_mod is not None:
        _salva_tutti(utenti)
        from lib.cloud_sync import registra_audit_account, sync_utente

        registra_audit_account(u_mod, "PASSWORD_MODIFICATA", "Password aggiornata dal titolare")
        sync_utente(u_mod)
    return trovato


def revoca_accesso_operatore(operatore_id: str) -> bool:
    utenti = carica_utenti(solo_attivi=False)
    trovato = False
    u_mod: dict | None = None
    for u in utenti:
        if u["id"] == operatore_id and u.get("ruolo") == RUOLO_OPERATORE:
            u["accesso_attivo"] = False
            u["password_hash"] = ""
            trovato = True
            u_mod = u
            break
    if trovato and u_mod is not None:
        _salva_tutti(utenti)
        from lib.cloud_sync import registra_audit_account, sync_utente

        registra_audit_account(u_mod, "ACCESSO_REVOCATO", "Login disabilitato dal titolare")
        sync_utente(u_mod)
    return trovato


def disattiva_operatore(operatore_id: str) -> bool:
    """
    Rimuove definitivamente l'operatore da `utenti.json` (stesso nome e username
    possono essere riutilizzati). Traccia l'evento su mirror / «Account_Modifiche».
    """
    utenti = carica_utenti(solo_attivi=False)
    eliminato: dict | None = None
    resto: list[dict] = []
    for u in utenti:
        if u["id"] == operatore_id and u.get("ruolo") == RUOLO_OPERATORE:
            eliminato = dict(u)
            continue
        resto.append(u)
    if eliminato is None:
        return False
    _salva_tutti(resto)
    from lib.cloud_sync import registra_audit_account

    registra_audit_account(
        eliminato,
        "OPERATORE_ELIMINATO",
        "Operatore eliminato definitivamente dall'app",
    )
    return True


def operatori_per_anagrafica(solo_attivi: bool = True) -> list[dict]:
    utenti = carica_utenti(solo_attivi=solo_attivi)
    return [u for u in utenti if u.get("ruolo") == RUOLO_OPERATORE]


def autentica(username: str, password: str) -> dict | None:
    username = username.strip().lower()
    for u in carica_utenti(solo_attivi=True):
        if u.get("username", "").lower() != username:
            continue
        if not u.get("accesso_attivo", False):
            return None
        if not u.get("password_hash"):
            return None
        if verifica_password(password, u["password_hash"]):
            return u
    return None

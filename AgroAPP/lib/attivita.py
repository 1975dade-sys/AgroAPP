import json
import uuid
from datetime import datetime
from pathlib import Path

from lib.campi import formatta_campi, normalizza_campi

ATTIVITA_PATH = Path(__file__).resolve().parent.parent / "data" / "attivita_in_corso.json"


def _ensure_file() -> None:
    ATTIVITA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not ATTIVITA_PATH.exists():
        ATTIVITA_PATH.write_text("[]", encoding="utf-8")


def carica_in_corso() -> list[dict]:
    _ensure_file()
    attivita: list[dict] = json.loads(ATTIVITA_PATH.read_text(encoding="utf-8"))
    return sorted(attivita, key=lambda a: a.get("iniziata_il", ""), reverse=True)


def _salva_tutte(attivita: list[dict]) -> None:
    _ensure_file()
    ATTIVITA_PATH.write_text(
        json.dumps(attivita, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def avvia_attivita(
    operatore: str,
    campi: list[str] | str,
    attivita: str,
    note: str = "",
    cultura: str = "",
    prodotto: str = "",
    mezzo: str = "",
) -> dict:
    operatore = operatore.strip()
    attivita = attivita.strip()
    lista_campi = normalizza_campi(campi)

    if not operatore or operatore == "Seleziona un nome":
        raise ValueError("Seleziona un operatore.")
    if not lista_campi:
        raise ValueError("Seleziona almeno un campo.")
    if not attivita:
        raise ValueError("Seleziona un tipo di attività.")

    nuova = {
        "id": str(uuid.uuid4()),
        "operatore": operatore,
        "campi": lista_campi,
        "campo": formatta_campi(lista_campi),
        "cultura": (cultura or "").strip(),
        "prodotto": (prodotto or "").strip(),
        "mezzo": (mezzo or "").strip(),
        "attivita": attivita,
        "note": (note or "").strip(),
        "iniziata_il": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    tutte = carica_in_corso()
    tutte.insert(0, nuova)
    _salva_tutte(tutte)
    return nuova


def get_attivita(attivita_id: str) -> dict | None:
    for att in carica_in_corso():
        if att["id"] == attivita_id:
            return att
    return None


def aggiorna_note(attivita_id: str, note: str) -> bool:
    tutte = carica_in_corso()
    trovata = False
    for att in tutte:
        if att["id"] == attivita_id:
            att["note"] = note.strip()
            trovata = True
            break
    if trovata:
        _salva_tutte(tutte)
    return trovata


def termina_attivita(attivita_id: str) -> dict | None:
    tutte = carica_in_corso()
    rimossa = None
    restanti = []
    for att in tutte:
        if att["id"] == attivita_id and rimossa is None:
            rimossa = att
        else:
            restanti.append(att)
    if rimossa:
        _salva_tutte(restanti)
    return rimossa


def durata_da_inizio(iniziata_il: str) -> str:
    try:
        inizio = datetime.strptime(iniziata_il, "%Y-%m-%d %H:%M")
    except ValueError:
        return "—"
    delta = datetime.now() - inizio
    minuti = int(delta.total_seconds() // 60)
    if minuti < 1:
        return "appena avviata"
    if minuti < 60:
        return f"{minuti} min"
    ore, m = divmod(minuti, 60)
    if ore < 24:
        return f"{ore} h {m} min" if m else f"{ore} h"
    giorni, ore_r = divmod(ore, 24)
    return f"{giorni} g {ore_r} h"

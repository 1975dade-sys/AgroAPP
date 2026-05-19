import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Callable


def _carica(path: Path) -> list[dict]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))


def _salva(path: Path, voci: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(voci, ensure_ascii=False, indent=2), encoding="utf-8")


def carica_voci(path: Path, solo_attivi: bool = True) -> list[dict]:
    voci = _carica(path)
    if solo_attivi:
        return [v for v in voci if v.get("attivo", True)]
    return voci


def etichetta_voce(voce: dict, campo: str = "nome") -> str:
    return voce.get(campo, "").strip()


def opzioni_select(
    path: Path,
    placeholder: str,
    campo_etichetta: str = "nome",
    extra_inizio: list[str] | None = None,
) -> list[str]:
    inizio = extra_inizio or []
    etichette = [etichetta_voce(v, campo_etichetta) for v in carica_voci(path)]
    return [placeholder] + inizio + etichette


def aggiungi_voce(
    path: Path,
    dati: dict,
    campo_unico: str = "nome",
    messaggio_duplicato: str = "Voce già presente.",
) -> dict:
    valore = dati.get(campo_unico, "").strip()
    if not valore:
        raise ValueError(f"Il campo «{campo_unico}» è obbligatorio.")

    voci = carica_voci(path, solo_attivi=False)
    for v in voci:
        if v.get("attivo", True) and etichetta_voce(v, campo_unico).lower() == valore.lower():
            raise ValueError(messaggio_duplicato)

    nuova = {
        "id": str(uuid.uuid4()),
        "attivo": True,
        "creato_il": datetime.now().strftime("%Y-%m-%d %H:%M"),
        **dati,
    }
    voci.append(nuova)
    _salva(path, voci)
    return nuova


def disattiva_voce(path: Path, voce_id: str) -> bool:
    voci = carica_voci(path, solo_attivi=False)
    trovata = False
    for v in voci:
        if v["id"] == voce_id:
            v["attivo"] = False
            trovata = True
            break
    if trovata:
        _salva(path, voci)
    return trovata

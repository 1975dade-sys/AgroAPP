"""Mezzi agricoli: trattori, attrezzi trainati, altre macchine."""
from pathlib import Path

from lib.anagrafica_base import (
    aggiungi_voce,
    carica_voci,
    disattiva_voce,
    etichetta_voce,
    opzioni_select,
)

MEZZI_PATH = Path(__file__).resolve().parent.parent / "data" / "mezzi_agricoli.json"
PLACEHOLDER = "Seleziona un mezzo"


def carica_mezzi(solo_attivi: bool = True) -> list[dict]:
    return carica_voci(MEZZI_PATH, solo_attivi=solo_attivi)


def opzioni_selectbox_diario() -> list[str]:
    return opzioni_select(MEZZI_PATH, PLACEHOLDER)


def etichetta_mezzo(mezzo: dict) -> str:
    return etichetta_voce(mezzo, "nome")


def aggiungi_mezzo(
    nome: str,
    marca: str = "",
    modello: str = "",
    targa_identificativo: str = "",
    note: str = "",
) -> tuple[dict, str | None]:
    nuovo = aggiungi_voce(
        MEZZI_PATH,
        {
            "nome": (nome or "").strip(),
            "marca": (marca or "").strip(),
            "modello": (modello or "").strip(),
            "targa_identificativo": (targa_identificativo or "").strip(),
            "note": (note or "").strip(),
        },
    )
    from lib.cloud_sync import sync_mezzo_agricolo

    err = sync_mezzo_agricolo(nuovo)
    return nuovo, err


def disattiva_mezzo(mezzo_id: str) -> bool:
    return disattiva_voce(MEZZI_PATH, mezzo_id)

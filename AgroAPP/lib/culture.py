from pathlib import Path

from lib.anagrafica_base import (
    aggiungi_voce,
    carica_voci,
    disattiva_voce,
    etichetta_voce,
    opzioni_select,
)

CULTURE_PATH = Path(__file__).resolve().parent.parent / "data" / "culture.json"
PLACEHOLDER = "Seleziona una cultura"


def carica_culture(solo_attivi: bool = True) -> list[dict]:
    return carica_voci(CULTURE_PATH, solo_attivi=solo_attivi)


def opzioni_selectbox_diario() -> list[str]:
    return opzioni_select(CULTURE_PATH, PLACEHOLDER)


def aggiungi_cultura(nome: str, prodotto_semina: str = "", note: str = "") -> dict:
    nuova = aggiungi_voce(
        CULTURE_PATH,
        {
            "nome": (nome or "").strip(),
            "prodotto_semina": (prodotto_semina or "").strip(),
            "note": (note or "").strip(),
        },
    )
    from lib.cloud_sync import sync_cultura

    sync_cultura(nuova)
    return nuova


def disattiva_cultura(cultura_id: str) -> bool:
    return disattiva_voce(CULTURE_PATH, cultura_id)


def etichetta_cultura(cultura: dict) -> str:
    nome = etichetta_voce(cultura)
    semina = cultura.get("prodotto_semina", "").strip()
    if semina:
        return f"{nome} — semina: {semina}"
    return nome

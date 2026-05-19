from pathlib import Path

from lib.anagrafica_base import (
    aggiungi_voce,
    carica_voci,
    disattiva_voce,
    etichetta_voce,
    opzioni_select,
)

PRODOTTI_PATH = Path(__file__).resolve().parent.parent / "data" / "prodotti.json"
PLACEHOLDER = "Seleziona un prodotto"
CATEGORIE = ["Seme", "Fitosanitario", "Fertilizzante", "Altro"]


def carica_prodotti(solo_attivi: bool = True) -> list[dict]:
    return carica_voci(PRODOTTI_PATH, solo_attivi=solo_attivi)


def opzioni_selectbox_diario() -> list[str]:
    return opzioni_select(PRODOTTI_PATH, PLACEHOLDER)


def aggiungi_prodotto(nome: str, categoria: str = "Altro", note: str = "") -> dict:
    nuova = aggiungi_voce(
        PRODOTTI_PATH,
        {
            "nome": (nome or "").strip(),
            "categoria": (categoria or "Altro").strip(),
            "note": (note or "").strip(),
        },
    )
    from lib.cloud_sync import sync_prodotto

    sync_prodotto(nuova)
    return nuova


def disattiva_prodotto(prodotto_id: str) -> bool:
    return disattiva_voce(PRODOTTI_PATH, prodotto_id)


def etichetta_prodotto(prodotto: dict) -> str:
    nome = etichetta_voce(prodotto)
    cat = prodotto.get("categoria", "")
    return f"{nome} ({cat})" if cat else nome

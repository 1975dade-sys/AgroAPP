from pathlib import Path

from lib.anagrafica_base import (
    aggiungi_voce,
    carica_voci,
    disattiva_voce,
    etichetta_voce,
    opzioni_select,
)

CAMPI_PATH = Path(__file__).resolve().parent.parent / "data" / "campi.json"
PLACEHOLDER = "Seleziona il campo"
SEPARATORE_CAMPI = " · "


def _seed_iniziale() -> None:
    if CAMPI_PATH.exists():
        return
    for nome in (
        "Campo Nord (Vigna)",
        "Campo Sud (Mais)",
        "Appezzamento Est (Uliveto)",
    ):
        aggiungi_voce(CAMPI_PATH, {"nome": nome, "note": ""})


def carica_campi(solo_attivi: bool = True) -> list[dict]:
    _seed_iniziale()
    return carica_voci(CAMPI_PATH, solo_attivi=solo_attivi)


def opzioni_selectbox_diario() -> list[str]:
    _seed_iniziale()
    return opzioni_select(CAMPI_PATH, PLACEHOLDER)


def opzioni_multiselect() -> list[str]:
    """Elenco campi selezionabili (senza placeholder)."""
    return [o for o in opzioni_selectbox_diario() if o != PLACEHOLDER]


def aggiungi_campo(nome: str, note: str = "") -> dict:
    nuova = aggiungi_voce(
        CAMPI_PATH,
        {"nome": (nome or "").strip(), "note": (note or "").strip()},
    )
    from lib.cloud_sync import sync_campo

    sync_campo(nuova)
    return nuova


def disattiva_campo(campo_id: str) -> bool:
    return disattiva_voce(CAMPI_PATH, campo_id)


def etichetta_campo(campo: dict) -> str:
    return etichetta_voce(campo)


def normalizza_campi(campi: list[str] | str | None) -> list[str]:
    """Converte input singolo o multiplo in lista di nomi campo."""
    if campi is None:
        return []
    if isinstance(campi, str):
        testo = campi.strip()
        if not testo or testo == PLACEHOLDER:
            return []
        if SEPARATORE_CAMPI in testo:
            return [p.strip() for p in testo.split(SEPARATORE_CAMPI) if p.strip()]
        return [testo]
    return [c.strip() for c in campi if c and str(c).strip() and str(c) != PLACEHOLDER]


def formatta_campi(campi: list[str] | str | None) -> str:
    """Testo unico per foglio Google e visualizzazione."""
    lista = normalizza_campi(campi)
    return SEPARATORE_CAMPI.join(lista)


def campi_da_record(record: dict) -> list[str]:
    """Legge i campi da un'attività (nuovo o vecchio formato)."""
    if record.get("campi"):
        return normalizza_campi(record["campi"])
    return normalizza_campi(record.get("campo", ""))

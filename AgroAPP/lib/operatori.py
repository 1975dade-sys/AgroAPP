"""Operatori agricoli — wrapper su lib.utenti."""
from lib.utenti import (
    aggiungi_operatore,
    disattiva_operatore,
    etichetta_utente,
    imposta_password_operatore,
    operatori_per_anagrafica,
    revoca_accesso_operatore,
)

# Re-export per compatibilità
etichetta_operatore = etichetta_utente
carica_operatori = operatori_per_anagrafica


def opzioni_selectbox_diario() -> list[str]:
    con_accesso = [
        o
        for o in operatori_per_anagrafica(solo_attivi=True)
        if o.get("accesso_attivo") and o.get("username")
    ]
    return ["Seleziona un nome"] + [etichetta_utente(o) for o in con_accesso]

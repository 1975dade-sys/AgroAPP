import streamlit as st

from lib.auth import richiede_titolare
from lib.anagrafica_pagina import render_pagina_anagrafica
from lib.campi import aggiungi_campo, carica_campi, disattiva_campo, etichetta_campo
from lib.mobile import submit_operazione

richiede_titolare()


def _form() -> None:
    with st.form("form_campo", clear_on_submit=True):
        nome = st.text_input("Nome campo *", placeholder="Es. Campo Nord (Vigna)")
        note = st.text_area("Note", placeholder="Ettari, tipo terreno, irrigazione…")
        inviato = submit_operazione("Aggiungi campo", type="primary", use_container_width=True)
    if inviato:
        try:
            nuovo = aggiungi_campo(nome, note)
            st.success(f"Aggiunto: {etichetta_campo(nuovo)}")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Errore: {exc}")


def _dettaglio(voce: dict) -> None:
    if voce.get("note"):
        st.caption(voce["note"])


render_pagina_anagrafica(
    "🗺️ Campi",
    "Appezzamenti e campi coltivati dell'azienda.",
    "campo",
    carica_campi,
    disattiva_campo,
    _form,
    _dettaglio,
    etichetta_campo,
)

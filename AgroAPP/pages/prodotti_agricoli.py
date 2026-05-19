import streamlit as st

from lib.auth import richiede_titolare
from lib.anagrafica_pagina import render_pagina_anagrafica
from lib.mobile import submit_operazione
from lib.prodotti import CATEGORIE, aggiungi_prodotto, carica_prodotti, disattiva_prodotto, etichetta_prodotto

richiede_titolare()


def _form() -> None:
    with st.form("form_prodotto", clear_on_submit=True):
        nome = st.text_input("Nome prodotto *", placeholder="Es. Mais ibrido P123")
        categoria = st.selectbox("Categoria", CATEGORIE)
        note = st.text_area("Note", placeholder="Fornitore, dosaggi, lotto…")
        inviato = submit_operazione("Aggiungi prodotto", type="primary", use_container_width=True)
    if inviato:
        try:
            nuovo = aggiungi_prodotto(nome, categoria, note)
            st.success(f"Aggiunto: {etichetta_prodotto(nuovo)}")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def _dettaglio(voce: dict) -> None:
    if voce.get("note"):
        st.caption(voce["note"])


render_pagina_anagrafica(
    "📦 Prodotti agricoli",
    "Semi, fitosanitari, fertilizzanti e altri prodotti usati in azienda.",
    "prodotto",
    carica_prodotti,
    disattiva_prodotto,
    _form,
    _dettaglio,
    etichetta_prodotto,
)

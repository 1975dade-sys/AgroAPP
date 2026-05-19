import streamlit as st

from lib.mobile import bottone_operazione, submit_operazione

__all__ = ["bottone_operazione", "intestazione_pagina", "sezione_in_sviluppo", "submit_operazione"]


def intestazione_pagina(titolo: str, sottotitolo: str = "") -> None:
    st.title(titolo)
    if sottotitolo:
        st.caption(sottotitolo)


def sezione_in_sviluppo(
    titolo: str,
    descrizione: str,
    funzionalita: list[str],
) -> None:
    intestazione_pagina(titolo, descrizione)
    st.info("Sezione in preparazione — il menu è pronto, i moduli verranno aggiunti qui.")
    st.markdown("**Funzionalità previste:**")
    for voce in funzionalita:
        st.markdown(f"- {voce}")

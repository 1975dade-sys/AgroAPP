"""Barra superiore compatta per desktop e smartphone."""
import streamlit as st

from lib.auth import etichetta_utente, logout, utente_corrente
from lib.info_app import render_titolo_agroapp
from lib.utenti import RUOLO_TITOLARE


def render_barra_superiore() -> None:
    user = utente_corrente() or {}
    ruolo = user.get("ruolo", "")
    icona = "👑" if ruolo == RUOLO_TITOLARE else "🧑‍🌾"
    mansione = user.get("mansione", "")

    render_titolo_agroapp(livello=3)

    c_utente, c_esci = st.columns([5, 1])
    with c_utente:
        dettaglio = f"**{icona} {etichetta_utente(user)}**"
        if mansione:
            st.markdown(f"{dettaglio}  \n{mansione} · {ruolo.capitalize()}")
        else:
            st.markdown(dettaglio)
    with c_esci:
        if st.button("Esci", key="logout_top", use_container_width=True):
            logout()
            st.rerun()

    st.divider()

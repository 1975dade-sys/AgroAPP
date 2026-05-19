"""Intestazione sidebar: titolo app e account loggato."""
import streamlit as st

from lib.auth import etichetta_utente, logout, utente_corrente, utente_loggato
from lib.info_app import render_titolo_agroapp
from lib.utenti import RUOLO_TITOLARE

__all__ = ["render_intestazione_sidebar"]


def _etichetta_ruolo(ruolo: str) -> tuple[str, str]:
    if ruolo == RUOLO_TITOLARE:
        return "Titolare", "👑"
    return "Operatore", "🧑‍🌾"


def render_intestazione_sidebar(*, mostra_account: bool = True, mostra_logout: bool = True) -> None:
    """Titolo e account in cima alla sidebar (usa sempre st.sidebar)."""
    render_titolo_agroapp(livello=3, in_sidebar=True)

    if not mostra_account or not utente_loggato():
        return

    user = utente_corrente() or {}
    ruolo = user.get("ruolo", "")
    ruolo_label, ruolo_icon = _etichetta_ruolo(ruolo)
    mansione = (user.get("mansione") or "").strip()
    nome = etichetta_utente(user)

    with st.sidebar.container(border=True):
        st.caption("Account connesso")
        st.markdown(f"### {ruolo_icon} {nome}")
        st.markdown(f"**{ruolo_label}**")
        if mansione:
            st.caption(mansione)

    if mostra_logout and st.sidebar.button(
        "Esci dall'account",
        key="esci_sidebar",
        use_container_width=True,
        type="secondary",
    ):
        logout()
        st.rerun()

"""Layout condiviso per le pagine di gestione anagrafiche."""
from collections.abc import Callable

import streamlit as st

from lib.mobile import bottone_operazione, prepara_layout_operativo


def render_pagina_anagrafica(
    titolo: str,
    sottotitolo: str,
    nome_voce: str,
    carica_fn: Callable,
    disattiva_fn: Callable,
    render_form: Callable[[], None],
    render_dettaglio: Callable[[dict], None],
    etichetta_fn: Callable[[dict], str],
) -> None:
    prepara_layout_operativo()
    st.title(titolo)
    st.caption(sottotitolo)
    st.divider()

    col_form, col_lista = st.columns([1, 1])

    with col_form:
        st.subheader(f"Nuovo {nome_voce}")
        render_form()

    with col_lista:
        st.subheader(f"Elenco {nome_voce}")
        voci = carica_fn(solo_attivi=True)
        if not voci:
            st.info(f"Nessun {nome_voce} inserito. Aggiungi il primo dal modulo a sinistra.")
        else:
            st.caption(f"{len(voci)} attivi")
            for voce in voci:
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**{etichetta_fn(voce)}**")
                    render_dettaglio(voce)
                with c2:
                    if bottone_operazione(
                        "Rimuovi", key=f"rimuovi_{voce['id']}", use_container_width=True
                    ):
                        disattiva_fn(voce["id"])
                        st.rerun()

    st.divider()
    with st.expander(f"{nome_voce.capitalize()} disattivati"):
        disattivati = [v for v in carica_fn(solo_attivi=False) if not v.get("attivo", True)]
        if disattivati:
            for voce in disattivati:
                st.text(f"{etichetta_fn(voce)} — disattivato il {voce.get('creato_il', '')}")
        else:
            st.caption(f"Nessun {nome_voce} disattivato.")

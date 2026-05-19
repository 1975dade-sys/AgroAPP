import streamlit as st

from lib.auth import richiede_titolare
from lib.anagrafica_pagina import render_pagina_anagrafica
from lib.culture import aggiungi_cultura, carica_culture, disattiva_cultura, etichetta_cultura
from lib.mobile import submit_operazione
from lib.prodotti import carica_prodotti, etichetta_prodotto

richiede_titolare()


def _opzioni_prodotto_semina() -> list[str]:
    return [""] + [etichetta_prodotto(p) for p in carica_prodotti()]


def _form() -> None:
    with st.form("form_cultura", clear_on_submit=True):
        nome = st.text_input("Nome cultura *", placeholder="Es. Mais, Vite, Grano turco")
        prodotti = _opzioni_prodotto_semina()
        prodotto_idx = st.selectbox(
            "Prodotto da seminare",
            range(len(prodotti)),
            format_func=lambda i: prodotti[i] or "— Nessuno / da definire —",
        )
        prodotto_semina = prodotti[prodotto_idx]
        note = st.text_area(
            "Note",
            placeholder="Varietà, appezzamento previsto, epoca di semina…",
        )
        inviato = submit_operazione("Aggiungi cultura", type="primary", use_container_width=True)
    if inviato:
        try:
            nuovo = aggiungi_cultura(nome, prodotto_semina, note)
            st.success(f"Aggiunta: {etichetta_cultura(nuovo)}")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


def _dettaglio(voce: dict) -> None:
    righe = []
    if voce.get("prodotto_semina"):
        righe.append(f"🌱 Semina: {voce['prodotto_semina']}")
    if voce.get("note"):
        righe.append(voce["note"])
    if righe:
        st.caption(" · ".join(righe))


render_pagina_anagrafica(
    "🌱 Cultura",
    "Colture e prodotto previsto per la semina.",
    "cultura",
    carica_culture,
    disattiva_cultura,
    _form,
    _dettaglio,
    etichetta_cultura,
)

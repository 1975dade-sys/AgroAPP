import streamlit as st

from lib.auth import richiede_titolare
from lib.anagrafica_pagina import render_pagina_anagrafica
from lib.mezzi_agricoli import (
    aggiungi_mezzo,
    carica_mezzi,
    disattiva_mezzo,
    etichetta_mezzo,
)
from lib.mobile import submit_operazione

richiede_titolare()


def _form() -> None:
    with st.form("form_mezzo", clear_on_submit=True):
        nome = st.text_input(
            "Nome mezzo *",
            placeholder="Es. Trattore principale, Rimorchio vasca, Atomizzatore",
        )
        marca = st.text_input("Marca", placeholder="Es. John Deere, New Holland")
        modello = st.text_input("Modello", placeholder="Es. 6120M, T7.210")
        targa = st.text_input(
            "Targa / matricola / numero interno",
            placeholder="Targa, telaio o codice interno aziendale",
        )
        note = st.text_area(
            "Note",
            placeholder="Potenza, anno, attacchi, manutenzioni, assicurazione…",
        )
        inviato = submit_operazione("Aggiungi mezzo", type="primary", use_container_width=True)
    if inviato:
        try:
            nuovo, err_cloud = aggiungi_mezzo(nome, marca, modello, targa, note)
            st.success(f"Aggiunto: {etichetta_mezzo(nuovo)}")
            if err_cloud:
                st.warning(f"Salvato in locale; tabella Google (Anagrafica_Mezzi_Agricoli): {err_cloud}")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Errore: {exc}")


def _dettaglio(voce: dict) -> None:
    righe = []
    if voce.get("marca") or voce.get("modello"):
        righe.append(" ".join(p for p in (voce.get("marca", ""), voce.get("modello", "")) if p).strip())
    if voce.get("targa_identificativo"):
        righe.append(f"🔖 {voce['targa_identificativo']}")
    if voce.get("note"):
        righe.append(voce["note"])
    if righe:
        st.caption(" · ".join(righe))


render_pagina_anagrafica(
    "🚜 Mezzi agricoli",
    "Trattori, attrezzi trainati e altre macchine: elenco locale e riga su Google Sheets (se collegato).",
    "mezzo",
    carica_mezzi,
    disattiva_mezzo,
    _form,
    _dettaglio,
    etichetta_mezzo,
)

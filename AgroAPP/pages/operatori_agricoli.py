import streamlit as st

from lib.auth import richiede_titolare
from lib.gsheet import salva_operatore_su_foglio, scrittura_abilitata
from lib.operatori import (
    aggiungi_operatore,
    carica_operatori,
    disattiva_operatore,
    etichetta_operatore,
    imposta_password_operatore,
    revoca_accesso_operatore,
)
from lib.mobile import prepara_layout_operativo
from lib.mobile import bottone_operazione, submit_operazione
from lib.ui import intestazione_pagina

richiede_titolare()
prepara_layout_operativo()

intestazione_pagina(
    "🧑‍🌾 Operatori agricoli",
    "Crea account per il personale: mansione, username e password (solo tu puoi modificarli o revocarli).",
)

if scrittura_abilitata():
    st.caption(
        "Ogni nuovo operatore viene salvato in **locale** (`data/utenti.json`), copiato nel **mirror** "
        "(`data/mirror/`) e, se il foglio è collegato, su **Google Sheets** (schede «Operatori agricoli», «Account_Utenti»; "
        "«Account_Modifiche» per password, revoche ed eliminazioni operatori). "
        "Aggiorna lo script in **Estensioni → Apps Script** con il codice del progetto (`apps_script/Code.gs`) e **ridistribuisci** l'app web."
    )

st.divider()

col_form, col_lista = st.columns([1, 1])

with col_form:
    st.subheader("Nuovo operatore con accesso")
    with st.form("form_operatore", clear_on_submit=True):
        nome = st.text_input("Nome *", placeholder="Es. Marco")
        cognome = st.text_input("Cognome *", placeholder="Es. Rossi")
        mansione = st.text_input("Mansione *", placeholder="Es. Trattorista, Capo campo")
        username = st.text_input("Username login *", placeholder="es. marco.rossi")
        password = st.text_input("Password iniziale *", type="password")
        telefono = st.text_input("Telefono", placeholder="Es. 333 1234567")
        note = st.text_area("Note", placeholder="Patente, specializzazioni...")
        inviato = submit_operazione("Crea operatore", type="primary", use_container_width=True)

    if inviato:
        try:
            nuovo = aggiungi_operatore(nome, cognome, mansione, username, password, telefono, note)
            if scrittura_abilitata():
                try:
                    salva_operatore_su_foglio(
                        nuovo["nome"],
                        nuovo["cognome"],
                        nuovo["telefono"],
                        nuovo["note"],
                    )
                except Exception as exc:
                    st.warning(f"Operatore salvato in app, errore foglio: {exc}")
            st.success(
                f"Creato **{etichetta_operatore(nuovo)}** · login `{nuovo['username']}`"
            )
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Errore: {exc}")

with col_lista:
    st.subheader("Elenco operatori")
    st.caption(
        "In ogni scheda il pulsante **Elimina definitivamente** è in alto; "
        "scorri in basso per password e revoca accesso."
    )
    operatori = carica_operatori(solo_attivi=True)

    if not operatori:
        st.info("Nessun operatore attivo. Crea il primo account a sinistra, oppure controlla sotto «Operatori disattivati».")
    else:
        for op in operatori:
            with st.container(border=True):
                accesso = "🟢 Accesso attivo" if op.get("accesso_attivo") else "🔴 Accesso revocato"
                st.markdown(f"**{etichetta_operatore(op)}** · {op.get('mansione', '')}")
                st.caption(
                    f"Login: `{op.get('username') or '—'}` · {accesso} · 📞 {op.get('telefono') or '—'}"
                )
                if op.get("note"):
                    st.caption(op["note"])

                st.markdown("###### Rimuovi dall'app")
                st.caption("Eliminazione definitiva da questo computer; potrai ricreare stesso nome e username.")
                if bottone_operazione(
                    "🗑️ Elimina definitivamente",
                    key=f"rimuovi_{op['id']}",
                    type="secondary",
                ):
                    disattiva_operatore(op["id"])
                    st.success("Operatore eliminato: puoi ricrearlo con lo stesso nome e username.")
                    st.rerun()

                st.markdown("###### Password e accesso")
                nuova_pwd = st.text_input(
                    "Nuova password",
                    type="password",
                    key=f"pwd_{op['id']}",
                    placeholder="Solo il titolare può reimpostarla",
                )
                if bottone_operazione("Salva password", key=f"save_pwd_{op['id']}"):
                    try:
                        imposta_password_operatore(op["id"], nuova_pwd)
                        st.success("Password aggiornata.")
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
                if bottone_operazione("Revoca accesso", key=f"rev_{op['id']}"):
                    revoca_accesso_operatore(op["id"])
                    st.warning("Accesso revocato.")
                    st.rerun()

st.divider()
with st.expander("Operatori disattivati (solo dati legacy)"):
    disattivati = [o for o in carica_operatori(solo_attivi=False) if not o.get("attivo", True)]
    if disattivati:
        st.caption(
            "Record ancora presenti da versioni precedenti dell'app. "
            "Usa **Elimina definitivamente** per toglierli del tutto da `utenti.json`."
        )
        for op in disattivati:
            with st.container(border=True):
                st.markdown(f"**{etichetta_operatore(op)}** · disattivato")
                st.caption(f"Login: `{op.get('username') or '—'}`")
                if bottone_operazione(
                    "🗑️ Elimina definitivamente",
                    key=f"rimuovi_legacy_{op['id']}",
                    type="secondary",
                ):
                    disattiva_operatore(op["id"])
                    st.success("Operatore eliminato dall'archivio.")
                    st.rerun()
    else:
        st.caption("Nessun record disattivato in archivio.")

import streamlit as st

from lib.auth import esegui_login, ruolo_da_tipo_accesso, utente_loggato, widget_esci_account
from lib.info_app import render_titolo_agroapp
from lib.mobile import submit_operazione
from lib.theme_ui import render_selettore_tema
from lib.utenti import ha_titolare

if not ha_titolare():
    st.rerun()

render_titolo_agroapp(livello=2)
render_selettore_tema(compatto=True)

if utente_loggato():
    widget_esci_account(key="esci_login")
    st.stop()

st.markdown("---")
st.caption("Seleziona il tipo di accesso e inserisci le tue credenziali.")

tipo_accesso = st.radio(
    "Accedi come",
    ["Titolare", "Operatore"],
    key="login_tipo_accesso",
    help="Il titolare usa l'account creato alla registrazione; gli operatori quello assegnato dal titolare.",
)

if tipo_accesso == "Titolare":
    st.info(
        "Accesso **titolare**: username e password scelti alla prima registrazione dell'azienda. "
        "Da qui gestisci anagrafiche, campi e account del personale."
    )
else:
    st.info(
        "Accesso **operatore**: usa username e password **forniti dal titolare**. "
        "Potrai avviare e chiudere le lavorazioni sulle anagrafiche già configurate."
    )

with st.form("login"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    inviato = submit_operazione("Accedi", type="primary", use_container_width=True)

if inviato:
    ruolo_atteso = ruolo_da_tipo_accesso(tipo_accesso)
    esito = esegui_login(username.strip(), password, ruolo_atteso)
    if esito == "ok":
        st.rerun()
    elif esito == "wrong_role":
        altro = "Operatore" if tipo_accesso == "Titolare" else "Titolare"
        st.error(
            f"Hai selezionato **{tipo_accesso}**, ma queste credenziali appartengono a un **{altro}**. "
            f"Cambia il selettore in alto e riprova."
        )
    else:
        if tipo_accesso == "Titolare":
            st.error("Username o password del titolare non corretti.")
        else:
            st.error(
                "Username o password non corretti, oppure accesso revocato dal titolare."
            )

st.divider()
st.caption(
    "Primo accesso titolare: usa **Titolare** con le credenziali create in registrazione. "
    "Gli operatori devono avere username e password assegnati dal titolare in *Operatori agricoli*."
)

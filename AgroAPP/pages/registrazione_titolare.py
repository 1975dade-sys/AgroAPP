import streamlit as st

from lib.auth import imposta_sessione
from lib.info_app import render_titolo_agroapp
from lib.mobile import submit_operazione
from lib.utenti import ha_titolare, registra_titolare

if ha_titolare():
    st.rerun()

render_titolo_agroapp(livello=2)
st.caption("Primo avvio — crea l'account del titolare dell'azienda.")
st.info(
    "Il titolare configura anagrafiche, campi e credenziali degli operatori. "
    "Gli operatori potranno solo avviare e chiudere le lavorazioni."
)

with st.form("reg_titolare"):
    nome = st.text_input("Nome *")
    cognome = st.text_input("Cognome *")
    mansione = st.text_input("Mansione", value="Titolare")
    username = st.text_input("Username per il login *", placeholder="es. mario.rossi")
    password = st.text_input("Password *", type="password")
    password2 = st.text_input("Ripeti password *", type="password")
    inviato = submit_operazione("Crea account titolare", type="primary", use_container_width=True)

if inviato:
    if password != password2:
        st.error("Le password non coincidono.")
    else:
        try:
            user = registra_titolare(nome, cognome, username, password, mansione)
            imposta_sessione(user)
            st.session_state["flash_home"] = (
                f"Benvenuto **{nome}**! Configura le anagrafiche dal menu in alto."
            )
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Errore: {exc}")

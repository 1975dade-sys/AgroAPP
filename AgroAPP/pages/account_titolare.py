import streamlit as st

from lib.auth import logout, richiede_titolare, utente_corrente
from lib.mobile import prepara_layout_operativo, submit_operazione
from lib.ui import intestazione_pagina
from lib.utenti import elimina_account_titolare, etichetta_utente

richiede_titolare()
prepara_layout_operativo()

user = utente_corrente() or {}

intestazione_pagina(
    "⚙️ Account titolare",
    "Gestione dell'account titolare su questo dispositivo.",
)

st.markdown(f"**Account:** {etichetta_utente(user)} · `{(user.get('username') or '—')}`")

st.warning(
    "**Eliminazione definitiva:** uscirai dall'app e dovrai **registrare di nuovo un titolare**. "
    "Gli **operatori** presenti in `data/utenti.json` restano salvati in locale. "
    "Il **foglio Google** non viene modificato automaticamente da questa azione."
)

with st.form("form_elimina_titolare"):
    pwd = st.text_input(
        "Conferma con la tua password titolare *",
        type="password",
        placeholder="Password attuale",
    )
    invia = submit_operazione(
        "Elimina definitivamente il mio account titolare",
        type="secondary",
    )

if invia:
    uid = user.get("id")
    if not uid:
        st.error("Sessione non valida.")
    else:
        try:
            elimina_account_titolare(pwd, str(uid))
            logout()
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

"""Autenticazione e sessione utente."""

import streamlit as st



from lib.utenti import RUOLO_OPERATORE, RUOLO_TITOLARE, autentica, ha_titolare



SESSION_KEY = "agroapp_user"





def utente_corrente() -> dict | None:

    return st.session_state.get(SESSION_KEY)





def utente_loggato() -> bool:

    return utente_corrente() is not None





def e_titolare() -> bool:

    user = utente_corrente()

    return bool(user and user.get("ruolo") == RUOLO_TITOLARE)





def e_operatore() -> bool:

    user = utente_corrente()

    return bool(user and user.get("ruolo") != RUOLO_TITOLARE)





def etichetta_utente(user: dict | None = None) -> str:

    user = user or utente_corrente() or {}

    nome = user.get("nome", "").strip()

    cognome = user.get("cognome", "").strip()

    if cognome:

        return f"{nome} {cognome}".strip()

    return nome





def imposta_sessione(user: dict) -> None:

    st.session_state[SESSION_KEY] = {

        "id": user["id"],

        "ruolo": user["ruolo"],

        "nome": user.get("nome", ""),

        "cognome": user.get("cognome", ""),

        "username": user.get("username", ""),

        "mansione": user.get("mansione", ""),

    }





def logout() -> None:

    st.session_state.pop(SESSION_KEY, None)





def widget_esci_account(*, in_sidebar: bool = False, key: str = "esci") -> None:

    """Mostra utente connesso e pulsante per uscire (pagina login, non sidebar)."""

    if not utente_loggato():

        return

    user = utente_corrente()

    ruolo = (user or {}).get("ruolo", "")

    if in_sidebar:
        from lib.header_ui import render_barra_superiore

        render_barra_superiore()
        return

    ruolo_label = "Titolare" if ruolo == RUOLO_TITOLARE else "Operatore"

    ruolo_icon = "👑" if ruolo == RUOLO_TITOLARE else "🧑‍🌾"

    st.success(

        f"Sei connesso come **{ruolo_icon} {etichetta_utente(user)}** ({ruolo_label})"

    )

    st.caption("Esci per provare un altro accesso (titolare o operatore).")

    if st.button(

        "Esci dall'account",

        key=key,

        use_container_width=True,

        type="primary",

    ):

        logout()

        st.rerun()





def richiede_login() -> None:

    if not ha_titolare() or not utente_loggato():

        st.rerun()





def richiede_titolare() -> None:

    richiede_login()

    if not e_titolare():

        st.error("Accesso riservato al titolare dell'azienda.")

        st.stop()





def esegui_login(username: str, password: str, ruolo_atteso: str | None = None) -> str:

    """Restituisce 'ok', 'invalid' o 'wrong_role'."""

    user = autentica(username, password)

    if not user:

        return "invalid"

    if ruolo_atteso and user.get("ruolo") != ruolo_atteso:

        return "wrong_role"

    imposta_sessione(user)

    return "ok"





def ruolo_da_tipo_accesso(tipo: str) -> str:

    if tipo == "Titolare":

        return RUOLO_TITOLARE

    return RUOLO_OPERATORE


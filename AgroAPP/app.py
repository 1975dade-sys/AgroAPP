import streamlit as st

from lib.auth import e_titolare, utente_loggato
from lib.header_ui import render_barra_superiore
from lib.mobile import configura_mobile, nascondi_sidebar
from lib.utenti import ha_titolare

# Pulisce eventuale stato del vecchio drawer
for _chiave in ("agroapp_drawer_aperto", "agroapp_collassa_sidebar"):
    st.session_state.pop(_chiave, None)
if "menu" in st.query_params:
    del st.query_params["menu"]

if not ha_titolare():
    layout = "centered"
elif not utente_loggato():
    layout = "centered"
else:
    layout = "wide"

st.set_page_config(
    page_title="AgroApp",
    page_icon="🌾",
    layout=layout,
    initial_sidebar_state="collapsed",
)

configura_mobile()

if not ha_titolare():
    nascondi_sidebar()
    st.navigation(
        [st.Page("pages/registrazione_titolare.py", title="Registrazione", icon="🔐")],
        position="hidden",
    ).run()
    st.stop()

if not utente_loggato():
    nascondi_sidebar()
    st.navigation(
        [st.Page("pages/login.py", title="Accesso", icon="🔑")],
        position="hidden",
    ).run()
    st.stop()

nascondi_sidebar()
render_barra_superiore()

menu_principale = [
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/diario.py", title="Diario", icon="📋"),
]
if e_titolare():
    menu_principale.append(
        st.Page("pages/account_titolare.py", title="Account", icon="⚙️"),
    )

menu_anagrafiche = []
if e_titolare():
    menu_anagrafiche = [
        st.Page("pages/campi.py", title="Campi", icon="🗺️"),
        st.Page("pages/cultura.py", title="Cultura", icon="🌱"),
        st.Page("pages/prodotti_agricoli.py", title="Prodotti", icon="📦"),
        st.Page("pages/operatori_agricoli.py", title="Operatori", icon="🧑‍🌾"),
        st.Page("pages/mezzi_agricoli.py", title="Mezzi agricoli", icon="🚜"),
    ]

menu = {"Principale": menu_principale}
if menu_anagrafiche:
    menu["Anagrafiche"] = menu_anagrafiche

st.navigation(menu, position="top", expanded=False).run()

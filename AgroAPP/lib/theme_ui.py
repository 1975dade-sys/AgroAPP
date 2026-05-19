"""Tema chiaro/scuro senza menu Streamlit (utile su PWA Android/iOS)."""
import streamlit as st

_TEMA_CHIARO = {
    "background": "#ffffff",
    "secondary": "#f0f7f4",
    "text": "#1b4332",
}
_TEMA_SCURO = {
    "background": "#0e1117",
    "secondary": "#262730",
    "text": "#fafafa",
}


def tema_corrente() -> str:
    t = st.session_state.get("agroapp_theme", "light")
    return "dark" if t == "dark" else "light"


def applica_tema_css() -> str:
    """CSS che sovrascrive i colori Streamlit in base alla scelta utente."""
    if tema_corrente() == "dark":
        c = _TEMA_SCURO
    else:
        c = _TEMA_CHIARO
    return f"""
    <style id="agroapp-theme-css">
    .stApp {{
      color-scheme: {"dark" if tema_corrente() == "dark" else "light"};
      --background-color: {c["background"]};
      --secondary-background-color: {c["secondary"]};
      --text-color: {c["text"]};
    }}
    .stApp, section.main, [data-testid="stAppViewContainer"] {{
      background-color: {c["background"]} !important;
      color: {c["text"]} !important;
    }}
  </style>
    """


def render_selettore_tema(*, compatto: bool = False) -> None:
    """Pulsanti tema visibili anche senza menu ⋮ Streamlit."""
    attuale = tema_corrente()
    if compatto:
        c1, c2 = st.columns(2)
    else:
        st.markdown("**Aspetto**")
        c1, c2 = st.columns(2)
    with c1:
        if st.button(
            "☀️ Chiaro",
            key="tema_chiaro",
            type="primary" if attuale == "light" else "secondary",
            use_container_width=True,
        ):
            st.session_state["agroapp_theme"] = "light"
            st.rerun()
    with c2:
        if st.button(
            "🌙 Scuro",
            key="tema_scuro",
            type="primary" if attuale == "dark" else "secondary",
            use_container_width=True,
        ):
            st.session_state["agroapp_theme"] = "dark"
            st.rerun()


"""Branding e versione AgroApp — unico stile in tutta l'app."""
import streamlit as st

VERSIONE = "1.0beta"
CREDITO = "By H.S.C. di Davide Capato"


def _misure(livello: int) -> dict[str, str]:
    if livello <= 2:
        return {
            "name": "2.15rem",
            "badge": "3.5rem",
            "emoji": "1.7rem",
            "meta": "0.92rem",
        }
    return {
        "name": "1.9rem",
        "badge": "3.15rem",
        "emoji": "1.55rem",
        "meta": "0.88rem",
    }


def _css_brand() -> str:
    return """
    <style id="agroapp-brand-css">
    .agroapp-brand-wrap {
      display: inline-flex;
      max-width: 100%;
      margin: 0 0 0.5rem 0;
      padding: 0.85rem 1.25rem 0.9rem 1rem;
      border-radius: 18px;
      border: 1px solid rgba(128, 128, 128, 0.25);
      border-left: 4px solid #2d6a4f;
      background: var(--secondary-background-color, #f0f7f4);
      font-family: system-ui, -apple-system, sans-serif;
    }
    .agroapp-brand-name {
      margin: 0;
      font-weight: 800;
      color: var(--text-color, #1b4332);
    }
    .agroapp-brand-meta {
      margin: 0.35rem 0 0 0;
      color: var(--text-color, #1b4332);
      opacity: 0.85;
    }
    .agroapp-brand-badge-icon {
      border-radius: 16px;
      background: linear-gradient(145deg, #1b4332, #52b788);
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .agroapp-brand-version {
      font-weight: 700;
      color: #fff;
      font-size: 0.78rem;
      background: #2d6a4f;
      padding: 0.12rem 0.55rem;
      border-radius: 6px;
    }
    </style>
    """


def _html_brand(*, livello: int) -> str:
    m = _misure(livello)
    return (
        f'<div class="agroapp-brand-wrap">'
        f'<div style="display:flex;align-items:center;gap:0.9rem;">'
        f'<div class="agroapp-brand-badge-icon" style="width:{m["badge"]};height:{m["badge"]};'
        f'font-size:{m["emoji"]};">🌾</div>'
        f'<div><p class="agroapp-brand-name" style="font-size:{m["name"]};">AgroApp</p>'
        f'<p class="agroapp-brand-meta" style="font-size:{m["meta"]};">'
        f'{CREDITO} - <span class="agroapp-brand-version">{VERSIONE}</span></p></div>'
        f'</div></div>'
    )


def inietta_css_brand() -> None:
    st.markdown(_css_brand(), unsafe_allow_html=True)


def render_titolo_agroapp(*, livello: int = 3, in_sidebar: bool = False) -> None:
    """Intestazione AgroApp (compatibile Streamlit Cloud)."""
    target = st.sidebar if in_sidebar else st
    html = _html_brand(livello=livello)
    try:
        if hasattr(target, "html"):
            target.html(html)
        else:
            target.markdown(html, unsafe_allow_html=True)
    except Exception:
        target.markdown(f"### 🌾 AgroApp\n*{CREDITO}* · `{VERSIONE}`")

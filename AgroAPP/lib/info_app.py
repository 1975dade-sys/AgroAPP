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
      border-left: 4px solid var(--primary-color, #2d6a4f);
      background: var(--secondary-background-color);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
      font-family: system-ui, -apple-system, sans-serif;
      box-sizing: border-box;
    }
    .agroapp-brand-name {
      margin: 0;
      padding: 0;
      font-weight: 800;
      line-height: 1.05;
      letter-spacing: -0.04em;
      color: var(--text-color);
    }
    .agroapp-brand-meta {
      margin: 0.35rem 0 0 0;
      padding: 0;
      line-height: 1.3;
      color: var(--text-color);
      opacity: 0.85;
      font-weight: 500;
    }
    .agroapp-brand-meta-sep {
      margin: 0 0.4rem;
      opacity: 0.45;
    }
    .agroapp-brand-badge-icon {
      border-radius: 16px;
      flex-shrink: 0;
      background: linear-gradient(145deg, #1b4332 0%, #2d6a4f 40%, #52b788 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
      box-shadow: 0 4px 12px rgba(45, 106, 79, 0.35);
    }
    .agroapp-brand-version {
      font-weight: 700;
      color: #fff !important;
      font-size: 0.78rem;
      letter-spacing: 0.04em;
      background: linear-gradient(135deg, #2d6a4f, #40916c);
      padding: 0.12rem 0.55rem;
      border-radius: 6px;
    }
    </style>
    """


def _html_brand(*, livello: int) -> str:
    m = _misure(livello)
    return f"""
<div class="agroapp-brand-wrap">
  <div style="display:flex;align-items:center;gap:0.9rem;min-width:0;">
    <div class="agroapp-brand-badge-icon" style="
      width:{m['badge']};height:{m['badge']};font-size:{m['emoji']};
    ">🌾</div>
    <div style="display:flex;flex-direction:column;align-items:flex-start;min-width:0;">
      <p class="agroapp-brand-name" style="font-size:{m['name']};">AgroApp</p>
      <p class="agroapp-brand-meta" style="font-size:{m['meta']};">
        <span>{CREDITO}</span>
        <span class="agroapp-brand-meta-sep">-</span>
        <span class="agroapp-brand-version">{VERSIONE}</span>
      </p>
    </div>
  </div>
</div>
""".strip()


def inietta_css_brand() -> None:
    """CSS intestazione AgroApp (leggibile in tema chiaro e scuro)."""
    st.markdown(_css_brand(), unsafe_allow_html=True)


def render_titolo_agroapp(*, livello: int = 3, in_sidebar: bool = False) -> None:
    """Intestazione AgroApp (HTML nel DOM principale per ereditare il tema Streamlit)."""
    target = st.sidebar if in_sidebar else st
    target.markdown(_html_brand(livello=livello), unsafe_allow_html=True)
arget.html(html, width="stretch")

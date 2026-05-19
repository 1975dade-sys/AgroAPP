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


def _html_brand(*, livello: int) -> str:
    m = _misure(livello)
    return f"""
<div style="
  display:inline-flex;
  max-width:100%;
  margin:0 0 0.5rem 0;
  padding:0.85rem 1.25rem 0.9rem 0.85rem;
  padding-left:1rem;
  border-radius:18px;
  border:1px solid rgba(45,106,79,0.2);
  border-left:4px solid #2d6a4f;
  background:linear-gradient(145deg,#ffffff 0%,#f0f9f4 48%,#e3f2ea 100%);
  box-shadow:0 2px 4px rgba(27,67,50,0.05),0 8px 24px rgba(45,106,79,0.12);
  font-family:system-ui,-apple-system,sans-serif;
  box-sizing:border-box;
">
  <div style="display:flex;align-items:center;gap:0.9rem;min-width:0;">
    <div style="
      width:{m['badge']};height:{m['badge']};border-radius:16px;flex-shrink:0;
      background:linear-gradient(145deg,#1b4332 0%,#2d6a4f 40%,#52b788 100%);
      display:flex;align-items:center;justify-content:center;
      font-size:{m['emoji']};line-height:1;
      box-shadow:0 4px 12px rgba(45,106,79,0.35),inset 0 1px 0 rgba(255,255,255,0.25);
    ">🌾</div>
    <div style="display:flex;flex-direction:column;align-items:flex-start;min-width:0;">
      <p style="
        margin:0;padding:0;font-size:{m['name']};font-weight:800;line-height:1.05;
        letter-spacing:-0.04em;color:#1b4332;
      ">AgroApp</p>
      <p style="
        margin:0.35rem 0 0 0;padding:0;font-size:{m['meta']};line-height:1.3;
        color:#4d6b5f;font-weight:500;
      ">
        <span>{CREDITO}</span>
        <span style="margin:0 0.4rem;color:#8fb39f;">-</span>
        <span style="
          font-weight:700;color:#fff;font-size:0.78rem;letter-spacing:0.04em;
          background:linear-gradient(135deg,#2d6a4f,#40916c);
          padding:0.12rem 0.55rem;border-radius:6px;
          box-shadow:0 1px 4px rgba(45,106,79,0.25);
        ">{VERSIONE}</span>
      </p>
    </div>
  </div>
</div>
""".strip()


def inietta_css_brand() -> None:
    """Compatibilità: stili ora inline nel blocco HTML."""
    return


def render_titolo_agroapp(*, livello: int = 3, in_sidebar: bool = False) -> None:
    """Intestazione AgroApp (sempre visibile con st.html)."""
    html = _html_brand(livello=livello)
    target = st.sidebar if in_sidebar else st
    target.html(html, width="stretch")

"""Supporto smartphone: PWA, CSS responsive, pulsanti touch-friendly."""
import streamlit as st
import streamlit.components.v1 as components

_BREAKPOINT = "768px"


def _css_responsive() -> str:
    return f"""
    <style id="agroapp-mobile-css">
    :root {{
      --agroapp-touch: 48px;
      --agroapp-pad: 0.75rem;
      --agroapp-green: #2d6a4f;
    }}

    /* Evita zoom automatico su iOS quando si tocca un campo */
    input, textarea, select {{
      font-size: 16px !important;
    }}

    .stButton > button,
    .stFormSubmitButton > button,
    .stLinkButton > a {{
      min-height: var(--agroapp-touch);
      border-radius: 10px;
      font-size: 1rem;
    }}

    [data-testid="stMetric"] {{
      background: #f0f7f4;
      border-radius: 12px;
      padding: 0.65rem 0.85rem;
    }}

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {{
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      max-width: 100%;
    }}

    /* Il primo wrapper interno spesso clippa la griglia se non ha overflow */
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataEditor"] > div {{
      max-width: 100%;
      overflow-x: auto !important;
      -webkit-overflow-scrolling: touch;
    }}

    #agroapp-install-banner {{
      padding-bottom: max(12px, env(safe-area-inset-bottom));
    }}

    @media (max-width: {_BREAKPOINT}) {{
      section.main .block-container {{
        padding-top: 0.75rem !important;
        padding-left: var(--agroapp-pad) !important;
        padding-right: var(--agroapp-pad) !important;
        padding-bottom: calc(5.5rem + env(safe-area-inset-bottom)) !important;
        max-width: 100% !important;
      }}

      [data-testid="stAppViewContainer"] {{
        padding-top: env(safe-area-inset-top);
      }}

      /* Colonne affiancate → impilate (form + elenchi, metriche, azioni) */
      div[data-testid="stHorizontalBlock"] {{
        flex-wrap: wrap !important;
        gap: 0.35rem !important;
      }}
      div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {{
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 0 !important;
      }}

      /* Eccezione: due pulsanti affiancati restano in riga se stretti */
      div[data-testid="stHorizontalBlock"].agroapp-row-2 > div[data-testid="column"] {{
        width: calc(50% - 0.25rem) !important;
        flex: 1 1 calc(50% - 0.25rem) !important;
      }}

      h1 {{ font-size: 1.45rem !important; }}
      h2 {{ font-size: 1.2rem !important; }}
      h3 {{ font-size: 1.05rem !important; }}

      [data-testid="stMetric"] label {{
        font-size: 0.8rem !important;
      }}
      [data-testid="stMetric"] [data-testid="stMetricValue"] {{
        font-size: 1.35rem !important;
      }}

      /* Radio orizzontali → colonna (login, esito lavorazione) */
      div[data-testid="stRadio"] > div {{
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 0.35rem !important;
      }}
      div[data-testid="stRadio"] label {{
        min-height: var(--agroapp-touch);
        padding: 0.5rem 0.75rem !important;
        border-radius: 10px;
        background: #f8faf9;
      }}

      /* Menu in alto: scorrimento orizzontale */
      header[data-testid="stHeader"] {{
        background: #fff;
        border-bottom: 1px solid #e8efe9;
      }}
      header[data-testid="stHeader"] [data-testid="stToolbar"] {{
        max-width: 100%;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        flex-wrap: nowrap !important;
      }}
      header[data-testid="stHeader"] a,
      header[data-testid="stHeader"] button {{
        white-space: nowrap;
        font-size: 0.9rem !important;
      }}

      /* Select e multiselect più alti */
      [data-baseweb="select"] > div {{
        min-height: var(--agroapp-touch);
      }}

      /* Contenitori attività */
      [data-testid="stVerticalBlockBorderWrapper"] {{
        margin-bottom: 0.75rem;
      }}
    }}
    </style>
    """


def nascondi_sidebar() -> None:
    """Nasconde la sidebar laterale: navigazione in alto."""
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
          display: none !important;
        }
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
          margin-left: 0 !important;
          max-width: 100% !important;
        }
        section.main {
          padding-top: 0.25rem !important;
        }
        #agroapp-backdrop-link,
        #agroapp-menu-fab,
        #agroapp-menu-fab-link,
        #agroapp-drawer-backdrop {
          display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def applica_stili_responsive() -> None:
    st.markdown(_css_responsive(), unsafe_allow_html=True)


def bottone_operazione(label: str, **kwargs) -> bool:
    kwargs.setdefault("use_container_width", True)
    return st.button(label, **kwargs)


def submit_operazione(label: str, **kwargs) -> bool:
    kwargs.setdefault("use_container_width", True)
    return st.form_submit_button(label, **kwargs)


def tabella_mobile(df, *, altezza: int = 280, **kwargs) -> None:
    """Tabella con scroll orizzontale e altezza limitata su smartphone."""
    kwargs.setdefault("use_container_width", False)
    kwargs.setdefault("hide_index", True)
    kwargs.setdefault("height", altezza)
    st.dataframe(df, **kwargs)


def prepara_layout_operativo() -> None:
    """Spazio extra in fondo per banner PWA e pollici."""
    st.markdown(
        '<div class="agroapp-pagina-campo" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )


def configura_mobile() -> None:
    applica_stili_responsive()
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;
          const head = doc.head;
          if (head.querySelector('meta[data-agroapp-viewport]')) {
            doc.body.classList.remove('agroapp-drawer-open');
            return;
          }

          const base = win.location.origin;

          function addLink(rel, href) {
            const el = doc.createElement('link');
            el.rel = rel;
            el.href = href;
            el.setAttribute('data-agroapp-pwa', '1');
            head.appendChild(el);
          }

          function addMeta(name, content, extra) {
            const el = doc.createElement('meta');
            el.name = name;
            el.content = content;
            if (extra) el.setAttribute(extra, '1');
            el.setAttribute('data-agroapp-pwa', '1');
            head.appendChild(el);
          }

          addMeta(
            'viewport',
            'width=device-width, initial-scale=1, viewport-fit=cover',
            'data-agroapp-viewport'
          );
          addLink('manifest', base + '/static/manifest.json');
          addLink('apple-touch-icon', base + '/static/apple-touch-icon.png');
          addMeta('mobile-web-app-capable', 'yes');
          addMeta('apple-mobile-web-app-capable', 'yes');
          addMeta('apple-mobile-web-app-status-bar-style', 'black-translucent');
          addMeta('apple-mobile-web-app-title', 'AgroApp');
          addMeta('theme-color', '#2d6a4f');
          addMeta('format-detection', 'telephone=no');

          if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register(base + '/static/sw.js', { scope: '/' })
              .catch(function () {});
          }

          let deferredPrompt = null;
          if (!doc.getElementById('agroapp-install-banner')) {
            const banner = doc.createElement('div');
            banner.id = 'agroapp-install-banner';
            banner.innerHTML =
              '<span>Installa AgroApp sulla schermata Home</span>' +
              '<button type="button" id="agroapp-install-btn">Installa</button>';
            banner.style.cssText =
              'display:none;position:fixed;bottom:0;left:0;right:0;z-index:99999;' +
              'background:#2d6a4f;color:#fff;padding:12px 16px;padding-bottom:max(12px,env(safe-area-inset-bottom));' +
              'font-family:system-ui,sans-serif;font-size:14px;box-shadow:0 -2px 12px rgba(0,0,0,0.2);' +
              'align-items:center;justify-content:space-between;gap:12px;';

            doc.body.appendChild(banner);

            const btn = doc.getElementById('agroapp-install-btn');
            btn.style.cssText =
              'background:#fff;color:#2d6a4f;border:none;padding:10px 18px;' +
              'min-height:44px;border-radius:10px;font-weight:600;cursor:pointer;';

            win.addEventListener('beforeinstallprompt', function (e) {
              e.preventDefault();
              deferredPrompt = e;
              banner.style.display = 'flex';
            });

            btn.addEventListener('click', function () {
              if (!deferredPrompt) return;
              deferredPrompt.prompt();
              deferredPrompt.userChoice.then(function () {
                banner.style.display = 'none';
                deferredPrompt = null;
              });
            });
          }

          doc.body.classList.remove('agroapp-drawer-open');
        })();
        </script>
        """,
        height=0,
        width=0,
    )

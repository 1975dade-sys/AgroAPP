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

    /* Allineamento a tema chiaro/scuro Streamlit (variabili ufficiali) */
    [data-testid="stMetric"] {{
      background: var(--secondary-background-color) !important;
      border-radius: 12px;
      padding: 0.65rem 0.85rem;
      border: 1px solid rgba(128, 128, 128, 0.2);
    }}
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {{
      color: var(--text-color) !important;
    }}

    [data-testid="stCaptionContainer"],
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li {{
      color: var(--text-color);
    }}

    div[data-testid="stRadio"] label {{
      color: var(--text-color) !important;
      background: var(--secondary-background-color) !important;
    }}

    header[data-testid="stHeader"] {{
      background: var(--background-color) !important;
      border-bottom: 1px solid rgba(128, 128, 128, 0.25);
    }}
    header[data-testid="stHeader"] a,
    header[data-testid="stHeader"] button {{
      color: var(--text-color) !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
      border-color: rgba(128, 128, 128, 0.25) !important;
    }}

    /* Footer / branding Streamlit sempre nascosto */
    footer,
    [data-testid="stFooter"],
    [data-testid="stStatusWidget"],
    [data-testid="stToolbarActions"],
    .stDeployButton {{
      display: none !important;
      visibility: hidden !important;
      height: 0 !important;
      width: 0 !important;
      opacity: 0 !important;
      pointer-events: none !important;
    }}

    /* Smartphone e PWA (Aggiungi a Home): nascondi tutta la barra Streamlit in alto */
    @media (max-width: {_BREAKPOINT}), (display-mode: standalone) {{
      header[data-testid="stHeader"] {{
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden !important;
        pointer-events: none !important;
      }}
      [data-testid="stAppViewContainer"] {{
        top: 0 !important;
      }}
      section.main .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: calc(6.5rem + env(safe-area-inset-bottom)) !important;
      }}
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
      }}

      /* Menu in alto: scorrimento orizzontale */
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
    from lib.info_app import inietta_css_brand
    from lib.theme_ui import applica_tema_css

    applica_stili_responsive()
    st.markdown(applica_tema_css(), unsafe_allow_html=True)
    inietta_css_brand()
    components.html(
        """
        <script>
        (function () {
          const win = window.parent;
          const doc = win.document;
          const head = doc.head;

          function hideStreamlitChrome() {
            const mobile = win.matchMedia('(max-width: 768px)').matches;
            const standalone = win.matchMedia('(display-mode: standalone)').matches;
            const pwa = mobile || standalone;
            const sel = [
              'footer',
              '[data-testid="stFooter"]',
              '[data-testid="stStatusWidget"]',
              '[data-testid="stToolbarActions"]',
              '.stDeployButton'
            ].join(',');
            doc.querySelectorAll(sel).forEach(function (el) {
              el.style.setProperty('display', 'none', 'important');
              el.style.setProperty('pointer-events', 'none', 'important');
              el.style.setProperty('height', '0', 'important');
              el.style.setProperty('opacity', '0', 'important');
            });
            if (pwa) {
              var hdr = doc.querySelector('header[data-testid="stHeader"]');
              if (hdr) {
                hdr.style.setProperty('display', 'none', 'important');
                hdr.style.setProperty('height', '0', 'important');
                hdr.style.setProperty('pointer-events', 'none', 'important');
              }
            }
            doc.querySelectorAll('a[href*="streamlit.io"], a[href*="share.streamlit"]').forEach(function (a) {
              if (!a.closest('section.main')) {
                a.style.setProperty('display', 'none', 'important');
                a.style.setProperty('pointer-events', 'none', 'important');
              }
            });
            doc.querySelectorAll('button, a, div').forEach(function (el) {
              if (el.closest('section.main')) return;
              var t = (el.textContent || '').trim();
              if (t.indexOf('Made with Streamlit') >= 0 || t === 'Deploy') {
                el.style.setProperty('display', 'none', 'important');
                el.style.setProperty('pointer-events', 'none', 'important');
              }
              try {
                var st = win.getComputedStyle(el);
                if ((st.position === 'fixed' || st.position === 'sticky') &&
                    parseFloat(st.bottom) >= 0 && parseFloat(st.bottom) < 120) {
                  var h = (el.getAttribute('href') || '') + t;
                  if (h.indexOf('streamlit') >= 0 || el.querySelector('[data-testid="stLogo"]')) {
                    el.style.setProperty('display', 'none', 'important');
                    el.style.setProperty('pointer-events', 'none', 'important');
                  }
                }
              } catch (e) {}
            });
          }
          hideStreamlitChrome();
          win.addEventListener('resize', hideStreamlitChrome);
          if (win.MutationObserver && doc.body) {
            new win.MutationObserver(hideStreamlitChrome).observe(doc.body, {
              childList: true,
              subtree: true
            });
          }

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

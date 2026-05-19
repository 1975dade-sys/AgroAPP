from datetime import datetime

import streamlit as st

from lib.auth import richiede_login
from lib.mobile import bottone_operazione, prepara_layout_operativo, tabella_mobile
from lib.attivita import carica_in_corso, durata_da_inizio, termina_attivita
from lib.campi import campi_da_record, formatta_campi
from lib.gsheet import carica_gsheet, chiudi_attivita_registro, get_conn, scrittura_abilitata
from lib.stati import STATO_ANNULLATA, STATO_CONCLUSA, STATO_PROBLEMI

richiede_login()
prepara_layout_operativo()

conn = get_conn()

if msg := st.session_state.pop("flash_home", None):
    st.success(msg)

st.header("Panoramica")
st.caption("Le attività vengono registrate sul foglio all'avvio; alla chiusura si aggiornano orario e esito.")

in_corso = carica_in_corso()
n = len(in_corso)

m1, m2, m3 = st.columns(3)
m1.metric("In corso ora", n)
m2.metric(
    "Operatori attivi",
    len({a["operatore"] for a in in_corso}) if in_corso else 0,
)
m3.metric(
    "Campi coinvolti",
    len({c for a in in_corso for c in campi_da_record(a)}) if in_corso else 0,
)

st.divider()

if not in_corso:
    st.info("Nessuna lavorazione in corso al momento.")
    if bottone_operazione("➕ Avvia una nuova attività", type="primary", use_container_width=True):
        st.switch_page("pages/diario.py")
else:
    for att in in_corso:
        with st.container(border=True):
            st.subheader(att["attivita"])
            st.caption("🟢 In corso")
            extra = []
            if att.get("cultura"):
                extra.append(f"🌱 {att['cultura']}")
            if att.get("prodotto"):
                extra.append(f"📦 {att['prodotto']}")
            if att.get("mezzo"):
                extra.append(f"🚜 {att['mezzo']}")
            extra_txt = (" · " + " · ".join(extra)) if extra else ""
            st.markdown(
                f"**{att['operatore']}** · {formatta_campi(campi_da_record(att))}{extra_txt}  \n"
                f"Inizio: **{att.get('iniziata_il', '—')}** · {durata_da_inizio(att.get('iniziata_il', ''))}"
            )

            if att.get("note"):
                st.caption(f"Note iniziali: {att['note']}")

            st.markdown("##### Chiusura lavorazione")
            esito = st.radio(
                "Esito",
                ["Conclusa", "Con problemi"],
                key=f"esito_{att['id']}",
            )
            problemi = ""
            if esito == "Con problemi":
                problemi = st.text_area(
                    "Problemi emersi *",
                    key=f"prob_{att['id']}",
                    placeholder="Descrivi guasti, ritardi, condizioni anomale…",
                )

            note_finale = st.text_area(
                "Note finali (opzionale)",
                value=att.get("note", ""),
                key=f"note_term_{att['id']}",
                placeholder="Es. prodotti usati, resa, osservazioni…",
            )

            if bottone_operazione(
                "✅ Termina lavorazione",
                key=f"term_{att['id']}",
                type="primary",
            ):
                if not scrittura_abilitata():
                    st.error("Collega la scrittura al foglio Google dal Diario attività.")
                elif esito == "Con problemi" and not problemi.strip():
                    st.error("Descrivi i problemi emersi prima di chiudere.")
                else:
                    try:
                        stato = STATO_PROBLEMI if esito == "Con problemi" else STATO_CONCLUSA
                        chiudi_attivita_registro(
                            conn,
                            att["id"],
                            stato,
                            note_finale,
                            problemi.strip(),
                            att=att,
                        )
                        termina_attivita(att["id"])
                        st.success("Lavorazione chiusa e aggiornata sul foglio.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Errore: {exc}")
            if bottone_operazione(
                "Annulla lavorazione",
                key=f"ann_{att['id']}",
            ):
                try:
                    if scrittura_abilitata():
                        chiudi_attivita_registro(
                            conn,
                            att["id"],
                            STATO_ANNULLATA,
                            note_finale or att.get("note", ""),
                            "Annullata dall'operatore",
                            att=att,
                        )
                    termina_attivita(att["id"])
                    st.warning("Lavorazione annullata.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Errore: {exc}")

st.divider()
st.subheader("Ultime registrate oggi")
try:
    registro = carica_gsheet(conn)
    if not registro.empty:
        col_data = "Inizio" if "Inizio" in registro.columns else "Data"
        oggi = datetime.now().strftime("%Y-%m-%d")
        mask = registro[col_data].astype(str).str.startswith(oggi)
        oggi_df = registro[mask].iloc[::-1].head(8)
        if oggi_df.empty:
            st.caption("Nessuna attività registrata oggi sul foglio.")
        else:
            tabella_mobile(oggi_df, altezza=240)
    else:
        st.caption("Nessuna attività nel foglio.")
except Exception:
    st.caption("Collega il foglio Google per vedere lo storico.")

if bottone_operazione("📋 Vai al diario"):
    st.switch_page("pages/diario.py")
if bottone_operazione("🔄 Aggiorna"):
    st.rerun()

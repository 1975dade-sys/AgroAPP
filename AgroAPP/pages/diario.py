import streamlit as st

from lib.anagrafica_ui import (
    bottone_salva_anagrafica,
    multiselect_campi,
    prepara_pannello_inserimento,
    selectbox_anagrafica,
)
from lib.attivita import avvia_attivita, termina_attivita
from lib.campi import aggiungi_campo, formatta_campi, opzioni_multiselect
from lib.culture import aggiungi_cultura, opzioni_selectbox_diario as opzioni_culture
from lib.gsheet import (
    carica_gsheet,
    get_apps_script_ui,
    get_conn,
    registra_inizio_attivita,
    salva_attivita_diario,
    salva_operatore_su_foglio,
    salva_webapp_in_config,
    scrittura_abilitata,
)
from lib.auth import e_titolare, etichetta_utente, richiede_login, utente_corrente
from lib.mobile import bottone_operazione, prepara_layout_operativo, tabella_mobile
from lib.operatori import etichetta_operatore, opzioni_selectbox_diario
from lib.mezzi_agricoli import aggiungi_mezzo, opzioni_selectbox_diario as opzioni_mezzi
from lib.prodotti import CATEGORIE, aggiungi_prodotto, opzioni_selectbox_diario as opzioni_prodotti


def pannello_configurazione_scrittura() -> None:
    st.info(
        "**Situazione:** l'app legge già il foglio Google. "
        "Per **salvare** le attività e **sincronizzare** campi, colture, prodotti e account sul cloud, "
        "completa i passi **una sola volta** (o aggiorna lo script se hai già pubblicato l'app web)."
    )

    st.markdown("### Passo 1 — Apri il foglio")
    st.link_button(
        "Apri il mio foglio Google",
        "https://docs.google.com/spreadsheets/d/1E4sTGusQbi0OCAhdb3DFEpBxdfqBXD3bAvnrSeoRSok/edit",
        use_container_width=True,
    )

    st.markdown(
        """
### Passo 2 — Apri Apps Script
Nel foglio: **Estensioni** → **Apps Script**

### Passo 3 — Incolla il codice e salva
        """
    )
    st.code(get_apps_script_ui(), language="javascript")

    st.markdown(
        """
### Passo 4 — Pubblica l'app web
**Distribuisci** → **Nuova distribuzione** → ⚙️ **App web**  
Esegui come: **Io** · Accesso: **Chiunque** → copia l'URL con `/exec`

### Passo 5 — Incolla l'URL qui
        """
    )

    url = st.text_input(
        "URL App web",
        placeholder="https://script.google.com/macros/s/xxxxxxxx/exec",
        key="input_webapp_url",
    )
    if bottone_operazione("✅ Collega il foglio", type="primary", use_container_width=True):
        if not url.strip().startswith("https://script.google.com/"):
            st.error("L'URL deve iniziare con https://script.google.com/ e finire con /exec")
        else:
            salva_webapp_in_config(url)
            st.success("Fatto! Ora puoi salvare le attività sul foglio.")
            st.rerun()


def _opzionale(valore: str | None) -> str:
    if not valore or str(valore).startswith("Seleziona"):
        return ""
    return str(valore)


def _testo_sessione(key: str) -> str:
    val = st.session_state.get(key)
    return str(val).strip() if val is not None else ""


if st.session_state.pop("vai_home", False):
    st.switch_page("pages/home.py")

richiede_login()
prepara_layout_operativo()
user = utente_corrente()
titolare = e_titolare()

conn = get_conn()

st.header("Diario attività")
st.write("Registra le lavorazioni sul campo: all'avvio si salva l'ora di inizio sul foglio.")

if titolare:
    st.caption("Come titolare puoi aggiungere anagrafiche qui (➕) o dal menu in alto.")
    if scrittura_abilitata():
        st.caption("Foglio Google · lettura e scrittura attive.")
    else:
        pannello_configurazione_scrittura()
        st.divider()
else:
    st.caption("Seleziona le anagrafiche preparate dal titolare.")
    if not scrittura_abilitata():
        st.warning("Il foglio Google non è collegato: chiedi al titolare di completare la configurazione.")

if titolare:
    opzioni_operatore = opzioni_selectbox_diario()
    if len(opzioni_operatore) <= 1:
        st.warning("Nessun operatore con accesso. Creane uno in **Operatori agricoli**.")
    operatore = selectbox_anagrafica("Chi sta inserendo l'attività?", "operatore", opzioni_operatore)
else:
    operatore = etichetta_utente(user)
    st.markdown(f"**Operatore:** {operatore} · {user.get('mansione', '')}")

def _salva_campo_inline() -> str:
    nome = aggiungi_campo(
        _testo_sessione("add_campo_nome"),
        _testo_sessione("add_campo_note"),
    )["nome"]
    st.session_state["prefill_campo_mul"] = nome
    return nome


campi_selezionati = multiselect_campi(
    "In quali campi stai lavorando?",
    "campo",
    opzioni_multiselect(),
)
if titolare:
    prepara_pannello_inserimento("campo", ["add_campo_nome", "add_campo_note"])
    with st.expander("➕ Aggiungi nuovo campo", key="exp_campo"):
        st.text_input("Nome campo *", key="add_campo_nome", placeholder="Es. Campo Nord (Vigna)")
        st.text_area("Note", key="add_campo_note")
        bottone_salva_anagrafica(
            "campo",
            _salva_campo_inline,
            ["add_campo_nome", "add_campo_note"],
            prefill_select=False,
        )

cultura = selectbox_anagrafica("Cultura (opzionale)", "cultura", opzioni_culture())
if titolare:
    prepara_pannello_inserimento(
        "cultura", ["add_cult_nome", "add_cult_semina", "add_cult_note"]
    )
    with st.expander("➕ Aggiungi nuova cultura", key="exp_cultura"):
        st.text_input("Nome cultura *", key="add_cult_nome", placeholder="Es. Mais, Vite")
        st.text_input("Prodotto da seminare", key="add_cult_semina", placeholder="Es. Ibrido P123")
        st.text_area("Note", key="add_cult_note")
        bottone_salva_anagrafica(
            "cultura",
            lambda: aggiungi_cultura(
                _testo_sessione("add_cult_nome"),
                _testo_sessione("add_cult_semina"),
                _testo_sessione("add_cult_note"),
            )["nome"],
            ["add_cult_nome", "add_cult_semina", "add_cult_note"],
        )

prodotto = selectbox_anagrafica("Prodotto agricolo (opzionale)", "prodotto", opzioni_prodotti())
if titolare:
    prepara_pannello_inserimento(
        "prodotto",
        ["add_prod_nome", "add_prod_cat", "add_prod_note"],
        field_defaults={"add_prod_cat": "Altro"},
    )
    with st.expander("➕ Aggiungi nuovo prodotto", key="exp_prodotto"):
        st.text_input("Nome prodotto *", key="add_prod_nome", placeholder="Es. Glifosate 360")
        st.selectbox("Categoria", CATEGORIE, key="add_prod_cat")
        st.text_area("Note", key="add_prod_note")
        bottone_salva_anagrafica(
            "prodotto",
            lambda: aggiungi_prodotto(
                _testo_sessione("add_prod_nome"),
                _testo_sessione("add_prod_cat") or "Altro",
                _testo_sessione("add_prod_note"),
            )["nome"],
            ["add_prod_nome", "add_prod_cat", "add_prod_note"],
            field_defaults={"add_prod_cat": "Altro"},
        )

mezzo = selectbox_anagrafica("Mezzo agricolo (opzionale)", "mezzo", opzioni_mezzi())
if titolare:
    prepara_pannello_inserimento(
        "mezzo",
        ["add_mezzo_nome", "add_mezzo_marca", "add_mezzo_modello", "add_mezzo_targa", "add_mezzo_note"],
    )
    with st.expander("➕ Aggiungi nuovo mezzo", key="exp_mezzo"):
        st.text_input("Nome mezzo *", key="add_mezzo_nome", placeholder="Es. Trattore principale")
        st.text_input("Marca", key="add_mezzo_marca", placeholder="Es. John Deere")
        st.text_input("Modello", key="add_mezzo_modello", placeholder="Es. 6120M")
        st.text_input("Targa / matricola", key="add_mezzo_targa")
        st.text_area("Note", key="add_mezzo_note")
        bottone_salva_anagrafica(
            "mezzo",
            lambda: aggiungi_mezzo(
                _testo_sessione("add_mezzo_nome"),
                _testo_sessione("add_mezzo_marca"),
                _testo_sessione("add_mezzo_modello"),
                _testo_sessione("add_mezzo_targa"),
                _testo_sessione("add_mezzo_note"),
            )[0]["nome"],
            ["add_mezzo_nome", "add_mezzo_marca", "add_mezzo_modello", "add_mezzo_targa", "add_mezzo_note"],
        )

attivita = st.radio(
    "Che tipo di attività stai svolgendo?",
    [
        "Trattamento Fitosanitario",
        "Lavorazione Terreno / Aratura",
        "Semina",
        "Irrigazione",
        "Raccolta",
        "Manutenzione Mezzi",
    ],
)

note = st.text_area("Note aggiuntive (es. dosi, condizioni meteo, guasti):")

cultura_val = _opzionale(cultura)
prodotto_val = _opzionale(prodotto)
mezzo_val = _opzionale(mezzo)

if bottone_operazione("▶ Avvia lavorazione", type="primary"):
    try:
        if not scrittura_abilitata():
            raise ValueError(
                "Collega il foglio Google per registrare l'attività all'avvio (vedi riquadro in alto)."
            )
        nuova = avvia_attivita(
            operatore,
            campi_selezionati,
            attivita,
            note,
            cultura_val,
            prodotto_val,
            mezzo_val,
        )
        try:
            registra_inizio_attivita(conn, nuova)
        except Exception:
            termina_attivita(nuova["id"])
            raise
        campi_testo = formatta_campi(campi_selezionati)
        st.session_state["flash_home"] = (
            f"Lavorazione avviata alle **{nuova['iniziata_il']}** · {attivita} su {campi_testo}. "
            "Registrata sul foglio con stato *In corso*."
        )
        for sezione in (("operatore",) if titolare else ()) + (
            "campo",
            "cultura",
            "prodotto",
            "mezzo",
        ):
            st.session_state[f"close_exp_{sezione}"] = True
        st.session_state["vai_home"] = True
        st.rerun()
    except ValueError as exc:
        st.error(str(exc))
    except Exception as exc:
        st.error(f"Errore: {exc}")

if titolare and bottone_operazione("✅ Salva e termina subito"):
    if operatore == "Seleziona un nome" or not campi_selezionati:
        st.error("⚠️ Seleziona operatore e almeno un campo prima di salvare.")
    elif not scrittura_abilitata():
        st.error("Collega prima la scrittura al foglio (riquadro in alto).")
    else:
        try:
            salva_attivita_diario(
                conn,
                operatore,
                formatta_campi(campi_selezionati),
                attivita,
                note,
                cultura_val,
                prodotto_val,
                mezzo_val,
            )
            st.success("Attività salvata sul foglio Google!")
            st.balloons()
            st.rerun()
        except Exception as exc:
            st.error(f"Errore durante il salvataggio: {exc}")

st.divider()
st.subheader("Registro attività")
registro = carica_gsheet(conn)
if not registro.empty:
    st.caption(f"{len(registro)} attività · Google Sheets")
    tabella_mobile(registro.iloc[::-1], altezza=320)
else:
    st.info("Nessuna attività nel foglio.")

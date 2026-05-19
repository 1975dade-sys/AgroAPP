"""Componenti UI riutilizzabili per anagrafiche nel diario."""
from collections.abc import Callable

import streamlit as st

from lib.mobile import bottone_operazione


def _applica_prefill_select(key: str, opzioni: list[str]) -> None:
    """Imposta il valore preselezionato tramite session_state (compatibile con key=)."""
    prefill = st.session_state.pop(f"prefill_{key}", None)
    if prefill and prefill in opzioni:
        st.session_state[f"sel_{key}"] = prefill


def _segna_chiusura_expander(key: str) -> None:
    """Programma la chiusura dell'expander al rerun successivo (prima dei widget)."""
    st.session_state[f"close_exp_{key}"] = True


def _chiudi_expander_se_scelto(key: str) -> None:
    val = st.session_state.get(f"sel_{key}", "")
    if val and not str(val).startswith("Seleziona"):
        _segna_chiusura_expander(key)


def selectbox_anagrafica(
    label: str,
    key: str,
    opzioni: list[str],
) -> str:
    if f"exp_{key}" not in st.session_state:
        st.session_state[f"exp_{key}"] = False

    _applica_prefill_select(key, opzioni)

    return st.selectbox(
        label,
        opzioni,
        key=f"sel_{key}",
        on_change=_chiudi_expander_se_scelto,
        args=(key,),
    )


def prepara_pannello_inserimento(
    key: str,
    field_keys: list[str] | None = None,
    field_defaults: dict[str, object] | None = None,
) -> None:
    """Va chiamato subito prima dell'expander."""
    if st.session_state.pop(f"close_exp_{key}", False):
        st.session_state[f"exp_{key}"] = False

    if field_keys and st.session_state.pop(f"clear_fields_{key}", False):
        defaults = field_defaults or {}
        for fk in field_keys:
            st.session_state[fk] = defaults.get(fk, "")


def _programma_chiusura_pannello(
    key: str,
    field_keys: list[str] | None,
) -> None:
    _segna_chiusura_expander(key)
    if field_keys:
        st.session_state[f"clear_fields_{key}"] = True


def multiselect_campi(
    label: str,
    key: str,
    opzioni: list[str],
) -> list[str]:
    if f"exp_{key}" not in st.session_state:
        st.session_state[f"exp_{key}"] = False

    prefill = st.session_state.pop(f"prefill_{key}_mul", None)
    if prefill and prefill in opzioni:
        correnti = list(st.session_state.get(f"mul_{key}", []))
        if prefill not in correnti:
            st.session_state[f"mul_{key}"] = correnti + [prefill]

    def _on_change() -> None:
        if st.session_state.get(f"mul_{key}"):
            _segna_chiusura_expander(key)

    return st.multiselect(
        label,
        opzioni,
        key=f"mul_{key}",
        placeholder="Seleziona uno o più campi…",
        on_change=_on_change,
    )


def bottone_salva_anagrafica(
    key: str,
    on_submit: Callable[[], str],
    field_keys: list[str] | None = None,
    field_defaults: dict[str, object] | None = None,
    prefill_select: bool = True,
) -> None:
    if bottone_operazione("Salva in anagrafica", key=f"btn_add_{key}", use_container_width=True):
        try:
            etichetta = on_submit()
            if etichetta:
                if prefill_select:
                    st.session_state[f"prefill_{key}"] = etichetta
                _programma_chiusura_pannello(key, field_keys)
                st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"Errore: {exc}")

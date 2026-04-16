from __future__ import annotations

import streamlit as st

from app.game_logic import pick_next_question
from app.state import get_current_question, reset_game_state
from app.ui import (
    render_game_summary,
    render_header,
    render_next_button,
    render_question,
    render_sidebar,
)
from core.config import PACKS_DIR
from core.io import load_approved_metadata_rows, load_pack_config


def discover_packs() -> list[str]:
    if not PACKS_DIR.exists():
        return []
    return sorted(
        p.name for p in PACKS_DIR.iterdir()
        if p.is_dir() and (p / "labels.yaml").exists()
    )


def load_pack_questions(pack_name: str):
    pack_dir = PACKS_DIR / pack_name
    metadata_path = pack_dir / "metadata.csv"
    labels_path = pack_dir / "labels.yaml"
    questions = load_approved_metadata_rows(metadata_path)
    pack_config = load_pack_config(labels_path)
    return pack_config, questions


def run() -> None:
    render_header()
    render_sidebar()

    # st.info("Try to predict what the AI will say. Not what is correct.")

    packs = discover_packs()
    if not packs:
        st.warning("No packs are available yet.")
        return

    default_index = 0
    if st.session_state.selected_pack in packs:
        default_index = packs.index(st.session_state.selected_pack)

    selected_pack = st.selectbox("Choose a pack", options=packs, index=default_index)
    pack_config, questions = load_pack_questions(selected_pack)

    st.write(f"**Pack:** {pack_config.display_name}")
    st.caption(pack_config.description)

    if not questions:
        st.warning("This pack has no approved questions yet.")
        return

    start_new_game = False
    if st.session_state.selected_pack != selected_pack:
        start_new_game = True

    if st.button("Start new game", width="stretch"):
        start_new_game = True

    if start_new_game:
        reset_game_state(selected_pack, questions)
        pick_next_question()
        st.rerun()

    if st.session_state.selected_pack is None:
        st.info("Choose a pack and start a game.")
        return

    question = get_current_question()
    if question is None:
        if render_game_summary():
            reset_game_state(selected_pack, questions)
            pick_next_question()
            st.rerun()
        return

    render_question(question)

    if st.session_state.revealed and render_next_button():
        next_question = pick_next_question()
        if next_question is None:
            st.session_state.current_question = None
        st.rerun()
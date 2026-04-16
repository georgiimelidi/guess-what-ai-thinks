from __future__ import annotations

import random
from typing import List, Optional

import streamlit as st

from core.config import RANDOM_SEED
from core.schema import MetadataRow


def init_state() -> None:
    defaults = {
        "selected_pack": None,
        "questions": [],
        "remaining_questions": [],
        "current_question": None,
        "revealed": False,
        "user_choice": None,
        "score": 0,
        "round_index": 0,
        "streak": 0,
        "best_streak": 0,
        "history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_game_state(pack_name: str, questions: List[MetadataRow]) -> None:
    from core.config import QUESTIONS_PER_GAME

    shuffled = questions[:]
    random.shuffle(shuffled)

    selected_questions = shuffled[: min(QUESTIONS_PER_GAME, len(shuffled))]

    st.session_state.selected_pack = pack_name
    st.session_state.questions = selected_questions
    st.session_state.remaining_questions = selected_questions[:]
    st.session_state.current_question = None
    st.session_state.revealed = False
    st.session_state.user_choice = None
    st.session_state.score = 0
    st.session_state.round_index = 0
    st.session_state.streak = 0
    st.session_state.best_streak = 0
    st.session_state.history = []


def get_current_question() -> Optional[MetadataRow]:
    return st.session_state.current_question
from __future__ import annotations

import json

import streamlit as st

from core.schema import MetadataRow


def pick_next_question() -> MetadataRow | None:
    if not st.session_state.remaining_questions:
        st.session_state.current_question = None
        return None

    question = st.session_state.remaining_questions.pop()
    st.session_state.current_question = question
    st.session_state.revealed = False
    st.session_state.user_choice = None
    st.session_state.round_index += 1
    return question


def get_options(question: MetadataRow) -> list[str]:
    return json.loads(question.options_json)


def submit_answer(choice: str) -> None:
    question = st.session_state.current_question
    if question is None or st.session_state.revealed:
        return

    correct = choice == question.ai_top1

    st.session_state.user_choice = choice
    st.session_state.revealed = True

    if correct:
        st.session_state.score += 1
        st.session_state.streak += 1
        st.session_state.best_streak = max(
            st.session_state.best_streak,
            st.session_state.streak,
        )
    else:
        st.session_state.streak = 0

    ai_wrong = bool(question.true_label) and question.ai_top1 != question.true_label

    st.session_state.history.append(
        {
            "image_id": question.image_id,
            "user_choice": choice,
            "ai_choice": question.ai_top1,
            "true_label": question.true_label,
            "correct": correct,
            "difficulty": question.difficulty,
            "ai_wrong": ai_wrong,
        }
    )
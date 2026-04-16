from __future__ import annotations

import json

import streamlit as st

from app.game_logic import get_options, submit_answer
from core.config import PROJECT_ROOT
from core.schema import MetadataRow


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 4.5rem;
            max-width: 760px;
        }

        h1, h2, h3 {
            letter-spacing: -0.02em;
        }

        .gwat-card {
            background: linear-gradient(180deg, #fffaf5 0%, #fff 100%);
            border: 1px solid rgba(196, 87, 110, 0.18);
            border-radius: 22px;
            padding: 1rem 1rem 0.8rem 1rem;
            box-shadow: 0 8px 28px rgba(31, 36, 48, 0.06);
            margin-top: 0.75rem;
            margin-bottom: 0.75rem;
        }

        .gwat-reveal {
            background: linear-gradient(180deg, #fff7f3 0%, #fff 100%);
            border: 1px solid rgba(232, 93, 117, 0.20);
            border-radius: 22px;
            padding: 1rem;
            box-shadow: 0 10px 30px rgba(31, 36, 48, 0.06);
            margin-top: 1rem;
        }

        .gwat-pill {
            display: inline-block;
            padding: 0.28rem 0.6rem;
            border-radius: 999px;
            background: #f3e9df;
            color: #6b4e58;
            font-size: 0.84rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }

        .gwat-hero {
            padding: 0.2rem 0 0.4rem 0;
        }

        .gwat-subtle {
            color: #6a6f7a;
            font-size: 0.96rem;
        }

        .gwat-footer {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(247, 244, 239, 0.96);
            border-top: 1px solid rgba(31, 36, 48, 0.08);
            backdrop-filter: blur(8px);
            padding: 0.55rem 1rem;
            text-align: center;
            color: #6a6f7a;
            font-size: 0.88rem;
            z-index: 999990;
        }

        div[data-testid="stMetric"] {
            background: #fff;
            border: 1px solid rgba(31, 36, 48, 0.08);
            border-radius: 18px;
            padding: 0.35rem 0.6rem;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 0.8rem;
                padding-right: 0.8rem;
                max-width: 100%;
            }
            .gwat-card, .gwat-reveal {
                border-radius: 18px;
                padding: 0.85rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


from core.config import FOOTER_TEXT

def render_footer() -> None:
    st.markdown(
        f"""
        <div class="gwat-footer">
            {FOOTER_TEXT}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="gwat-hero">
            <h1>Guess What the AI Thinks</h1>
            <div class="gwat-subtle">
                Predict which label the AI will choose, not what the image really is.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.subheader("Game")
        st.metric("Score", st.session_state.score)
        st.metric("Round", st.session_state.round_index)
        st.metric("Streak", st.session_state.streak)
        remaining = len(st.session_state.remaining_questions)
        total = len(st.session_state.questions)
        st.caption(f"Remaining questions: {remaining} / {total}")


def render_question(question: MetadataRow) -> None:
    image_path = PROJECT_ROOT / question.image_path

    col_img, col_ui = st.columns([1.2, 1], gap="medium")

    with col_img:
        st.image(str(image_path), width="stretch")

    with col_ui:
        st.markdown(
            f"""
            <div style="margin-bottom:0.5rem;">
                <span class="gwat-pill">Pack: {question.pack_name}</span>
                <span class="gwat-pill">Difficulty: {question.difficulty}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 🔁 BEFORE CLICK → show options
        if not st.session_state.revealed:
            st.markdown("**What will the AI choose?**")
            options = get_options(question)

            for idx, option in enumerate(options):
                key = f"option_{st.session_state.round_index}_{question.image_id}_{idx}"
                if st.button(
                    option.replace("_", " ").title(),
                    width="stretch",
                    key=key,
                ):
                    submit_answer(option)
                    st.rerun()

        # AFTER CLICK → show results IN SAME PLACE
        else:
            render_reveal_inline(question)


def render_reveal(question: MetadataRow) -> None:
    if not st.session_state.revealed:
        return

    all_scores = json.loads(question.all_scores_json)
    ranked = sorted(
        [(k, v["probability"]) for k, v in all_scores.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    user_choice = st.session_state.user_choice
    ai_choice = question.ai_top1
    ai_conf = 100.0 * question.ai_score_top1
    correct = user_choice == ai_choice

    st.markdown("---")

    if correct:
        st.success("Correct. You predicted the AI.")
    else:
        st.error("Not this time.")

    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.write(f"**Your choice:** {user_choice.replace('_', ' ').title()}")
        st.write(f"**AI choice:** {ai_choice.replace('_', ' ').title()}")
        st.write(f"**Top confidence:** {ai_conf:.1f}%")
    with c2:
        st.write(f"**Difficulty:** {question.difficulty.title()}")
        if question.true_label:
            st.write(f"**True label:** {question.true_label}")

    st.markdown("**Top 3 AI guesses**")
    for rank, (label, prob) in enumerate(ranked, start=1):
        st.progress(float(prob), text=f"{rank}. {label.replace('_', ' ').title()} · {100*prob:.1f}%")


def render_game_summary() -> bool:
    score = st.session_state.get("score", 0)
    rounds_played = len(st.session_state.get("history", []))
    best_streak = st.session_state.get("best_streak", 0)

    accuracy = (score / rounds_played) if rounds_played > 0 else 0.0

    st.subheader("Game over")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Score", f"{score} / {rounds_played}")
    with c2:
        st.metric("Accuracy", f"{100 * accuracy:.1f}%")
    with c3:
        st.metric("Best streak", best_streak)

    if accuracy >= 0.75:
        st.success("You beat the AI intuition.")
    elif accuracy >= 0.45:
        st.info("Nice run. The model is tricky.")
    else:
        st.warning("The AI fooled you this time.")

    return st.button("Play again", width="stretch")


def render_next_button() -> bool:
    return st.button("Next round", width="stretch")

def render_reveal_inline(question: MetadataRow) -> None:
    import json

    all_scores = json.loads(question.all_scores_json)
    ranked = sorted(
        [(k, v["probability"]) for k, v in all_scores.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    user_choice = st.session_state.user_choice
    ai_choice = question.ai_top1
    ai_conf = 100.0 * question.ai_score_top1
    correct = user_choice == ai_choice
    ai_wrong = bool(question.true_label) and ai_choice != question.true_label

    if correct:
        st.success("Correct. You predicted the AI.")
    else:
        st.error("Not this time.")

    if ai_wrong:
        st.warning("AI mistake")

    st.markdown("### Result")
    st.write(f"**Your choice:** {user_choice.replace('_', ' ').title()}")
    st.write(f"**AI choice:** {ai_choice.replace('_', ' ').title()}")
    st.write(f"**Top confidence:** {ai_conf:.1f}%")
    st.write(f"**Difficulty:** {question.difficulty.title()}")

    if question.true_label:
        st.write(f"**True label:** {question.true_label.replace('_', ' ').title()}")

    st.markdown("### Top 3 AI guesses")
    for rank, (label, prob) in enumerate(ranked, start=1):
        st.progress(
            float(prob),
            text=f"{rank}. {label.replace('_', ' ').title()} · {100*prob:.1f}%",
        )

def is_ai_wrong(question: MetadataRow) -> bool:
    return bool(question.true_label) and question.ai_top1 != question.true_label
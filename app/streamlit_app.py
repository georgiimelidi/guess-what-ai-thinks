from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.pages import play_page, stats_page, validator_page
from app.state import init_state
from app.ui import inject_css, render_footer


def main() -> None:
    st.set_page_config(
        page_title="Guess What the AI Thinks",
        page_icon="🧠",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    init_state()
    inject_css()

    show_validator = st.query_params.get("admin") == "1"

    pages = [
        st.Page(play_page.run, title="Play", icon="🎮", url_path="play", default=True),
        st.Page(stats_page.run, title="Stats", icon="📊", url_path="stats"),
    ]

    if show_validator:
        pages.append(
            st.Page(
                validator_page.run,
                title="Validator",
                icon="✅",
                url_path="validator",
            )
        )

    pg = st.navigation(pages)
    pg.run()

    render_footer()


if __name__ == "__main__":
    main()
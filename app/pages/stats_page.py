from __future__ import annotations

import pandas as pd
import streamlit as st


def run() -> None:
    st.title("Stats")

    history = st.session_state.get("history", [])
    if not history:
        st.info("Play a few rounds first.")
        return

    df = pd.DataFrame(history)
    accuracy = 100.0 * df["correct"].mean()
    total = len(df)

    ai_wrong_rate = 0.0
    if "ai_wrong" in df.columns:
        ai_wrong_rate = 100.0 * df["ai_wrong"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rounds played", total)
    c2.metric("Accuracy", f"{accuracy:.1f}%")
    c3.metric("Current streak", st.session_state.get("streak", 0))
    c4.metric("AI wrong", f"{ai_wrong_rate:.1f}%")

    st.subheader("Recent rounds")
    df_view = df.copy()
    for col in ["user_choice", "ai_choice", "true_label"]:
        if col in df_view.columns:
            df_view[col] = df_view[col].fillna("").str.replace("_", " ").str.title()
    df_view["difficulty"] = df_view["difficulty"].str.title()

    show_cols = ["image_id", "user_choice", "ai_choice", "correct", "difficulty"]
    if "true_label" in df_view.columns:
        show_cols.append("true_label")
    if "ai_wrong" in df_view.columns:
        show_cols.append("ai_wrong")

    st.dataframe(df_view[show_cols], width="stretch", hide_index=True)

    st.subheader("By difficulty")
    by_diff = (
        df.groupby("difficulty")["correct"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "rounds", "mean": "accuracy"})
    )
    by_diff["accuracy"] = (100.0 * by_diff["accuracy"]).round(1).astype(str) + "%"
    by_diff["difficulty"] = by_diff["difficulty"].str.title()
    st.dataframe(by_diff, width="stretch", hide_index=True)

    if "ai_wrong" in df.columns:
        st.subheader("Rounds where AI was wrong")
        wrong_df = df[df["ai_wrong"] == True].copy()
        if wrong_df.empty:
            st.caption("No AI mistakes seen in this session.")
        else:
            for col in ["user_choice", "ai_choice", "true_label"]:
                if col in wrong_df.columns:
                    wrong_df[col] = wrong_df[col].fillna("").str.replace("_", " ").str.title()
            st.dataframe(
                wrong_df[["image_id", "user_choice", "ai_choice", "true_label", "correct"]],
                width="stretch",
                hide_index=True,
            )
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from core.config import PACKS_DIR, PROJECT_ROOT
from core.io import (
    get_metadata_csv_path,
    load_metadata_rows,
    load_pack_config,
    update_metadata_row,
)


def discover_packs() -> list[str]:
    if not PACKS_DIR.exists():
        return []
    return sorted(
        p.name for p in PACKS_DIR.iterdir()
        if p.is_dir() and (p / "labels.yaml").exists()
    )


def init_validator_state(pack_name: str, num_rows: int) -> None:
    if st.session_state.get("validator_pack") != pack_name:
        st.session_state.validator_pack = pack_name
        st.session_state.validator_index = 0

    if "validator_index" not in st.session_state:
        st.session_state.validator_index = 0

    if num_rows == 0:
        st.session_state.validator_index = 0
    else:
        st.session_state.validator_index = max(
            0,
            min(st.session_state.validator_index, num_rows - 1),
        )


def go_prev(num_rows: int) -> None:
    if num_rows > 0:
        st.session_state.validator_index = max(0, st.session_state.validator_index - 1)


def go_next(num_rows: int) -> None:
    if num_rows > 0:
        st.session_state.validator_index = min(num_rows - 1, st.session_state.validator_index + 1)


def save_current_row(pack_name: str, row, approved_value: str, true_label_value: str, notes_value: str) -> None:
    metadata_path = get_metadata_csv_path(pack_name)

    row.approved = approved_value
    row.true_label = true_label_value.strip() or None
    row.notes = notes_value.strip()

    update_metadata_row(metadata_path, row)


def render_predictions(row) -> None:
    all_scores = json.loads(row.all_scores_json)
    ranked = sorted(
        [(label, values["probability"]) for label, values in all_scores.items()],
        key=lambda x: x[1],
        reverse=True,
    )[:3]

    st.markdown("### Top 3 AI guesses")
    for rank, (label, prob) in enumerate(ranked, start=1):
        st.progress(
            float(prob),
            text=f"{rank}. {label.replace('_', ' ').title()} · {100 * prob:.1f}%",
        )


def is_ai_wrong(row) -> bool:
    return bool(row.true_label) and row.ai_top1 != row.true_label


def apply_filters(rows, approved_filter: str, needs_true_label: bool, ai_wrong_only: bool, difficulty_filter: str):
    filtered = rows

    if approved_filter == "approved":
        filtered = [r for r in filtered if r.approved == "TRUE"]
    elif approved_filter == "rejected":
        filtered = [r for r in filtered if r.approved == "FALSE"]
    elif approved_filter == "unlabeled":
        filtered = [r for r in filtered if not r.true_label]

    if needs_true_label:
        filtered = [r for r in filtered if not r.true_label]

    if ai_wrong_only:
        filtered = [r for r in filtered if is_ai_wrong(r)]

    if difficulty_filter != "all":
        filtered = [r for r in filtered if r.difficulty == difficulty_filter]

    return filtered


def run() -> None:
    st.title("Validator")

    packs = discover_packs()
    if not packs:
        st.warning("No packs found.")
        return

    pack_name = st.selectbox("Pack", packs)
    pack_dir = PACKS_DIR / pack_name
    metadata_path = pack_dir / "metadata.csv"
    labels_path = pack_dir / "labels.yaml"

    pack_config = load_pack_config(labels_path)
    all_rows = load_metadata_rows(metadata_path)

    st.subheader("Filters")
    f1, f2, f3, f4 = st.columns(4)

    with f1:
        approved_filter = st.selectbox(
            "Approval",
            options=["all", "approved", "rejected", "unlabeled"],
            index=0,
        )

    with f2:
        difficulty_filter = st.selectbox(
            "Difficulty",
            options=["all", "easy", "medium", "hard"],
            index=0,
        )

    with f3:
        needs_true_label = st.checkbox("Missing true label only", value=False)

    with f4:
        ai_wrong_only = st.checkbox("AI wrong only", value=False)

    rows = apply_filters(
        rows=all_rows,
        approved_filter=approved_filter,
        needs_true_label=needs_true_label,
        ai_wrong_only=ai_wrong_only,
        difficulty_filter=difficulty_filter,
    )

    init_validator_state(pack_name, len(rows))

    if not all_rows:
        st.info("This pack has no rows yet.")
        return

    approved_count = sum(1 for r in all_rows if r.approved == "TRUE")
    wrong_count = sum(1 for r in all_rows if is_ai_wrong(r))
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", len(all_rows))
    c2.metric("Approved", approved_count)
    c3.metric("AI wrong", wrong_count)

    st.caption(f"Filtered rows: {len(rows)}")

    if not rows:
        st.warning("No rows match the current filters.")
        return

    nav1, nav2, nav3 = st.columns([1, 2, 1])
    with nav1:
        if st.button("← Previous", width="stretch"):
            go_prev(len(rows))
            st.rerun()
    with nav2:
        current_index = st.session_state.validator_index
        selected_index = st.number_input(
            "Filtered row index",
            min_value=0,
            max_value=len(rows) - 1,
            value=current_index,
            step=1,
        )
        if selected_index != current_index:
            st.session_state.validator_index = selected_index
            st.rerun()
    with nav3:
        if st.button("Next →", width="stretch"):
            go_next(len(rows))
            st.rerun()

    row = rows[st.session_state.validator_index]
    image_path = PROJECT_ROOT / row.image_path

    left, right = st.columns([1.3, 1], gap="medium")

    with left:
        st.image(str(image_path), width="stretch")
        st.caption(row.image_id)

    with right:
        st.markdown("### Current metadata")
        st.write(f"**AI top 1:** {row.ai_top1.replace('_', ' ').title()} ({100 * row.ai_score_top1:.1f}%)")
        st.write(f"**AI top 2:** {row.ai_top2.replace('_', ' ').title()} ({100 * row.ai_score_top2:.1f}%)")
        st.write(f"**AI top 3:** {row.ai_top3.replace('_', ' ').title()} ({100 * row.ai_score_top3:.1f}%)")
        st.write(f"**Difficulty:** {row.difficulty.title()}")
        st.write(f"**Approved:** {row.approved}")
        st.write(f"**True label:** {(row.true_label or '').replace('_', ' ').title()}")
        if is_ai_wrong(row):
            st.warning("AI mistake")
        render_predictions(row)

    st.markdown("---")
    st.subheader("Edit row")

    valid_label_ids = [label.id for label in pack_config.labels]
    true_label_options = [""] + valid_label_ids

    current_true_label = row.true_label or ""
    if current_true_label not in true_label_options:
        true_label_options.append(current_true_label)

    approved_value = st.radio(
        "Approved",
        options=["TRUE", "FALSE"],
        index=0 if row.approved == "TRUE" else 1,
        horizontal=True,
        key=f"approved_{row.image_id}",
    )

    true_label_value = st.selectbox(
        "True label",
        options=true_label_options,
        index=true_label_options.index(current_true_label),
        format_func=lambda x: "—" if x == "" else x.replace("_", " ").title(),
        key=f"true_label_{row.image_id}",
    )

    notes_value = st.text_area(
        "Notes",
        value=row.notes or "",
        key=f"notes_{row.image_id}",
        height=100,
    )

    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("Save changes", width="stretch"):
            save_current_row(
                pack_name=pack_name,
                row=row,
                approved_value=approved_value,
                true_label_value=true_label_value,
                notes_value=notes_value,
            )
            st.success("Saved.")
            st.rerun()

    with b2:
        if st.button("Approve", width="stretch"):
            save_current_row(
                pack_name=pack_name,
                row=row,
                approved_value="TRUE",
                true_label_value=true_label_value,
                notes_value=notes_value,
            )
            st.success("Approved.")
            st.rerun()

    with b3:
        if st.button("Reject", width="stretch"):
            save_current_row(
                pack_name=pack_name,
                row=row,
                approved_value="FALSE",
                true_label_value=true_label_value,
                notes_value=notes_value,
            )
            st.success("Rejected.")
            st.rerun()

    st.markdown("---")
    st.subheader("Pack overview")

    overview = pd.DataFrame(
        [
            {
                "image_id": r.image_id,
                "ai_top1": r.ai_top1,
                "difficulty": r.difficulty,
                "approved": r.approved,
                "true_label": r.true_label or "",
                "ai_wrong": is_ai_wrong(r),
            }
            for r in all_rows
        ]
    )

    if not overview.empty:
        overview["ai_top1"] = overview["ai_top1"].str.replace("_", " ").str.title()
        overview["difficulty"] = overview["difficulty"].str.title()
        overview["true_label"] = overview["true_label"].str.replace("_", " ").str.title()

    st.dataframe(overview, width="stretch", hide_index=True)
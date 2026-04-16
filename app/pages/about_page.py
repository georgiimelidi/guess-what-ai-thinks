from __future__ import annotations

import streamlit as st


def run() -> None:
    st.title("About")

    st.markdown(
        """
        **Guess What the AI Thinks** is an interactive game about model behavior.

        You are not trying to guess the correct answer.  
        You are trying to guess what the model will predict.
        """
    )

    st.markdown("### How it works")
    st.markdown(
        """
        - Each image is evaluated by a vision-language model  
        - The model scores a small set of possible labels  
        - You try to predict which label gets the highest score  
        - After each round, the app reveals the model’s top guesses and confidence  
        """
    )

    st.markdown("### Model")
    st.markdown(
        """
        This project uses **SigLIP** (`google/siglip2-base-patch16-224`) via Hugging Face Transformers.

        The model performs zero-shot image–text matching over a custom label set for each pack.
        """
    )

    st.markdown("### Packs")
    st.markdown(
        """
        - **Animals**: similar species and subtle differences  
        - **Food**: visually confusing dishes and textures  
        - **Tech Objects**: everyday tech devices from different angles  
        - **Illusions**: deceptive images and perception traps  
        """
    )

    st.markdown("### Why this project")
    st.markdown(
        """
        Most demos focus on whether AI is correct.

        This one focuses on **how AI sees** and how people can learn to anticipate its behavior.
        """
    )

    st.markdown("### Author")
    st.markdown(
        """
        **Georgii Melidi**  
        2026  

        🌐 [gmelidi.com](https://gmelidi.com/)
        """
    )
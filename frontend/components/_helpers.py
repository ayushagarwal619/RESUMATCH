from typing import Tuple


def get_score_color(score: float) -> Tuple[str, str]:
    """Return (text_color, background_color) for a 0–100 score using CSS variables."""
    if score >= 80:
        return "var(--color-success)", "var(--low-impact-bg)"
    if score >= 60:
        return "var(--color-warning)", "var(--medium-impact-bg)"
    return "var(--color-danger)", "var(--high-impact-bg)"


def get_score_emoji(score: float) -> str:
    """Emoji that matches the score band — used in headlines."""
    if score >= 90:
        return "🌟"
    if score >= 80:
        return "✅"
    if score >= 70:
        return "👍"
    if score >= 60:
        return "⚠️"
    return "🔴"


def get_severity_style(severity: str) -> Tuple[str, str, str]:
    """
    Return (icon, text_color, background_color) for an IssueDetail severity using CSS variables.
    """
    level = (severity or "").lower()
    if level in ("critical", "high"):
        return "🔴", "var(--color-danger)", "var(--high-impact-bg)"
    if level == "medium":
        return "🟡", "var(--color-warning)", "var(--medium-impact-bg)"
    return "🟢", "var(--color-success)", "var(--low-impact-bg)"


def html_inject(html_str: str) -> None:
    import re
    import streamlit as st
    clean = re.sub(r'\s+', ' ', html_str).strip()
    st.markdown(clean, unsafe_allow_html=True)

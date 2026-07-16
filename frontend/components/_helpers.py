from typing import Tuple


def get_score_color(score: float) -> Tuple[str, str]:
    """Return (text_color, background_color) for a 0–100 score."""
    if score >= 80:
        return "#10B981", "rgba(16, 185, 129, 0.15)"  # green
    if score >= 60:
        return "#F59E0B", "rgba(245, 158, 11, 0.15)"  # orange
    return "#EF4444", "rgba(239, 68, 68, 0.15)"      # red


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
    Return (icon, text_color, background_color) for an IssueDetail severity.
    """
    level = (severity or "").lower()
    if level in ("critical", "high"):
        return "🔴", "#EF4444", "rgba(239, 68, 68, 0.15)"
    if level == "medium":
        return "🟡", "#F59E0B", "rgba(245, 158, 11, 0.15)"
    return "🟢", "#10B981", "rgba(16, 185, 129, 0.15)"


def html_inject(html_str: str) -> None:
    import re
    import streamlit as st
    clean = re.sub(r'\s+', ' ', html_str).strip()
    st.markdown(clean, unsafe_allow_html=True)

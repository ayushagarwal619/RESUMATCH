from typing import Any, Dict
import streamlit as st
import textwrap


def display_recommendations(analysis: Dict[str, Any]) -> None:
    suggestions = analysis.get("suggestions") or []
    if not suggestions:
        return

    st.markdown("### 💡 Recommended Improvements")
    for suggestion in suggestions:
        st.markdown(
            textwrap.dedent(f"""
            <div class="glass-card" style="padding: 1rem; border-left: 4px solid var(--accent-secondary); border-color: var(--accent-secondary); margin-bottom: 0.8rem;">
                <p style="color: var(--text-primary); font-size: 0.9rem; line-height: 1.5; margin: 0;">{suggestion}</p>
            </div>
            """),
            unsafe_allow_html=True,
        )

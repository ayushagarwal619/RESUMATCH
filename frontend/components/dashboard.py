from typing import Any, Dict
import streamlit as st

from frontend.components.score_display import display_overall_score, display_score_breakdown
from frontend.components.strengths_issues import display_strengths, display_critical_issues
from frontend.components.skill_validation import display_skill_validation
from frontend.components.jd_comparison import display_jd_comparison
from frontend.components.detailed_feedback import display_detailed_feedback
from frontend.components.action_items import display_action_items
from frontend.components.recommendations import display_recommendations


def display_results_dashboard(analysis: Dict[str, Any]) -> None:
    """
    Render the full results page from one backend response dict.
    """
    display_overall_score(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_score_breakdown(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_strengths(analysis.get("strengths") or [])
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_critical_issues(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_skill_validation(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    # JD comparison only shows up if the user actually submitted a JD.
    jd_comparison = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")
    if jd_comparison:
        display_jd_comparison(jd_comparison)
        st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_detailed_feedback(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_action_items(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    display_recommendations(analysis)

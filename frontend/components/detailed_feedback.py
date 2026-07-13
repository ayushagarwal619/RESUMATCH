from typing import Any, Dict, List
import streamlit as st
from frontend.components._helpers import get_severity_style

SEVERITY_ORDER = ["critical", "high", "medium", "low"]


def _group_by_severity(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {level: [] for level in SEVERITY_ORDER}
    for issue in issues:
        level = (issue.get("severity_level") or "low").lower()
        grouped.setdefault(level, []).append(issue)
    return grouped


def _render_issue(issue: Dict[str, Any]) -> None:
    icon, text_color, bg_color = get_severity_style(issue.get("severity_level"))
    title = issue.get("issue_title", "Untitled issue")
    impact = issue.get("ats_impact", "")
    explanation = issue.get("explanation", "")
    where = issue.get("where_it_appears", "")
    how_to_fix = issue.get("how_to_fix", "")
    action_items = issue.get("action_items") or []
    example = issue.get("example_improvement", "")

    st.markdown(
        f"""
        <div class="glass-card" style="padding: 1.5rem; margin-bottom: 1.2rem; border-left: 4px solid {text_color}; border-color: {text_color};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; flex-wrap: wrap; gap: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.4rem;">{icon}</span>
                    <h4 style="margin: 0; color: white; font-size: 1.1rem; font-weight: 700;">{title}</h4>
                </div>
                <span style="font-size: 0.75rem; font-weight: bold; background: {bg_color}; color: {text_color}; padding: 2px 10px; border-radius: var(--radius-full); border: 1px solid rgba(255,255,255,0.05);">{impact}</span>
            </div>
            <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin: 0 0 1rem 0;">{explanation}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("🛠️ Action Plan & Code Example", expanded=False):
        if where:
            st.markdown(f"📍 **Where it appears:** {where}")
        if how_to_fix:
            st.markdown(f"💡 **How to fix:** {how_to_fix}")
        if action_items:
            st.markdown("📋 **Action checklist:**")
            for item in action_items:
                st.markdown(f"- {item}")
        if example:
            st.markdown("📝 **Example improvement:**")
            st.code(example, language="text")


def display_detailed_feedback(analysis: Dict[str, Any]) -> None:
    issues = analysis.get("detailed_feedback") or []
    if not issues:
        return  # backend produced no per-issue feedback this run

    # Filter out score breakdown title if present in issues
    issues = [iss for iss in issues if iss.get("issue_title") != "ATS Score Breakdown & Explanation"]

    st.markdown("### 🔍 Detailed Feedback")
    st.caption(f"{len(issues)} issue(s) flagged — grouped by severity.")

    grouped = _group_by_severity(issues)
    for level in SEVERITY_ORDER:
        items = grouped.get(level, [])
        if not items:
            continue
        st.markdown(f"#### {level.title()} ({len(items)})")
        for issue in items:
            _render_issue(issue)

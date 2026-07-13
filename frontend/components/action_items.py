from typing import Any, Dict, List, Tuple
import streamlit as st

SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _collect_action_items(analysis: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Return list of (severity, source_title, action_text)."""
    items: List[Tuple[str, str, str]] = []

    for issue in analysis.get("detailed_feedback") or []:
        level = (issue.get("severity_level") or "low").lower()
        title = issue.get("issue_title", "")
        for action in issue.get("action_items") or []:
            items.append((level, title, action))

    if not items:
        for suggestion in analysis.get("suggestions") or []:
            items.append(("medium", "General", suggestion))

    items.sort(key=lambda row: SEVERITY_RANK.get(row[0], 99))
    return items


def display_action_items(analysis: Dict[str, Any]) -> None:
    items = _collect_action_items(analysis)
    
    # Filter out score breakdown title if present in source titles
    items = [item for item in items if item[1] != "ATS Score Breakdown & Explanation"]

    if not items:
        return

    st.markdown("### ⚡ Action Items Checklist")
    st.caption("Concrete steps to improve your score, prioritized by estimated impact.")

    st.markdown('<div style="display: flex; flex-direction: column; gap: 10px; margin-top: 1rem;">', unsafe_allow_html=True)
    
    for level, source, action in items:
        # Determine priority style
        if level in ("critical", "high"):
            badge_color = "#EF4444"
            badge_bg = "rgba(239, 68, 68, 0.15)"
            impact_text = "High Impact (+8-12 pts)"
            border_color = "#EF4444"
        elif level == "medium":
            badge_color = "#F59E0B"
            badge_bg = "rgba(245, 158, 11, 0.15)"
            impact_text = "Medium Impact (+4-6 pts)"
            border_color = "#F59E0B"
        else:
            badge_color = "#10B981"
            badge_bg = "rgba(16, 185, 129, 0.15)"
            impact_text = "Low Impact (+1-3 pts)"
            border_color = "#10B981"

        st.markdown(
            f"""
            <div class="glass-card" style="padding: 1.2rem; border-left: 4px solid {border_color}; border-color: {border_color}; display: flex; align-items: flex-start; gap: 12px; margin-bottom: 0.5rem;">
                <div style="font-size: 1.3rem; margin-top: 2px;">☑️</div>
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                        <span style="font-weight: 700; color: white; font-size: 0.9rem;">{source}</span>
                        <span style="font-size: 0.75rem; font-weight: bold; background: {badge_bg}; color: {badge_color}; padding: 2px 8px; border-radius: var(--radius-full); border: 1px solid rgba(255,255,255,0.03);">{impact_text}</span>
                    </div>
                    <p style="color: var(--text-primary); font-size: 0.9rem; line-height: 1.5; margin: 0;">{action}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)

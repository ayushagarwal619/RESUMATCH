from typing import Any, Dict, List
import streamlit as st


def display_strengths(strengths: List[str]) -> None:
    st.markdown("### 💪 Strengths")
    if not strengths:
        st.info("Keep improving your resume to unlock strengths!")
        return

    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.2rem; margin-top: 1rem;">
    """, unsafe_allow_html=True)
    
    for item in strengths:
        item_lower = item.lower()
        if "project" in item_lower:
            icon, title = "📁", "Project Portfolio"
        elif "experience" in item_lower or "work" in item_lower:
            icon, title = "💼", "Professional Experience"
        elif "education" in item_lower or "academic" in item_lower:
            icon, title = "🎓", "Academic Foundation"
        elif "skill" in item_lower:
            icon, title = "🛠️", "Technical Skills"
        elif "verb" in item_lower:
            icon, title = "🚀", "Action-Oriented Language"
        elif "layout" in item_lower or "format" in item_lower:
            icon, title = "✨", "ATS-Friendly Layout"
        elif "metrics" in item_lower or "outcome" in item_lower:
            icon, title = "📈", "Quantified Achievements"
        else:
            icon, title = "🌟", "Resume Strength"

        st.markdown(
            f"""
            <div class="glass-card" style="padding: 1.2rem; border-left: 4px solid var(--accent-green); border-color: var(--accent-green); margin-bottom: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.4rem;">{icon}</span>
                        <h4 style="margin: 0; color: white; font-size: 1rem; font-weight: 700;">{title}</h4>
                    </div>
                    <span style="font-size: 0.75rem; font-weight: bold; background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 2px 8px; border-radius: var(--radius-full);">High Confidence</span>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5; margin: 0;">{item}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    st.markdown("</div>", unsafe_allow_html=True)


def display_critical_issues(analysis: Dict[str, Any]) -> None:
    critical = analysis.get("critical_issues") or []
    summary = analysis.get("issues_summary") or []

    # Filter out score breakdown title if present
    summary = [s for s in summary if s != "ATS Score Breakdown & Explanation"]

    if not critical and not summary:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid var(--accent-green); border-color: var(--accent-green); padding: 1.5rem; text-align: center; margin-top: 1rem;">
            <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">✅</div>
            <h3 style="color: white; margin: 0 0 0.5rem 0; font-weight: 700; font-size: 1.25rem;">No Critical Issues Found!</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; margin: 0;">Your resume doesn't have any urgent structural issues. Excellent formatting.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("### 🚨 Critical Issues")
    
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.2rem; margin-top: 1rem; margin-bottom: 1rem;">
    """, unsafe_allow_html=True)

    for item in critical:
        st.markdown(
            f"""
            <div class="glass-card" style="padding: 1.2rem; border-left: 4px solid var(--accent-red); border-color: var(--accent-red);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.4rem;">🚨</span>
                        <h4 style="margin: 0; color: white; font-size: 1.05rem; font-weight: 700;">{item}</h4>
                    </div>
                    <span style="font-size: 0.75rem; font-weight: bold; background: rgba(239, 68, 68, 0.15); color: #EF4444; padding: 2px 8px; border-radius: var(--radius-full);">High Priority</span>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.85rem; line-height: 1.5; margin: 0;">This issue should be addressed first for better recruiter validation.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    extra = [s for s in summary if s not in critical]
    if extra:
        with st.expander("📋 Additional flagged items", expanded=False):
            for item in extra:
                st.markdown(f"- {item}")

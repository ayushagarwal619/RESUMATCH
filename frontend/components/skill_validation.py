from typing import Any, Dict
import streamlit as st
from frontend.components._helpers import html_inject


def display_skill_validation(analysis: Dict[str, Any]) -> None:
    details = analysis.get("skill_validation_details") or {}
    validated = details.get("validated", [])
    unvalidated = details.get("unvalidated", [])
    total = details.get("total", len(validated) + len(unvalidated))
    pct = details.get("validation_pct", 0.0)

    st.markdown("### 🛠️ Skill Validation Analysis")

    if total == 0:
        st.info("No skills detected on the resume.")
        return

    html_inject(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin-top: 1rem; margin-bottom: 2rem;">
        <div class="glass-card" style="text-align: center; padding: 1.2rem;">
            <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-primary);">{total}</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Total Skills</div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 1.2rem;">
            <div style="font-size: 2.2rem; font-weight: 800; color: var(--color-success);">{len(validated)}</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Validated Skills</div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 1.2rem;">
            <div style="font-size: 2.2rem; font-weight: 800; color: var(--accent-primary);">{pct:.0f}%</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Validation Rate</div>
        </div>
    </div>
    """)

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h4 style="color: var(--text-primary); font-size: 1.1rem; font-weight: 700; margin-bottom: 10px;">Demonstrated Skills Verification</h4>
    </div>
    """, unsafe_allow_html=True)

    if validated:
        with st.expander(f"✅ Validated Skills ({len(validated)})", expanded=True):
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">', unsafe_allow_html=True)
            for entry in validated:
                skill = entry.get("skill", "?")
                projects = entry.get("projects", []) or []
                similarity = entry.get("similarity")
                
                project_text = ", ".join(projects[:2]) if projects else "Experience section"
                sim_text = f" ({similarity * 100:.0f}% match)" if isinstance(similarity, (int, float)) else ""
                
                html_inject(f"""
                <span class="skill-chip skill-chip-validated" title="Demonstrated in: {project_text}">
                    {skill}{sim_text} <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: normal;">({project_text})</span>
                </span>
                """)
            st.markdown('</div>', unsafe_allow_html=True)

    if unvalidated:
        with st.expander(f"⚠️ Unvalidated Skills ({len(unvalidated)})", expanded=False):
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">', unsafe_allow_html=True)
            for skill in unvalidated:
                html_inject(f"""
                <span class="skill-chip skill-chip-missing">
                    {skill}
                </span>
                """)
            st.markdown('</div>', unsafe_allow_html=True)

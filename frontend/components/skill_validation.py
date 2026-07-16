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
        <div class="glass-card" style="text-align: center; padding: 1.2rem; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;">
            <div style="font-size: 2.2rem; font-weight: 800; color: var(--text-primary);">{total}</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Total Skills</div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 1.2rem; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;">
            <div style="font-size: 2.2rem; font-weight: 800; color: var(--color-success);">{len(validated)}</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Validated Skills</div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 1.2rem; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;">
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
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">', unsafe_allow_html=True)
            for entry in validated:
                skill = entry.get("skill", "?")
                projects = entry.get("projects", []) or []
                proficiency = entry.get("proficiency", "Beginner")
                
                # Determine colors based on proficiency rating
                if proficiency == "Advanced":
                    p_badge = "<span style='padding: 2px 6px; background: rgba(139, 92, 246, 0.12); border: 1px solid #8B5CF6; color: #a78bfa; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 8px;'>ADVANCED</span>"
                elif proficiency == "Intermediate":
                    p_badge = "<span style='padding: 2px 6px; background: rgba(59, 130, 246, 0.12); border: 1px solid #3B82F6; color: #60a5fa; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 8px;'>INTERMEDIATE</span>"
                else:
                    p_badge = "<span style='padding: 2px 6px; background: rgba(100, 116, 139, 0.12); border: 1px solid #64748B; color: #94a3b8; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 8px;'>BEGINNER</span>"
                
                project_text = "; ".join(projects) if projects else "Experience section"
                
                html_inject(f"""
                <span class="skill-chip skill-chip-validated" style="display: inline-flex; align-items: center; padding: 8px 12px; margin-bottom: 6px;" title="Evidence: {project_text}">
                    <span style="font-weight: 700; color: var(--text-primary);">{skill}</span>
                    {p_badge}
                </span>
                """)
            st.markdown('</div>', unsafe_allow_html=True)

    if unvalidated:
        with st.expander(f"⚠️ Unvalidated Skills ({len(unvalidated)})", expanded=False):
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 10px; padding: 10px 0;">', unsafe_allow_html=True)
            for skill in unvalidated:
                html_inject(f"""
                <span class="skill-chip skill-chip-missing" style="display: inline-flex; align-items: center; padding: 8px 12px; margin-bottom: 6px;">
                    <span style="font-weight: 600;">{skill}</span>
                    <span style="padding: 2px 6px; background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; color: #fca5a5; border-radius: 4px; font-size: 0.7rem; font-weight: 800; margin-left: 8px;">UNVERIFIED</span>
                </span>
                """)
            st.markdown('</div>', unsafe_allow_html=True)

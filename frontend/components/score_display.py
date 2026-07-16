from typing import Any, Dict
import streamlit as st
from frontend.components._helpers import html_inject

COMPONENTS = [
    ("Formatting Quality", "formatting",        20, "📝"),
    ("Keywords & Skills",  "keywords",          25, "🔑"),
    ("Content Quality",    "content",           25, "📄"),
    ("Skill Validation",   "skill_validation",  15, "✅"),
    ("ATS Compatibility",  "ats_compatibility", 15, "🤖"),
]

def display_overall_score(analysis: Dict[str, Any]) -> None:
    """Render the recruiter-grade triple scores side-by-side with animated SVGs."""
    qual_score = float(analysis.get("resume_quality_score", 0) or analysis.get("ATS_score", 0))
    comp_score = float(analysis.get("ats_compatibility_score", 0) or analysis.get("ATS_score", 0))
    match_score = analysis.get("job_match_score")
    if match_score is not None:
        try:
            match_score = float(match_score)
        except (ValueError, TypeError):
            match_score = None
            
    interpretation = analysis.get("interpretation", "")
    
    # SVG circle dash offsets (r=90 => circumference = 2 * pi * 90 = 565.48)
    qual_offset = 565.48 - (565.48 * qual_score / 100.0)
    comp_offset = 565.48 - (565.48 * comp_score / 100.0)
    match_offset = 565.48 - (565.48 * match_score / 100.0) if match_score is not None else 0
    
    def get_color_and_label(val):
        if val >= 80:
            return "#10B981", "Excellent"
        elif val >= 60:
            return "#F59E0B", "Good"
        else:
            return "#EF4444", "Needs Work"

    qual_color, qual_label = get_color_and_label(qual_score)
    comp_color, comp_label = get_color_and_label(comp_score)
    if match_score is not None:
        match_color, match_label = get_color_and_label(match_score)
        
    st.markdown("## 📊 Recruiter-Grade Evaluation")
    
    if match_score is not None:
        c1, c2, c3 = st.columns(3)
        cols = [
            (c1, "Resume Quality", qual_score, qual_offset, qual_color, qual_label, 
             "Evaluates layout structure, section completeness checklist, achievements, and experience metrics."),
            (c2, "ATS Compatibility", comp_score, comp_offset, comp_color, comp_label, 
             "Checks section parsing tags, location privacy details, and absence of text blockers."),
            (c3, "Job Match Score", match_score, match_offset, match_color, match_label, 
             "Measures keyword alignment and role profile gaps against job description requirements.")
        ]
    else:
        c1, c2 = st.columns(2)
        cols = [
            (c1, "Resume Quality", qual_score, qual_offset, qual_color, qual_label, 
             "Evaluates layout structure, section completeness checklist, achievements, and experience metrics."),
            (c2, "ATS Compatibility", comp_score, comp_offset, comp_color, comp_label, 
             "Checks section parsing tags, location privacy details, and absence of text blockers.")
        ]
                
    for col, title, val, offset, color, label, desc in cols:
        with col:
            html_inject(f"""
            <div class="glass-card animate-glow" style="text-align: center; padding: 2rem; margin-top: 1rem; height: 390px; display: flex; flex-direction: column; justify-content: space-between; align-items: center; border: var(--border-soft); border-radius: 16px;">
                <h3 style="color: var(--text-primary); font-size: 1.15rem; font-weight: 700; margin-bottom: 0.5rem; height: 40px; display: flex; align-items: center; justify-content: center;">{title}</h3>
                <div class="score-circle-container" style="--dashoffset: {offset}px; width: 140px; height: 140px; position: relative; display: flex; align-items: center; justify-content: center;">
                    <svg class="score-svg" viewBox="0 0 200 200" style="width: 140px; height: 140px; transform: rotate(-90deg);">
                        <defs>
                            <linearGradient id="grad_{title.replace(' ', '')}" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#8B5CF6" />
                                <stop offset="100%" stop-color="#3B82F6" />
                            </linearGradient>
                        </defs>
                        <circle cx="100" cy="100" r="90" style="fill: none; stroke: var(--circle-stroke-empty); stroke-width: 12px;" />
                        <circle cx="100" cy="100" r="90" style="fill: none; stroke: url(#grad_{title.replace(' ', '')}); stroke-width: 12px; stroke-dasharray: 565.48; stroke-dashoffset: {offset}; stroke-linecap: round; transition: stroke-dashoffset 1s ease-out;" />
                    </svg>
                    <div class="score-value" style="position: absolute; color: var(--text-primary); font-size: 2.2rem; font-weight: 800; text-align: center;">{val:.0f}</div>
                </div>
                <div style="margin-top: 0.5rem;"><span style="color: {color}; font-size: 0.9rem; font-weight: 700; text-transform: uppercase;">{label}</span></div>
                <p style="color: var(--text-secondary); margin-top: 0.75rem; font-size: 0.85rem; line-height: 1.35; min-height: 50px;">{desc}</p>
            </div>
            """)
            
    st.info(f"💡 **Overall Recruiter Summary**: {interpretation}")

def display_score_breakdown(analysis: Dict[str, Any]) -> None:
    """Five progress bars, one per scoring component, wrapped in glass-cards, followed by explainability details."""
    component_scores = analysis.get("component_scores") or {}
    explainable_cards = analysis.get("explainable_cards") or {}
    
    st.markdown("### 📈 Category Breakdown")

    left, right = st.columns(2)
    for i, (label, key, max_score, icon) in enumerate(COMPONENTS):
        value = float(component_scores.get(key, 0))
        percentage = (value / max_score) * 100.0 if max_score else 0.0
        
        # Color coding
        if percentage >= 80:
            bar_color = "var(--color-success)"
        elif percentage >= 60:
            bar_color = "var(--color-warning)"
        else:
            bar_color = "var(--color-danger)"

        with left if i % 2 == 0 else right:
            html_inject(f"""
            <div class="glass-card" style="padding: 1.2rem; margin-bottom: 1rem; border: var(--border-soft);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 600; color: var(--text-primary); font-size: 0.95rem;">{icon} {label}</span>
                    <span style="font-weight: 700; color: var(--text-primary); font-size: 0.95rem;">{value:.1f} / {max_score}</span>
                </div>
                <div class="shimmer-progress" style="height: 10px;">
                    <div class="shimmer-progress-fill" style="width: {percentage}%; background: {bar_color};"></div>
                </div>
            </div>
            """)
            
    # Explainable score cards section
    if explainable_cards:
        st.markdown("<div style='margin: 1.5rem 0 1rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("#### 🔍 Explainable Scoring Breakdown")
        for cat, details in explainable_cards.items():
            with st.expander(f"📊 {cat} — Score: {details.get('score')}/100", expanded=False):
                st.markdown(f"**Evidence from Resume:** {details.get('evidence')}")
                st.markdown(f"**Deductions & Reasoning:** {details.get('reason')}")
                st.markdown(f"**Actionable Recommendation:** {details.get('improvement')}")

from typing import Any, Dict

import streamlit as st

COMPONENTS = [
    ("Formatting",        "formatting",        20, "📝"),
    ("Keywords & Skills", "keywords",          25, "🔑"),
    ("Content Quality",   "content",           25, "📄"),
    ("Skill Validation",  "skill_validation",  15, "✅"),
    ("ATS Compatibility", "ats_compatibility", 15, "🤖"),
]


def display_overall_score(analysis: Dict[str, Any]) -> None:
    """Big colored score circle with SVG animation and interpretation line."""
    score = float(analysis.get("ATS_score", analysis.get("ats_score", 0)))
    interpretation = analysis.get("interpretation", "")
    
    # SVG circle calculation
    dashoffset = 565.48 - (565.48 * score / 100.0)
    
    # Check score tiers for colors
    if score >= 80:
        status_color = "#10B981" # Green
        status_label = "Excellent"
    elif score >= 60:
        status_color = "#F59E0B" # Orange
        status_label = "Good"
    else:
        status_color = "#EF4444" # Red
        status_label = "Needs Improvement"

    st.markdown("## 📊 Analysis Results")
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(
            f"""
            <div class="glass-card animate-glow" style="text-align: center; padding: 2.5rem; margin-top: 1rem;">
                <div class="score-circle-container" style="--dashoffset: {dashoffset}px;">
                    <svg class="score-svg" viewBox="0 0 200 200">
                        <defs>
                            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#8B5CF6" />
                                <stop offset="100%" stop-color="#3B82F6" />
                            </linearGradient>
                        </defs>
                        <circle class="score-bg-circle" cx="100" cy="100" r="90" />
                        <circle class="score-fill-circle" cx="100" cy="100" r="90" />
                    </svg>
                    <div class="score-value-text">{score:.0f}</div>
                    <div class="score-label-text" style="color: {status_color};">{status_label}</div>
                </div>
                <h3 style="color: white; margin-top: 1.5rem; font-size: 1.5rem; font-weight: 700;">Overall ATS Score</h3>
                <p style="color: var(--text-secondary); margin-top: 0.5rem; font-size: 1rem;">{interpretation}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def display_score_breakdown(analysis: Dict[str, Any]) -> None:
    """Five progress bars, one per scoring component, wrapped in glass-cards."""
    component_scores = analysis.get("component_scores") or {}
    st.markdown("### 📈 Category Breakdown")

    left, right = st.columns(2)
    for i, (label, key, max_score, icon) in enumerate(COMPONENTS):
        value = float(component_scores.get(key, 0))
        percentage = (value / max_score) * 100.0 if max_score else 0.0
        
        # Color coding
        if percentage >= 80:
            bar_color = "var(--accent-green)"
        elif percentage >= 60:
            bar_color = "var(--accent-yellow)"
        else:
            bar_color = "var(--accent-red)"

        with left if i % 2 == 0 else right:
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 1.2rem; margin-bottom: 1rem; border-color: rgba(255,255,255,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 600; color: white; font-size: 0.95rem;">{icon} {label}</span>
                        <span style="font-weight: 700; color: white; font-size: 0.95rem;">{value:.1f} / {max_score}</span>
                    </div>
                    <div class="shimmer-progress" style="height: 10px;">
                        <div class="shimmer-progress-fill" style="width: {percentage}%; background: {bar_color};"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

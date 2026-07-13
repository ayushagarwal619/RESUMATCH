from typing import Any, Dict, Optional
import streamlit as st
from frontend.components._helpers import html_inject


def display_jd_comparison(jd_comparison: Optional[Dict[str, Any]]) -> None:
    if not jd_comparison:
        return

    st.markdown("### 🎯 Job Description Match")

    match_pct = float(jd_comparison.get("match_percentage", 0))
    semantic = float(jd_comparison.get("semantic_similarity", 0)) * 100.0
    matched = jd_comparison.get("matched_keywords", []) or []
    missing = jd_comparison.get("missing_keywords", []) or []
    gap = jd_comparison.get("skills_gap", []) or []

    html_inject(f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.2rem; margin-top: 1rem; margin-bottom: 2rem;">
        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; font-weight: 800; color: var(--accent-primary);">{match_pct:.0f}%</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Keyword Match</div>
            <div class="shimmer-progress" style="height: 6px; margin-top: 10px;">
                <div class="shimmer-progress-fill" style="width: {match_pct}%; background: var(--grad-primary);"></div>
            </div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; font-weight: 800; color: var(--accent-secondary);">{semantic:.0f}%</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; text-transform: uppercase; margin-top: 4px;">Semantic Similarity</div>
            <div class="shimmer-progress" style="height: 6px; margin-top: 10px;">
                <div class="shimmer-progress-fill" style="width: {semantic}%; background: var(--accent-secondary);"></div>
            </div>
        </div>
    </div>
    """)

    col1, col2 = st.columns(2)
    with col1:
        with st.expander(f"✅ Matched Keywords ({len(matched)})", expanded=True):
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">', unsafe_allow_html=True)
            if matched:
                for kw in matched:
                    html_inject(f'<span class="skill-chip skill-chip-validated">{kw}</span>')
            else:
                st.markdown('<span style="color: var(--text-muted);">None matched yet</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        with st.expander(f"❌ Missing Keywords ({len(missing)})", expanded=True):
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">', unsafe_allow_html=True)
            if missing:
                for kw in missing:
                    html_inject(f'<span class="skill-chip skill-chip-missing">{kw}</span>')
            else:
                st.markdown('<span style="color: var(--color-success); font-weight: 600;">All key terms are present!</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    if gap:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.expander(f"📊 Identified Skills Gaps ({len(gap)})", expanded=True):
            st.markdown('<div style="display: flex; flex-wrap: wrap; gap: 8px; padding: 10px 0;">', unsafe_allow_html=True)
            for skill in gap:
                html_inject(f'<span class="skill-chip skill-chip-partial">{skill}</span>')
            st.markdown('</div>', unsafe_allow_html=True)

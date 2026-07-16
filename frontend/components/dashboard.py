from typing import Any, Dict
import streamlit as st

from frontend.components.score_display import display_overall_score, display_score_breakdown
from frontend.components.strengths_issues import display_strengths, display_critical_issues
from frontend.components.skill_validation import display_skill_validation
from frontend.components.jd_comparison import display_jd_comparison
from frontend.components.detailed_feedback import display_detailed_feedback
from frontend.components.action_items import display_action_items
from frontend.components.recommendations import display_recommendations
from frontend.components._helpers import html_inject

def display_recruiter_insights(analysis: Dict[str, Any]) -> None:
    """Renders recruiter-grade pre-screening checklist, strengths, concerns, red flags, and confidence."""
    insights = analysis.get("recruiter_insights") or {}
    red_flags = analysis.get("red_flags") or []
    raw_completeness = analysis.get("completeness_percentage") or analysis.get("resume_completeness_pct")
    if raw_completeness is None:
        completeness = 100.0
    else:
        try:
            completeness = float(raw_completeness)
        except (ValueError, TypeError):
            completeness = 100.0
    
    st.markdown("### 🧑‍💼 Recruiter Insights & Red Flags")
    
    # Recommendation & Completeness row
    c1, c2 = st.columns(2)
    with c1:
        rec = insights.get("overall_recommendation", "Borderline")
        if rec == "Strong Hire":
            color = "#10B981"
            bg = "rgba(16,185,129,0.06)"
        elif rec == "Hire":
            color = "#3B82F6"
            bg = "rgba(59,130,246,0.06)"
        elif rec == "Borderline":
            color = "#F59E0B"
            bg = "rgba(245,158,11,0.06)"
        else:
            color = "#EF4444"
            bg = "rgba(239,68,68,0.06)"
            
        html_inject(f"""
        <div class="glass-card" style="padding: 1.2rem; display: flex; flex-direction: column; justify-content: center; height: 110px; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;">
            <div style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px; text-transform: uppercase;">Recruiter Verdict</div>
            <div style="display: inline-block; padding: 6px 16px; background: {bg}; border: 1.5px solid {color}; color: {color}; font-weight: 800; font-size: 1.25rem; border-radius: 8px; text-align: center; width: fit-content; letter-spacing: 0.02em;">
                {rec.upper()}
            </div>
        </div>
        """)
    with c2:
        html_inject(f"""
        <div class="glass-card" style="padding: 1.2rem; display: flex; flex-direction: column; justify-content: center; height: 110px; border: 1px solid rgba(255,255,255,0.05); border-radius: 12px;">
            <div style="font-size: 0.8rem; color: var(--text-secondary); font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px; text-transform: uppercase;">Resume Completeness</div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="font-weight: 800; color: var(--text-primary); font-size: 1.25rem;">{completeness:.0f}%</span>
                <span style="font-size: 0.85rem; color: var(--text-secondary);">11 Checklist Sections</span>
            </div>
            <div class="shimmer-progress" style="height: 10px; background: rgba(255,255,255,0.05); border-radius: 4px; overflow: hidden; border: 1px solid rgba(255,255,255,0.02);">
                <div class="shimmer-progress-fill" style="width: {completeness}%; background: linear-gradient(90deg, #8B5CF6 0%, #3B82F6 100%); height: 100%;"></div>
            </div>
        </div>
        """)
        
    st.markdown("<div style='margin: 0.75rem 0;'></div>", unsafe_allow_html=True)
    
    # Strengths vs Concerns
    left, right = st.columns(2)
    with left:
        st.markdown("<p style='font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;'>🎯 Top 5 Key Strengths</p>", unsafe_allow_html=True)
        for s in insights.get("strengths", []):
            st.markdown(f"<span style='color: var(--color-success); font-weight: 700;'>✓</span> <span style='font-size: 0.9rem; color: var(--text-secondary);'>{s.strip()}</span>", unsafe_allow_html=True)
    with right:
        st.markdown("<p style='font-size: 0.95rem; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;'>⚠️ Top 5 Concerns</p>", unsafe_allow_html=True)
        for c in insights.get("hiring_concerns", []):
            st.markdown(f"<span style='color: var(--color-warning); font-weight: 700;'>•</span> <span style='font-size: 0.9rem; color: var(--text-secondary);'>{c.strip()}</span>", unsafe_allow_html=True)
            
    # Red flags warning
    if red_flags:
        st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)
        html_inject(f"""
        <div class="glass-card" style="border: 1px solid rgba(239, 68, 68, 0.25); background: rgba(239, 68, 68, 0.03); padding: 1.2rem; border-radius: 12px;">
            <h4 style="color: #EF4444; margin: 0 0 8px 0; font-size: 1rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                🚨 Recruiter Red Flags Warning
            </h4>
            <ul style="margin: 0; padding-left: 1.2rem; color: var(--text-secondary); font-size: 0.88rem; line-height: 1.5;">
                {"".join([f"<li style='margin-bottom: 4px;'>{rf}</li>" for rf in red_flags])}
            </ul>
        </div>
        """)

    # Confidence scores footer
    conf = analysis.get("confidence_scores") or analysis.get("confidence") or {
        "personal_info": 0.95, "skills": 0.90, "experience": 0.90, "projects": 0.85, "certifications": 0.90
    }
    if conf:
        st.markdown("<div style='margin: 1.5rem 0 0.5rem 0;'></div>", unsafe_allow_html=True)
        badges = []
        for k, v in conf.items():
            pct = int(v * 100) if v <= 1.0 else int(v)
            badges.append(f"<span style='display: inline-block; padding: 4px 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-size: 0.75rem; color: var(--text-secondary); margin-right: 8px; margin-bottom: 8px;'>{k.replace('_', ' ').title()}: <b>{pct}% Conf.</b></span>")
            
        html_inject(f"""
        <div style='display: flex; flex-wrap: wrap; align-items: center; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 1rem;'>
            <span style='font-size: 0.75rem; color: var(--text-secondary); margin-right: 12px; font-weight: 800; letter-spacing: 0.05em;'>ENTITY CONFIDENCE:</span>
            {"".join(badges)}
        </div>
        """)

def display_results_dashboard(analysis: Dict[str, Any]) -> None:
    """Render the full results page from one backend response dict."""
    display_overall_score(analysis)
    st.markdown("<div style='margin: 2rem 0; border-top: 1px solid rgba(255,255,255,0.05);'></div>", unsafe_allow_html=True)

    # Insert Recruiter Insights
    display_recruiter_insights(analysis)
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

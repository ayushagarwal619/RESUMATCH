import requests
import streamlit as st

from frontend.services import api_client


def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is it running on port 8000?")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.error(f"Backend returned {exc.response.status_code}: {exc.response.text}")
    else:
        st.error(f"Unexpected error: {exc}")


def render() -> None:
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin: 0; background: linear-gradient(135deg, #FFFFFF 40%, #C084FC 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; letter-spacing: -0.02em;">Analysis History</h1>
        <p style="margin: 6px 0 0 0; font-size: 1.05rem; color: var(--text-secondary); font-weight: 500;">Review your past resume evaluations.</p>
    </div>
    """, unsafe_allow_html=True)

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.markdown("""
        <div class="glass-card" style="border-left: 4px solid var(--accent-yellow); border-color: var(--accent-yellow); padding: 1.5rem; margin-top: 1rem;">
            <div style="font-size: 1.8rem; margin-bottom: 0.5rem;">⚠️</div>
            <h3 style="color: white; margin: 0 0 0.5rem 0; font-weight: 700; font-size: 1.15rem;">Access Denied</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; margin: 0;">Please sign in from the sidebar to view your history list.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    try:
        history = api_client.get_history(access_token)
    except requests.RequestException as exc:
        _show_backend_error(exc)
        return

    if not history:
        st.markdown("""
        <div class="glass-card" style="padding: 2.5rem; text-align: center; margin-top: 1rem; border-color: rgba(255,255,255,0.03);">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📂</div>
            <h3 style="color: white; margin-top: 0; margin-bottom: 0.8rem; font-weight: 700; font-size: 1.4rem;">No Analyses Yet</h3>
            <p style="color: var(--text-secondary); font-size: 1rem; max-width: 420px; margin: 0 auto 2rem auto; line-height: 1.5;">You haven't analyzed any resumes on this account yet. Run your first evaluation to save results.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1.5, 2, 1.5])
        with col2:
            if st.button("🚀 Go to RESUMATCH Scorer", use_container_width=True, type="primary"):
                st.session_state.current_view = "scorer"
                st.rerun()
        return

    st.markdown(f"**Total saved evaluations:** {len(history)}")
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    for idx, entry in enumerate(history):
        filename = entry.get("filename", "resume")
        ats_score = float(entry.get("ats_score", 0))
        created_at = entry.get("created_at", "")
        analysis = entry.get("analysis_result", {}) or {}

        component_scores = analysis.get("component_scores", {}) or {}
        jd_comparison = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")

        # Title formatting
        title_str = f"📄 {filename}  |  Score: {ats_score:.0f}/100  |  {created_at}"

        with st.expander(title_str):
            st.markdown(
                f"""
                <div class="glass-card" style="padding: 1.2rem; margin-bottom: 1rem; border-color: rgba(255,255,255,0.02);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; text-align: center;">
                        <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: var(--radius-sm);">
                            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{ats_score:.0f}/100</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Overall</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: var(--radius-sm);">
                            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{component_scores.get('formatting', 0):.0f}/20</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Formatting</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: var(--radius-sm);">
                            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{component_scores.get('keywords', 0):.0f}/25</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Keywords</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: var(--radius-sm);">
                            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{component_scores.get('content', 0):.0f}/25</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Content</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: var(--radius-sm);">
                            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{component_scores.get('skill_validation', 0):.0f}/15</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Validation</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.02); padding: 8px; border-radius: var(--radius-sm);">
                            <div style="font-size: 1.5rem; font-weight: 800; color: white;">{component_scores.get('ats_compatibility', 0):.0f}/15</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase;">Compatibility</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if jd_comparison:
                st.markdown(
                    f"""
                    <div style="margin-bottom: 1rem; font-weight: 600; font-size: 0.9rem; color: var(--accent-purple);">
                        🎯 Job Description Match Rate: {jd_comparison.get('match_percentage', 0):.0f}%
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            entry_id = entry.get("id")
            if entry_id:
                if st.button("🗑️ Delete Analysis Record", key=f"delete_{idx}", type="secondary"):
                    try:
                        api_client.delete_history_entry(str(entry_id), access_token)
                        st.toast("Analysis record deleted successfully!")
                        st.rerun()
                    except requests.RequestException as exc:
                        _show_backend_error(exc)

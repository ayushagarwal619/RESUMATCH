import streamlit as st

def get_image_base64(path):
    import base64
    from pathlib import Path
    try:
        data = Path(path).read_bytes()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

def html_inject(html_str: str) -> None:
    import re
    clean = re.sub(r'\s+', ' ', html_str).strip()
    st.markdown(clean, unsafe_allow_html=True)

def render():
    # 1. Background Mesh Grid and Aurora Blobs
    html_inject("""
    <div class="bg-mesh-container">
        <div class="mesh-grid"></div>
        <div class="mesh-blob-1"></div>
        <div class="mesh-blob-2"></div>
    </div>
    """)

    # 2. Two-Column Hero Layout
    left_col, right_col = st.columns([1.2, 0.9])
    
    with left_col:
        # Side-by-side logo icon and text
        logo_base64 = get_image_base64("frontend/assets/logo_icon.jpg")
        html_inject(f"""
        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 1.5rem;">
            <img src="data:image/jpeg;base64,{logo_base64}" style="width: 34px; height: 34px; border-radius: 6px;" class="logo-img" />
            <span style="font-weight: 800; font-size: 1.4rem; letter-spacing: -0.02em; color: var(--text-primary); font-family: 'Plus Jakarta Sans', sans-serif;">RESUMATCH</span>
        </div>
        """)
        # Left-column text content
        html_inject("""
        <div style="padding-top: 0.5rem;">
            <div class="hero-badge">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="m12 3-1.912 5.886H3.82l4.816 3.498L6.724 18.27 12 14.772l5.276 3.498-1.912-5.886 4.816-3.498h-6.268L12 3z"/></svg>
                AI-POWERED ATS ANALYSIS
            </div>
            <h1 class="hero-title" style="font-size: clamp(2.5rem, 5.5vw, 4.5rem); font-weight: 800; line-height: 1.05; letter-spacing: -0.04em;">Optimize Your Resume.<br>Win More Interviews.</h1>
            <p class="hero-subtitle" style="font-size: clamp(1.05rem, 2.2vw, 1.35rem); line-height: 1.6; margin-bottom: 2.2rem; color: var(--text-secondary);">RESUMATCH gives you deep ATS insights, skill validation, and actionable feedback to make your resume stand out to recruiters.</p>
        </div>
        """)
        
        # Hero Buttons side-by-side
        btn_l, btn_r = st.columns([1.3, 1])
        with btn_l:
            if st.button("🚀 Scan Your Resume", key="hero_btn_scan", use_container_width=True, type="primary"):
                st.session_state.current_view = 'scorer'
                st.rerun()
        with btn_r:
            if st.button("👁️ View Live Demo", key="hero_btn_demo", use_container_width=True, type="secondary"):
                st.toast("Scan a resume below to explore the interactive results dashboard!")
                
        # Trust badges
        html_inject("""
        <div style="margin-top: 2rem; display: flex; align-items: center; gap: 20px; font-size: 0.85rem; color: var(--text-secondary); font-weight: 600;">
            <span style="display: flex; align-items: center; gap: 6px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                No Sign Up Required
            </span>
            <span style="display: flex; align-items: center; gap: 6px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                100% Free
            </span>
            <span style="display: flex; align-items: center; gap: 6px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-success)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
                Private & Secure
            </span>
        </div>
        """)

    with right_col:
        # Right-column: Simulated ATS Dashboard Visual illustration (Strictly style-free HTML tags to prevent escaping)
        html_inject("""
        <div class="glass-card floating-graphics animate-glow hero-dashboard-card">
            <div class="card-badge">PRO</div>
            <h4 class="report-header">ATS METRIC REPORT</h4>
            <div class="hero-dashboard-score-row">
                <span class="hero-dashboard-score-num">95</span>
                <span class="hero-dashboard-score-label">Excellent</span>
            </div>
            
            <div class="hero-dashboard-metric-item" style="margin-top: 2rem;">
                <div class="hero-dashboard-metric-header">
                    <span>Formatting Quality</span>
                    <span>19/20</span>
                </div>
                <div class="shimmer-progress"><div class="shimmer-progress-fill w-95"></div></div>
            </div>
            
            <div class="hero-dashboard-metric-item">
                <div class="hero-dashboard-metric-header">
                    <span>Keywords Match</span>
                    <span>24/25</span>
                </div>
                <div class="shimmer-progress"><div class="shimmer-progress-fill w-96 bg-blue"></div></div>
            </div>
            
            <div class="hero-dashboard-metric-item">
                <div class="hero-dashboard-metric-header">
                    <span>Skill Validation Proof</span>
                    <span>15/15</span>
                </div>
                <div class="shimmer-progress"><div class="shimmer-progress-fill w-100 bg-cyan"></div></div>
            </div>
        </div>
        """)

    # Scroll indicator
    html_inject("""
    <div style="text-align: center; margin-top: 4rem; margin-bottom: 3rem; opacity: 0.7;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="animation: bounce 2s infinite;"><path d="m6 9 6 6 6-6"/></svg>
        <style>
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-8px); }
                60% { transform: translateY(-4px); }
            }
        </style>
    </div>
    """)

    # Section 2: Statistics Row
    html_inject("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 2rem; margin-bottom: 5rem;">
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div class="counter-number">10,000+</div>
            <div class="counter-label">Resumes Analyzed</div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div class="counter-number">95%</div>
            <div class="counter-label">User Satisfaction</div>
        </div>
        <div class="glass-card" style="text-align: center; padding: 2rem;">
            <div class="counter-number">5</div>
            <div class="counter-label">Analysis Dimensions</div>
        </div>
    </div>
    """)

    # Section 3: Why Choose RESUMATCH? (Features Section)
    html_inject("""
    <div class="section-title">Why Choose RESUMATCH?</div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 2rem; margin-bottom: 5rem;">
        <div class="glass-card" style="padding: 2.2rem;">
            <div style="margin-bottom: 1.2rem; color: var(--accent-primary);">
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
            </div>
            <h3 style="color: var(--text-primary); font-size: 1.35rem; margin-bottom: 0.8rem; font-weight: 700;">Comprehensive Analysis</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">Get scored across 5 key dimensions: formatting, keywords, content quality, validation, and compatibility.</p>
        </div>
        <div class="glass-card" style="padding: 2.2rem;">
            <div style="margin-bottom: 1.2rem; color: var(--accent-primary);">
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="m9 12 2 2 4-4"/></svg>
            </div>
            <h3 style="color: var(--text-primary); font-size: 1.35rem; margin-bottom: 0.8rem; font-weight: 700;">Smart Skill Validation</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">Verifies your skills through project context and work history matches using semantic semantic checking.</p>
        </div>
        <div class="glass-card" style="padding: 2.2rem;">
            <div style="margin-bottom: 1.2rem; color: var(--accent-primary);">
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.886H3.82l4.816 3.498L6.724 18.27 12 14.772l5.276 3.498-1.912-5.886 4.816-3.498h-6.268L12 3z"/></svg>
            </div>
            <h3 style="color: var(--text-primary); font-size: 1.35rem; margin-bottom: 0.8rem; font-weight: 700;">Actionable Insights</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">Receive specific, prioritized action items to optimize your resume and win more interviews.</p>
        </div>
        <div class="glass-card" style="padding: 2.2rem;">
            <div style="margin-bottom: 1.2rem; color: var(--accent-primary);">
                <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </div>
            <h3 style="color: var(--text-primary); font-size: 1.35rem; margin-bottom: 0.8rem; font-weight: 700;">Privacy First</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">All evaluations run securely. Your personal details and resume data never leave your control.</p>
        </div>
    </div>
    """)

    # Section 4: How RESUMATCH Works (timeline)
    html_inject("""
    <div class="section-title">How RESUMATCH Works</div>
    <div class="timeline-container">
        <div class="timeline-step">
            <div class="step-num">1</div>
            <h3 style="color: var(--text-primary); font-size: 1.25rem; margin-bottom: 0.6rem; font-weight: 700;">Upload Resume</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0; line-height: 1.5;">Upload your resume in PDF, DOC, or DOCX formats securely.</p>
        </div>
        <div class="timeline-step">
            <div class="step-num">2</div>
            <h3 style="color: var(--text-primary); font-size: 1.25rem; margin-bottom: 0.6rem; font-weight: 700;">AI Scan</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0; line-height: 1.5;">Our custom scorer scans your projects and validates keywords.</p>
        </div>
        <div class="timeline-step">
            <div class="step-num">3</div>
            <h3 style="color: var(--text-primary); font-size: 1.25rem; margin-bottom: 0.6rem; font-weight: 700;">Optimize & Get Hired</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0; line-height: 1.5;">Apply structured, prioritized fixes to increase matches.</p>
        </div>
    </div>
    """)

    # Testimonials Carousel
    html_inject("""
    <div class="section-title">Trusted by Job Seekers</div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 5rem;">
        <div class="glass-card" style="padding: 1.8rem;">
            <p style="font-style: italic; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                "RESUMATCH helped me increase my ATS score from 62 to 94. Got 3x more interview calls!"
            </p>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: var(--accent-primary); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">RS</div>
                <div>
                    <h4 style="margin: 0; color: var(--text-primary); font-size: 0.95rem; font-weight: 700;">Rahul Sharma <span style="font-size: 0.75rem; color: var(--color-success); margin-left: 4px; font-weight: 800;">✓ Verified</span></h4>
                    <p style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Software Engineer at Hult Prize</p>
                </div>
            </div>
        </div>
        <div class="glass-card" style="padding: 1.8rem;">
            <p style="font-style: italic; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                "The insights are incredibly detailed and actionable. Worth every second!"
            </p>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: var(--accent-secondary); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">PS</div>
                <div>
                    <h4 style="margin: 0; color: var(--text-primary); font-size: 0.95rem; font-weight: 700;">Priya Singh <span style="font-size: 0.75rem; color: var(--color-success); margin-left: 4px; font-weight: 800;">✓ Verified</span></h4>
                    <p style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Product Manager</p>
                </div>
            </div>
        </div>
        <div class="glass-card" style="padding: 1.8rem;">
            <p style="font-style: italic; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.5rem;">
                "Best free ATS checker I've used. Highly recommended!"
            </p>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: var(--accent-highlight); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">AP</div>
                <div>
                    <h4 style="margin: 0; color: var(--text-primary); font-size: 0.95rem; font-weight: 700;">Amit Patel <span style="font-size: 0.75rem; color: var(--color-success); margin-left: 4px; font-weight: 800;">✓ Verified</span></h4>
                    <p style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Data Scientist</p>
                </div>
            </div>
        </div>
    </div>
    """)

    # Footer section
    html_inject("""
    <div style="margin-top: 5rem; border-top: var(--border-soft); padding-top: 2.5rem; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 20px; font-size: 0.85rem; color: var(--text-secondary);">
        <div>
            <span style="font-weight: 800; background: var(--grad-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">RESUMATCH</span> — © 2026. All rights reserved.
        </div>
        <div style="display: flex; gap: 20px;">
            <a href="https://github.com" target="_blank" style="color: var(--text-secondary); text-decoration: none;">GitHub</a>
            <a href="https://linkedin.com" target="_blank" style="color: var(--text-secondary); text-decoration: none;">LinkedIn</a>
            <a href="#" style="color: var(--text-secondary); text-decoration: none;">Privacy Policy</a>
            <a href="#" style="color: var(--text-secondary); text-decoration: none;">Terms of Service</a>
        </div>
    </div>
    """)

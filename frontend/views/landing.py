import streamlit as st

def render():
    # Hero Title and Subtitle Block
    st.markdown("""
    <div class="resumatch-hero">
        <div class="hero-badge">🤖 AI-POWERED ATS ANALYSIS</div>
        <div class="hero-title">Optimize Your Resume.<br>Win More Interviews.</div>
        <div class="hero-subtitle">RESUMATCH gives you deep ATS insights, skill validation, and actionable feedback to make your resume stand out to recruiters and tracking systems.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Call-to-Action Buttons
    col1, col2, col3, col4 = st.columns([1.2, 1.8, 1.8, 1.2])
    with col2:
        if st.button("🚀 Analyze Your Resume Now", use_container_width=True, type="primary"):
            st.session_state.current_view = 'scorer'
            st.rerun()
    with col3:
        if st.button("👁️ See How It Works", use_container_width=True, type="secondary"):
            st.toast("Scroll down to see the timeline & features!")
            
    # Floating Score Mockup Graphics
    st.markdown("""
    <div class="glass-card floating-graphics animate-glow" style="max-width: 440px; margin: 3rem auto 4rem auto; text-align: left;">
        <div class="card-badge">PRO</div>
        <h4 style="margin: 0; color: #64748B; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700;">ATS SCORE</h4>
        <div style="display: flex; align-items: baseline; gap: 10px; margin: 0.6rem 0;">
            <span style="font-size: 3.8rem; font-weight: 800; color: white; line-height: 1; letter-spacing: -0.03em;">95</span>
            <span style="font-size: 1.3rem; font-weight: 700; color: #10B981;">Excellent</span>
        </div>
        
        <div style="margin: 1.8rem 0 0.8rem 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px; font-weight: 500;">
                <span>Formatting Quality</span>
                <span>19/20</span>
            </div>
            <div class="shimmer-progress"><div class="shimmer-progress-fill" style="width: 95%;"></div></div>
        </div>
        
        <div style="margin: 0.8rem 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px; font-weight: 500;">
                <span>Keywords & Skills Match</span>
                <span>24/25</span>
            </div>
            <div class="shimmer-progress"><div class="shimmer-progress-fill" style="width: 96%; background: var(--accent-blue);"></div></div>
        </div>
        
        <div style="margin: 0.8rem 0;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px; font-weight: 500;">
                <span>Skill Validation Proof</span>
                <span>15/15</span>
            </div>
            <div class="shimmer-progress"><div class="shimmer-progress-fill" style="width: 100%; background: var(--accent-cyan);"></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 2: Statistics
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; margin-bottom: 5rem;">
        <div class="glass-card" style="text-align: center;">
            <div class="counter-number">10,000+</div>
            <div class="counter-label">Resumes Analyzed</div>
        </div>
        <div class="glass-card" style="text-align: center;">
            <div class="counter-number">95%</div>
            <div class="counter-label">User Satisfaction</div>
        </div>
        <div class="glass-card" style="text-align: center;">
            <div class="counter-number">5</div>
            <div class="counter-label">Analysis Dimensions</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 3: Why Choose RESUMATCH?
    st.markdown("""
    <div class="section-title">Why Choose RESUMATCH?</div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 2rem; margin-bottom: 5rem;">
        <div class="glass-card">
            <div style="font-size: 2.2rem; margin-bottom: 1.2rem;">📊</div>
            <h3 style="color: white; font-size: 1.3rem; margin-bottom: 0.6rem; font-weight: 700;">Comprehensive Analysis</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">Get scored across 5 dimensions: formatting, keywords, content, validation, and compatibility.</p>
        </div>
        <div class="glass-card">
            <div style="font-size: 2.2rem; margin-bottom: 1.2rem;">🧠</div>
            <h3 style="color: white; font-size: 1.3rem; margin-bottom: 0.6rem; font-weight: 700;">Smart Skill Validation</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">Verifies your skills through project context and work history matches using semantic checking.</p>
        </div>
        <div class="glass-card">
            <div style="font-size: 2.2rem; margin-bottom: 1.2rem;">⚡</div>
            <h3 style="color: white; font-size: 1.3rem; margin-bottom: 0.6rem; font-weight: 700;">Actionable Insights</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">Receive specific, prioritized action items to optimize your resume and win more interviews.</p>
        </div>
        <div class="glass-card">
            <div style="font-size: 2.2rem; margin-bottom: 1.2rem;">🔒</div>
            <h3 style="color: white; font-size: 1.3rem; margin-bottom: 0.6rem; font-weight: 700;">Privacy First</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin: 0;">All evaluations run securely. Your personal details and resume data never leave your control.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section 4: How RESUMATCH Works
    st.markdown("""
    <div class="section-title">How RESUMATCH Works</div>
    <div class="timeline-container">
        <div class="timeline-step">
            <div class="step-num">1</div>
            <h3 style="color: white; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 700;">Upload Resume</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">Upload your resume in PDF, DOC, or DOCX formats.</p>
        </div>
        <div class="timeline-step">
            <div class="step-num">2</div>
            <h3 style="color: white; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 700;">AI Analysis</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">AI scans and validates your skills, keywords, and action verbs.</p>
        </div>
        <div class="timeline-step">
            <div class="step-num">3</div>
            <h3 style="color: white; font-size: 1.2rem; margin-bottom: 0.5rem; font-weight: 700;">Get ATS Report</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0;">Get detailed reports, formatting reviews, and prioritized fixes.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Testimonials
    st.markdown("""
    <div class="section-title">Trusted by Job Seekers</div>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 5rem;">
        <div class="glass-card" style="padding: 1.6rem;">
            <p style="font-style: italic; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.2rem;">
                "RESUMATCH helped me increase my ATS score from 62 to 94. Got 3x more interview calls!"
            </p>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: #3B82F6; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">RS</div>
                <div>
                    <h4 style="margin: 0; color: white; font-size: 0.95rem; font-weight: 600;">Rahul Sharma</h4>
                    <p style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Software Engineer</p>
                </div>
            </div>
        </div>
        <div class="glass-card" style="padding: 1.6rem;">
            <p style="font-style: italic; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.2rem;">
                "The insights are incredibly detailed and actionable. Worth every second!"
            </p>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: #8B5CF6; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">PS</div>
                <div>
                    <h4 style="margin: 0; color: white; font-size: 0.95rem; font-weight: 600;">Priya Singh</h4>
                    <p style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Product Manager</p>
                </div>
            </div>
        </div>
        <div class="glass-card" style="padding: 1.6rem;">
            <p style="font-style: italic; color: var(--text-secondary); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.2rem;">
                "Best free ATS checker I've used. Highly recommended!"
            </p>
            <div style="display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 50%; background: #06B6D4; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">AP</div>
                <div>
                    <h4 style="margin: 0; color: white; font-size: 0.95rem; font-weight: 600;">Amit Patel</h4>
                    <p style="margin: 0; color: var(--text-muted); font-size: 0.8rem;">Data Scientist</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Bottom CTA banner
    st.markdown("""
    <div class="glass-card animate-glow" style="text-align: center; padding: 3rem 2rem; border-color: rgba(139, 92, 246, 0.4); margin-bottom: 2rem;">
        <h2 style="color: white; font-size: 2rem; font-weight: 800; margin-bottom: 0.8rem; letter-spacing: -0.02em;">Ready to Boost Your Resume Score?</h2>
        <p style="color: var(--text-secondary); font-size: 1.1rem; max-width: 500px; margin: 0 auto 2rem auto; line-height: 1.5;">Get started now and increase your chances of getting hired.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 2, 1.5])
    with col2:
        if st.button("🚀 Optimize Your Resume Now", key="bottom_cta", use_container_width=True, type="primary"):
            st.session_state.current_view = 'scorer'
            st.rerun()

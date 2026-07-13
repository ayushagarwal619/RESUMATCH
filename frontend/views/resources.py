import streamlit as st
import textwrap

def render():
    """Render the resources page"""
    
    st.markdown(
        textwrap.dedent("""
        <div style="margin-bottom: 2rem;">
            <h1 style="margin: 0; background: linear-gradient(135deg, var(--text-primary) 40%, var(--accent-primary) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; font-size: 2.5rem; letter-spacing: -0.02em;">Resources & Tips</h1>
            <p style="margin: 6px 0 0 0; font-size: 1.05rem; color: var(--text-secondary); font-weight: 600;">Learn how to optimize your resume for applicant tracking systems.</p>
        </div>
        """),
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card" style="border-left: 4px solid var(--color-success); border-color: var(--color-success); padding: 1.5rem; height: 100%;">
                <h3 style="color: var(--text-primary); font-size: 1.25rem; font-weight: 800; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">✅ Do's</h3>
                <ul style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.8; padding-left: 20px;">
                    <li>Use standard, clear section headings</li>
                    <li>Include relevant keywords from the job description</li>
                    <li>Use simple, clean formatting and bullet points</li>
                    <li>List technical skills explicitly in a skills block</li>
                    <li>Quantify achievements with business metrics and numbers</li>
                    <li>Use standard, web-safe fonts (Arial, Calibri, Times New Roman)</li>
                    <li>Save and export your resume as PDF or DOCX formats</li>
                </ul>
            </div>
            """),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card" style="border-left: 4px solid var(--color-danger); border-color: var(--color-danger); padding: 1.5rem; height: 100%;">
                <h3 style="color: var(--text-primary); font-size: 1.25rem; font-weight: 800; margin-bottom: 1rem; display: flex; align-items: center; gap: 8px;">❌ Don'ts</h3>
                <ul style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.8; padding-left: 20px;">
                    <li>Avoid inserting tables, text boxes, and complex diagrams</li>
                    <li>Don't hide contact info inside page headers/footers</li>
                    <li>Avoid graphic elements, profile photos, and ratings bars</li>
                    <li>Don't use fancy or non-standard custom fonts</li>
                    <li>Avoid columns (multi-column layouts can confuse parsers)</li>
                    <li>Don't keyword stuff or spam terms out of context</li>
                    <li>Avoid abbreviations without spelling them out first</li>
                </ul>
            </div>
            """),
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)
    st.markdown("## 🔑 Common ATS Keywords by Industry")
    
    tab1, tab2, tab3 = st.tabs(["💻 Tech", "💼 Business", "🎨 Creative"])
    
    with tab1:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card" style="padding: 1.5rem; margin-top: 10px;">
                <h4 style="color: var(--text-primary); font-size: 1.1rem; font-weight: 800; margin-bottom: 12px;">Software Engineering & DevOps</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    <span class="skill-chip skill-chip-validated">Python</span>
                    <span class="skill-chip skill-chip-validated">Java</span>
                    <span class="skill-chip skill-chip-validated">JavaScript</span>
                    <span class="skill-chip skill-chip-validated">React.js</span>
                    <span class="skill-chip skill-chip-validated">Node.js</span>
                    <span class="skill-chip skill-chip-validated">Git</span>
                    <span class="skill-chip skill-chip-validated">Docker</span>
                    <span class="skill-chip skill-chip-validated">Kubernetes</span>
                    <span class="skill-chip skill-chip-validated">CI/CD</span>
                    <span class="skill-chip skill-chip-validated">Agile</span>
                    <span class="skill-chip skill-chip-validated">Scrum</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
    
    with tab2:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card" style="padding: 1.5rem; margin-top: 10px;">
                <h4 style="color: var(--text-primary); font-size: 1.1rem; font-weight: 800; margin-bottom: 12px;">Management & Business Operations</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    <span class="skill-chip skill-chip-validated">Project Management</span>
                    <span class="skill-chip skill-chip-validated">Stakeholder Engagement</span>
                    <span class="skill-chip skill-chip-validated">Budget Allocation</span>
                    <span class="skill-chip skill-chip-validated">Strategic Planning</span>
                    <span class="skill-chip skill-chip-validated">Team Leadership</span>
                    <span class="skill-chip skill-chip-validated">Financial Modeling</span>
                    <span class="skill-chip skill-chip-validated">A/B Testing</span>
                    <span class="skill-chip skill-chip-validated">KPI Tracking</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
    
    with tab3:
        st.markdown(
            textwrap.dedent("""
            <div class="glass-card" style="padding: 1.5rem; margin-top: 10px;">
                <h4 style="color: var(--text-primary); font-size: 1.1rem; font-weight: 800; margin-bottom: 12px;">Creative Design & Product Strategy</h4>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    <span class="skill-chip skill-chip-validated">Adobe Creative Suite</span>
                    <span class="skill-chip skill-chip-validated">UI/UX Design</span>
                    <span class="skill-chip skill-chip-validated">Figma</span>
                    <span class="skill-chip skill-chip-validated">Wireframing</span>
                    <span class="skill-chip skill-chip-validated">Prototyping</span>
                    <span class="skill-chip skill-chip-validated">Brand Identity</span>
                    <span class="skill-chip skill-chip-validated">Visual Communication</span>
                    <span class="skill-chip skill-chip-validated">User Research</span>
                </div>
            </div>
            """),
            unsafe_allow_html=True
        )
    
    st.markdown("<div style='margin-bottom: 3rem;'></div>", unsafe_allow_html=True)
    st.markdown("## 📄 ATS-Friendly Resume Templates")
    st.markdown(
        textwrap.dedent("""
        <div class="glass-card" style="border-left: 4px solid var(--accent-primary); border-color: var(--accent-primary); padding: 1.5rem;">
            <h3 style="color: var(--text-primary); font-size: 1.2rem; font-weight: 800; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 8px;">📋 Templates Coming Soon</h3>
            <p style="color: var(--text-secondary); font-size: 0.95rem; margin: 0; line-height: 1.5;">We are curating a set of professional, single-column Google Docs and Microsoft Word resume templates that guarantee 100% parsing accuracy on any applicant tracking system.</p>
        </div>
        """),
        unsafe_allow_html=True
    )

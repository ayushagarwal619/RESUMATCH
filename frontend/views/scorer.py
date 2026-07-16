from typing import Optional
import textwrap
import requests
import streamlit as st

from frontend.services import api_client
from frontend.components.dashboard import display_results_dashboard


def _read_jd(jd_file, jd_text: str) -> str:
    """
    Turn whatever the user provided into a plain JD string for the backend.
    """
    if jd_text:
        return jd_text.strip()
    if jd_file is None:
        return ""
    if jd_file.name.lower().endswith(".txt"):
        return jd_file.getvalue().decode("utf-8", errors="ignore")
    st.warning(
        "Job description files must be `.txt` for now — paste the JD text instead "
        "if you have a PDF or DOCX."
    )
    return ""


def _show_backend_error(exc: Exception) -> None:
    """Translate a `requests` exception into a friendly Streamlit error."""
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is `uvicorn backend.main:app` running on port 8000?")
    elif isinstance(exc, requests.Timeout):
        st.error("The backend took too long to respond. Try a smaller resume or check the server logs.")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        try:
            detail = exc.response.json().get("detail", exc.response.text)
        except ValueError:
            detail = exc.response.text
        
        detail_str = str(detail)
        is_parser_error = any(
            kw in detail_str.lower()
            for kw in [
                "scanned", "ocr", "tesseract", "selectable", 
                "pdfplumber", "pypdf2", "parsing failed"
            ]
        ) or ("could not read or parse" in detail_str.lower() and "exceeds" not in detail_str.lower() and "empty" not in detail_str.lower())
        
        if is_parser_error:
            st.markdown(
                textwrap.dedent("""
                <div class="danger-card animate-glow" style="padding: 1.8rem; margin: 1.5rem 0;">
                    <h3 style="color: var(--color-danger); margin-top: 0; margin-bottom: 0.8rem; font-size: 1.3rem; font-weight: 800; display: flex; align-items: center; gap: 8px;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                        Scanned PDF detected
                    </h3>
                    <p style="color: var(--text-primary); margin-bottom: 1rem; font-weight: 700;">
                        This resume appears to be a scanned or image-based PDF.
                    </p>
                    <p style="color: var(--text-secondary); margin-bottom: 1.2rem; font-size: 0.95rem; line-height: 1.6;">
                        Currently <strong>RESUMATCH</strong> supports only text-based PDFs. OCR support is currently unavailable but is coming soon.<br>
                        Please upload a text-based PDF, DOC, or DOCX.
                    </p>
                </div>
                """),
                unsafe_allow_html=True
            )
        else:
            st.error(f"Backend returned {exc.response.status_code}: {detail}")
    else:
        st.error(f"Unexpected error: {exc}")


def _summary_text(analysis: dict) -> str:
    """Tiny client-side text summary for the Download button."""
    score = analysis.get("ATS_score", analysis.get("ats_score", 0))
    lines = [f"ATS Score: {score:.0f}/100", ""]
    if analysis.get("strengths"):
        lines.append("STRENGTHS:")
        lines.extend(f"  - {s}" for s in analysis["strengths"])
        lines.append("")
    if analysis.get("critical_issues"):
        lines.append("CRITICAL ISSUES:")
        lines.extend(f"  - {s}" for s in analysis["critical_issues"])
        lines.append("")
    if analysis.get("suggestions"):
        lines.append("SUGGESTIONS:")
        lines.extend(f"  - {s}" for s in analysis["suggestions"])
    return "\n".join(lines)


def _render_upload_area(analysis_mode: str):
    """Two-column custom premium upload widgets. Returns (resume_file, jd_file, jd_text)."""
    left, right = st.columns(2)

    with left:
        st.markdown(
            textwrap.dedent("""
            <div class="custom-upload-container">
                <div class="upload-illustration">
                    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="floating-icon"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                </div>
                <h4>Upload your Resume</h4>
                <p class="upload-sub">Drag & drop or browse your local files</p>
                <div class="format-chips">
                    <span>PDF</span>
                    <span>DOC</span>
                    <span>DOCX</span>
                </div>
                <div class="max-size-label">MAX FILE SIZE: 5MB</div>
            </div>
            """),
            unsafe_allow_html=True
        )
        
        resume_file = st.file_uploader(
            "Upload your file here",
            type=["pdf", "doc", "docx"],
            label_visibility="collapsed",
            key="resume_upload",
        )
        if resume_file:
            html_inject(f"""
            <div class="file-preview-card glass-card">
                <div class="file-icon">📄</div>
                <div class="file-info">
                    <div class="file-name">{resume_file.name}</div>
                    <div class="file-size">{resume_file.size / 1024:.1f} KB</div>
                </div>
                <div class="file-status-badge">READY</div>
            </div>
            """)

    jd_file: Optional[object] = None
    jd_text = ""

    with right:
        if analysis_mode == "Job Description Comparison":
            st.markdown(
                textwrap.dedent("""
                <div class="custom-upload-container">
                    <div class="upload-illustration">
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="floating-icon" style="animation-delay: 1.5s;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
                    </div>
                    <h4>Target Job Description</h4>
                    <p class="upload-sub">Provide the job listing text or upload requirements</p>
                </div>
                """),
                unsafe_allow_html=True
            )
            
            jd_method = st.radio(
                "Input method:",
                ["Paste Text", "Upload .txt File"],
                horizontal=True,
                label_visibility="collapsed",
                key="jd_input_method",
            )
            
            st.markdown("<div style='margin-bottom: 0.5rem;'></div>", unsafe_allow_html=True)
            
            if jd_method == "Upload .txt File":
                jd_file = st.file_uploader(
                    "Choose JD file (.txt only)",
                    type=["txt"],
                    key="jd_upload",
                )
                if jd_file:
                    html_inject(f"""
                    <div class="file-preview-card glass-card">
                        <div class="file-icon">📄</div>
                        <div class="file-info">
                            <div class="file-name">{jd_file.name}</div>
                            <div class="file-size">{jd_file.size / 1024:.1f} KB</div>
                        </div>
                        <div class="file-status-badge">READY</div>
                    </div>
                    """)
            else:
                jd_text = st.text_area(
                    "Paste job description text:",
                    height=130,
                    placeholder="Paste the Job Description here...",
                    label_visibility="collapsed",
                    key="jd_text",
                )
                if jd_text:
                    html_inject(f"""
                    <div class="file-preview-card glass-card">
                        <div class="file-icon">📝</div>
                        <div class="file-info">
                            <div class="file-name">Job Description Text</div>
                            <div class="file-size">{len(jd_text)} characters</div>
                        </div>
                        <div class="file-status-badge">READY</div>
                    </div>
                    """)
        else:
            st.markdown(
                textwrap.dedent("""
                <div class="custom-upload-container" style="opacity: 0.5; cursor: not-allowed; border-style: solid; border-color: var(--border-soft);">
                    <div class="upload-illustration">
                        <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-muted);"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                    </div>
                    <h4 style="color: var(--text-muted);">JD Match Disabled</h4>
                    <p class="upload-sub" style="color: var(--text-muted); margin-bottom: 0;">Switch to Job Description Comparison mode in options to paste requirements.</p>
                </div>
                """),
                unsafe_allow_html=True
            )

    return resume_file, jd_file, jd_text


def _render_export_buttons(analysis: dict) -> None:
    st.markdown(
        textwrap.dedent("""
        <div style="margin-top: 3rem; margin-bottom: 1.5rem;">
            <h3 style="color: var(--text-primary); font-size: 1.4rem; font-weight: 800;">📥 Export Evaluation Results</h3>
        </div>
        """),
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)

    with c1:
        if st.button("📑 Generate PDF Report", key="btn_gen_pdf", use_container_width=True, type="primary"):
            try:
                with st.spinner("Generating PDF on backend..."):
                    pdf_bytes = api_client.generate_pdf(
                        analysis,
                        access_token=st.session_state["access_token"],
                    )
                st.session_state["scorer_pdf_bytes"] = pdf_bytes
            except requests.RequestException as exc:
                _show_backend_error(exc)

        if "scorer_pdf_bytes" in st.session_state:
            st.download_button(
                "⬇️ Download PDF Report",
                data=st.session_state["scorer_pdf_bytes"],
                file_name="ats_resume_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_report",
            )

    with c2:
        st.download_button(
            "📄 Download Summary (.txt)",
            data=_summary_text(analysis),
            file_name="ats_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_summary",
        )


def render() -> None:
    st.markdown(
        textwrap.dedent("""
        <div class="premium-hero">
            <div class="hero-glow-blob"></div>
            <h1 class="hero-title">Optimize Your Resume. Win Interviews.</h1>
            <p class="hero-subtitle">Upload your resume to receive instantaneous, recruiter-grade ATS scoring, structural audit, and keywords compatibility match.</p>
            <div class="trust-badges">
                <span class="trust-badge"><span class="badge-dot dot-purple"></span> ATS Optimized</span>
                <span class="trust-badge"><span class="badge-dot dot-blue"></span> Recruiter Grade</span>
                <span class="trust-badge"><span class="badge-dot dot-green"></span> AI Powered</span>
            </div>
        </div>
        """),
        unsafe_allow_html=True
    )

    with st.sidebar:
        st.markdown("<div style='margin: 1.5rem 0 1rem 0; border-top: var(--border-soft);'></div>", unsafe_allow_html=True)
        st.markdown("## 📊 Analysis Options")
        st.info(
            "**General ATS Score**: resume only — overall compatibility.\n\n"
            "**JD Comparison**: resume + job description — targeted match analysis."
        )

    analysis_mode = st.radio(
        "Select Analysis Mode:",
        ["General ATS Score", "Job Description Comparison"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<div style='margin: 1.5rem 0;'></div>", unsafe_allow_html=True)

    resume_file, jd_file, jd_text = _render_upload_area(analysis_mode)

    st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)

    if not resume_file:
        st.info("👆 Upload your resume to begin the evaluation.")
        if st.session_state.get("scorer_analysis"):
            display_results_dashboard(st.session_state["scorer_analysis"])
        return

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.warning("⚠️ Please sign in from the sidebar to start analyzing your resume.")
        return

    _, mid, _ = st.columns([1.2, 1.6, 1.2])
    with mid:
        analyze = st.button("⚡ Run RESUMATCH AI Scorer", key="btn_run_scorer", use_container_width=True, type="primary")

    if not analyze:
        if st.session_state.get("scorer_analysis"):
            display_results_dashboard(st.session_state["scorer_analysis"])
            _render_export_buttons(st.session_state["scorer_analysis"])
        return

    st.session_state.pop("scorer_pdf_bytes", None)
    st.session_state.pop("scorer_analysis", None)

    job_description = _read_jd(jd_file, jd_text) if analysis_mode == "Job Description Comparison" else ""

    try:
        with st.spinner("Analyzing your resume... this can take 10–30 seconds."):
            analysis = api_client.analyze_resume(
                resume_file=resume_file,
                access_token=access_token,
                job_description=job_description,
            )
    except requests.RequestException as exc:
        _show_backend_error(exc)
        return

    st.session_state["scorer_analysis"] = analysis
    import json
    print("==========================================")
    print("STREAMLIT RECEIVED ANALYSIS JSON:")
    print(json.dumps(analysis, indent=2))
    print("==========================================")
    st.success("✅ Analysis complete!")
    display_results_dashboard(analysis)
    _render_export_buttons(analysis)

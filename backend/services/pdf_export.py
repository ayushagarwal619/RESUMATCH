import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

logger = logging.getLogger('ats_resume_scorer')

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b")) # Slate 500
        
        # Generation time
        now_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        self.drawString(54, 36, f"Generated on {now_str} | Powered by RESUMATCH")
        
        # Page number
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(self._pagesize[0] - 54, 36, page_text)
        self.restoreState()

def generate_pdf_report(analysis_data: Dict[str, Any], candidate_name: str = "Candidate") -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=60
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Modify normal
    normal_style = styles['Normal']
    normal_style.fontName = 'Helvetica'
    normal_style.fontSize = 9.5
    normal_style.leading = 14
    normal_style.textColor = colors.HexColor("#334155")
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=10
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16.5,
        textColor=colors.HexColor("#1e1b4b"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155")
    )
    
    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    
    # 1. Header with Logo & Brand
    logo_path = Path(__file__).resolve().parent.parent.parent / 'frontend' / 'assets' / 'logo_icon.jpg'
    if not logo_path.exists():
        logo_path = Path(__file__).resolve().parent.parent.parent / 'frontend' / 'assets' / 'logo.jpg'
        
    logo_flowable = ""
    if logo_path.exists():
        try:
            logo_flowable = Image(str(logo_path), width=28, height=28)
        except Exception:
            pass
            
    if logo_flowable:
        header_data = [
            [
                logo_flowable,
                Paragraph("<b>RESUMATCH</b> — Match. Optimize. Get Hired.", subtitle_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[36, 468])
    else:
        # Graceful fallback text header
        header_data = [
            [
                Paragraph("<b><font color='#6366f1'>✦ RESUMATCH</font></b> — Match. Optimize. Get Hired.", subtitle_style)
            ]
        ]
        header_table = Table(header_data, colWidths=[504])
        
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    
    # 2. Premium ATS Score Banner Card (Dark theme cover-like card)
    overall_score = int(analysis_data.get('ATS_score', 0) or analysis_data.get('ats_score', 0))
    if overall_score >= 80:
        score_color = colors.HexColor("#16a34a") # green
        score_bg = colors.HexColor("#f0fdf4")
    elif overall_score >= 60:
        score_color = colors.HexColor("#ea580c") # amber
        score_bg = colors.HexColor("#fffbeb")
    else:
        score_color = colors.HexColor("#dc2626") # red
        score_bg = colors.HexColor("#fef2f2")
        
    score_display_style = ParagraphStyle(
        'OverallScoreText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=38,
        leading=42,
        textColor=score_color,
        alignment=1
    )
    
    score_label_style = ParagraphStyle(
        'OverallScoreLabelText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569"),
        alignment=1
    )
    
    # Score circle container table (renders as a nested card inside the dark card)
    score_circle_data = [
        [Paragraph(f"{overall_score}", score_display_style)],
        [Paragraph("ATS SCORE", score_label_style)]
    ]
    score_circle_table = Table(score_circle_data, colWidths=[100])
    score_circle_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), score_bg),
        ('BOX', (0,0), (-1,-1), 2, score_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    info_data = [
        [
            Paragraph(f"<font size=15 color='#ffffff'><b>ATS Resume Evaluation Report</b></font><br/>"
                      f"<font size=11 color='#cbd5e1'>Candidate: <b>{candidate_name}</b></font><br/>"
                      f"<font size=9 color='#94a3b8'>Evaluation Date: {date_str}</font><br/>"
                      f"<font size=8.5 color='#a78bfa'><b>RESUMATCH PREMIUM EVALUATION SYSTEM</b></font>", body_style),
            score_circle_table
        ]
    ]
    info_table = Table(info_data, colWidths=[364, 140])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), # Slate 900 (Dark SaaS card background)
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor("#1e293b")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 16),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))
    
    # 3. Score Breakdown Section
    story.append(Paragraph("Score Breakdown", section_heading))
    cs = analysis_data.get('component_scores') or {}
    if hasattr(cs, '__dict__'):
        cs = cs.__dict__
        
    def get_score_pct(score_val, max_val):
        try:
            return min(100, max(0, int((float(score_val) / max_val) * 100)))
        except Exception:
            return 0
            
    formatting_score = float(cs.get('formatting', 0))
    keywords_score = float(cs.get('keywords', 0))
    content_score = float(cs.get('content', 0))
    skill_score = float(cs.get('skill_validation', 0))
    compat_score = float(cs.get('ats_compatibility', 0))
    
    formatting_pct = get_score_pct(formatting_score, 20)
    keywords_pct = get_score_pct(keywords_score, 25)
    content_pct = get_score_pct(content_score, 25)
    skill_pct = get_score_pct(skill_score, 15)
    compat_pct = get_score_pct(compat_score, 15)
    
    def make_progress_bar(score_pct):
        bar_width = 120
        filled_width = max(1, min(bar_width, int(score_pct * (bar_width / 100.0))))
        empty_width = bar_width - filled_width
        
        # Color bar: purple → blue based on percentage
        bar_color = "#6366f1" if score_pct >= 80 else ("#3b82f6" if score_pct >= 60 else "#8b5cf6")
        
        bar_table = Table([["", ""]], colWidths=[filled_width, empty_width], rowHeights=[8])
        bar_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor(bar_color)),
            ('BACKGROUND', (1,0), (1,0), colors.HexColor("#e2e8f0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        return bar_table
        
    breakdown_data = [
        [Paragraph("<b>Evaluation Dimension</b>", body_style), Paragraph("<b>Score</b>", body_style), Paragraph("<b>Percentage</b>", body_style), Paragraph("<b>Visual Match</b>", body_style)],
        [Paragraph("Formatting & Structure", body_style), f"{formatting_score} / 20", f"{formatting_pct}%", make_progress_bar(formatting_pct)],
        [Paragraph("Keyword Matching", body_style), f"{keywords_score} / 25", f"{keywords_pct}%", make_progress_bar(keywords_pct)],
        [Paragraph("Content Quality", body_style), f"{content_score} / 25", f"{content_pct}%", make_progress_bar(content_pct)],
        [Paragraph("Skill Validation", body_style), f"{skill_score} / 15", f"{skill_pct}%", make_progress_bar(skill_pct)],
        [Paragraph("ATS Compatibility", body_style), f"{compat_score} / 15", f"{compat_pct}%", make_progress_bar(compat_pct)],
    ]
    breakdown_table = Table(breakdown_data, colWidths=[174, 80, 80, 170])
    breakdown_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor("#cbd5e1")),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 15))
    
    # 4. Strengths & Critical Issues in Side-by-Side Themed Cards
    strengths = analysis_data.get('strengths', [])
    critical_issues = analysis_data.get('critical_issues', [])
    
    # Strengths Card (Soft Green)
    str_story = [Paragraph("<b>✓ Key Strengths</b>", ParagraphStyle('StrHeader', parent=body_style, fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#15803d"), spaceAfter=6))]
    if strengths:
        for strength in strengths:
            str_story.append(Paragraph(f"<font color='#16a34a'><b>✓</b></font> {strength}", bullet_style))
    else:
        str_story.append(Paragraph("No specific strengths noted.", body_style))
        
    str_card = Table([[str_story]], colWidths=[238])
    str_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0fdf4")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bbf7d0")),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    
    # Critical Issues Card (Soft Red)
    issue_story = [Paragraph("<b>✗ Critical Issues</b>", ParagraphStyle('IssueHeader', parent=body_style, fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#b91c1c"), spaceAfter=6))]
    if critical_issues:
        for issue in critical_issues:
            issue_story.append(Paragraph(f"<font color='#dc2626'><b>✗</b></font> {issue}", bullet_style))
    else:
        issue_story.append(Paragraph("No critical issues found.", body_style))
        
    issue_card = Table([[issue_story]], colWidths=[238])
    issue_card.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#fef2f2")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#fecaca")),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    
    sc_table = Table([[str_card, issue_card]], colWidths=[248, 256])
    sc_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(sc_table)
    story.append(Spacer(1, 15))
    
    # 5. Skill Validation Details as Colored Chips/Tags
    svd = analysis_data.get('skill_validation_details') or {}
    if hasattr(svd, 'model_dump'):
        svd = svd.model_dump()
        
    validated_skills = svd.get('validated', [])
    unvalidated_skills = svd.get('unvalidated', [])
    
    story.append(Paragraph("Skill Validation Results", section_heading))
    
    def make_skills_chips(skills_list, is_validated=True):
        if not skills_list:
            return Paragraph("None detected", body_style)
            
        cols = 3
        rows = []
        current_row = []
        
        bg_color = "#f3e8ff" if is_validated else "#f1f5f9"
        border_color = "#d8b4fe" if is_validated else "#cbd5e1"
        text_color = "#6b21a8" if is_validated else "#334155"
        
        for skill in skills_list:
            if isinstance(skill, dict):
                skill_name = skill.get('skill', '')
                projects = skill.get('projects', [])
                proj_str = f" ({len(projects)} prj)" if projects else ""
                display_text = f"<b>{skill_name}</b>{proj_str}"
            else:
                display_text = f"{skill}"
                
            p = Paragraph(f"<font color='{text_color}'>{display_text}</font>", ParagraphStyle('ChipText', parent=body_style, fontSize=8.5, alignment=1))
            current_row.append(p)
            if len(current_row) == cols:
                rows.append(current_row)
                current_row = []
                
        if current_row:
            while len(current_row) < cols:
                current_row.append("")
            rows.append(current_row)
            
        if not rows:
            return Paragraph("None", body_style)
            
        t = Table(rows, colWidths=[168, 168, 168])
        t_style = [
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]
        
        for r_idx, row in enumerate(rows):
            for c_idx, cell in enumerate(row):
                if cell != "":
                    t_style.append(('BACKGROUND', (c_idx, r_idx), (c_idx, r_idx), colors.HexColor(bg_color)))
                    t_style.append(('BOX', (c_idx, r_idx), (c_idx, r_idx), 0.5, colors.HexColor(border_color)))
                    
        t.setStyle(TableStyle(t_style))
        return t

    story.append(Paragraph("<b>Validated Skills</b> (found in project/experience descriptions):", body_style))
    story.append(Spacer(1, 4))
    story.append(make_skills_chips(validated_skills, is_validated=True))
    
    if unvalidated_skills:
        story.append(Spacer(1, 10))
        story.append(Paragraph("<b>Unvalidated Skills</b> (listed but lacking context):", body_style))
        story.append(Spacer(1, 4))
        story.append(make_skills_chips(unvalidated_skills, is_validated=False))
        
    story.append(Spacer(1, 15))
    
    # 6. Detailed Recommendations & Left-Border Severity Cards
    raw_feedback = analysis_data.get('detailed_feedback', [])
    def to_dict(item):
        if isinstance(item, dict):
            return item
        return item.model_dump() if hasattr(item, 'model_dump') else item.__dict__
        
    feedback_items = [to_dict(fb) for fb in raw_feedback]
    if feedback_items:
        story.append(Paragraph("Detailed Recommendations & Actions", section_heading))
        for idx, fb in enumerate(feedback_items):
            title = fb.get('issue_title', 'Issue')
            severity = fb.get('severity_level', 'Info').upper()
            impact = fb.get('ats_impact', 'Low')
            explanation = fb.get('explanation', '')
            where = fb.get('where_it_appears', '')
            fix = fb.get('how_to_fix', '')
            action_items = fb.get('action_items', [])
            example = fb.get('example_improvement', '')
            
            if severity in ("HIGH", "CRITICAL"):
                severity_color = "#dc2626"
                bg_card = "#fff5f5"
            elif severity in ("MODERATE", "MEDIUM"):
                severity_color = "#ea580c"
                bg_card = "#fffbeb"
            else:
                severity_color = "#2563eb"
                bg_card = "#eff6ff"
                
            issue_story = []
            issue_story.append(Paragraph(f"<b>{idx+1}. {title}</b>", ParagraphStyle('FbTitle', parent=body_style, fontName='Helvetica-Bold', fontSize=10.5, textColor=colors.HexColor("#0f172a"))))
            issue_story.append(Spacer(1, 3))
            issue_story.append(Paragraph(f"<font color='{severity_color}'><b>{severity}</b></font> | Impact: <b>{impact}</b> | Location: <i>{where if where else 'General'}</i>", ParagraphStyle('FbMeta', parent=body_style, fontSize=8.5, textColor=colors.HexColor("#475569"))))
            issue_story.append(Spacer(1, 5))
            issue_story.append(Paragraph(f"<b>Explanation:</b> {explanation}", body_style))
            if fix:
                issue_story.append(Spacer(1, 2))
                issue_story.append(Paragraph(f"<b>Recommendation:</b> {fix}", body_style))
                
            if action_items:
                issue_story.append(Spacer(1, 4))
                for item in action_items:
                    issue_story.append(Paragraph(f"<font color='{severity_color}'>•</font> {item}", bullet_style))
                    
            if example:
                issue_story.append(Spacer(1, 4))
                issue_story.append(Paragraph(f"<i>Example Improvement:</i> {example}", ParagraphStyle('ExampleStyle', parent=body_style, fontSize=8.5, leftIndent=10, textColor=colors.HexColor("#475569"))))
                
            # Render left-border card
            card_table = Table([[issue_story]], colWidths=[480])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_card)),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ('LINELEFT', (0,0), (0,-1), 4, colors.HexColor(severity_color)),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 12),
                ('RIGHTPADDING', (0,0), (-1,-1), 12),
            ]))
            
            story.append(KeepTogether(card_table))
            story.append(Spacer(1, 10))
            
    # 7. Job Description comparison
    jd_analysis = analysis_data.get('jd_match_analysis') or analysis_data.get('jd_comparison') or {}
    if hasattr(jd_analysis, 'model_dump'):
        jd_analysis = jd_analysis.model_dump()
        
    if jd_analysis and jd_analysis.get('match_percentage', 0) > 0:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Job Description Matching & Keywords", section_heading))
        match_pct = jd_analysis.get('match_percentage', 0.0)
        sim = jd_analysis.get('semantic_similarity', 0.0)
        matched = jd_analysis.get('matched_keywords', [])
        missing = jd_analysis.get('missing_keywords', [])
        gap = jd_analysis.get('skills_gap', [])
        
        story.append(Paragraph(f"<b>Job Description Match:</b> {match_pct}% (Semantic similarity: {sim})", body_style))
        if matched:
            story.append(Paragraph(f"<b>Matched Keywords:</b> {', '.join(matched[:15])}", body_style))
        if missing:
            story.append(Paragraph(f"<b>Missing Keywords:</b> <font color='#dc2626'>{', '.join(missing[:15])}</font>", body_style))
        if gap:
            story.append(Paragraph(f"<b>Skills Gap:</b> {', '.join(gap[:15])}", body_style))
            
    doc.build(story, canvasmaker=NumberedCanvas)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_combined_pdf(html_docs: Dict[str, str]) -> bytes:
    # Deprecated fallback that returns a simple PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>RESUMATCH PDF Export Fallback</b>", styles['Heading1']),
        Spacer(1, 10),
        Paragraph("This fallback PDF generation has been replaced with the native ReportLab generate_pdf_report service.", styles['Normal'])
    ]
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

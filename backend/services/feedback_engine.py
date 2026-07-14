import re
from typing import List, Dict, Any, Optional
from backend.models.schemas import IssueDetail

def analyze_issues(
        resume_text: str, 
        parsed_resume: Dict, 
        skills: List[str], 
        projects: List[Dict], 
        action_verbs: List[str], 
        skill_validation: Dict, 
        scores: Dict, 
        contact_info: Optional[Dict] = None, 
) -> List[IssueDetail]:
    
    detected: List[IssueDetail] = []
    contact = parsed_resume.get('personal_info', {})
    exp_entries = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    proj_entries = [p for p in parsed_resume.get('projects', []) if isinstance(p, dict)]
    
    # 1. Missing Core Sections (High)
    missing_sections = []
    if not exp_entries: missing_sections.append("Work Experience")
    if not proj_entries: missing_sections.append("Projects")
    if not parsed_resume.get('education'): missing_sections.append("Education")
    
    if missing_sections:
        detected.append(IssueDetail(
            issue_title=f"Missing Critical Resume Sections",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Your resume is missing standard recruiter-expected sections: {', '.join(missing_sections)}. "
                "Hiring pipelines use parsing templates to locate historical data; missing sections often trigger automatic exclusions."
            ),
            where_it_appears="Structure check — sections missing",
            how_to_fix=f"Create clear markdown headers for: {', '.join([s.upper() for s in missing_sections])}.",
            action_items=[f"Add a dedicated '{s.upper()}' section" for s in missing_sections],
            example_improvement="EXPERIENCE\n• Software Engineer | Vercel\n• Designed backend API endpoints..."
        ))

    # 2. Incomplete Contact Details (High)
    missing_contacts = []
    if not contact.get('email'): missing_contacts.append('email address')
    if not contact.get('phone'): missing_contacts.append('phone number')
    if not contact.get('linkedin'): missing_contacts.append('LinkedIn profile link')
    if not contact.get('github'): missing_contacts.append('GitHub profile link')

    if missing_contacts:
        detected.append(IssueDetail(
            issue_title="Incomplete Recruiter Contact Details",
            severity_level="High",
            ats_impact="High",
            explanation=(
                f"Your contact header is missing: {', '.join(missing_contacts)}. "
                "Recruiters require active professional profiles and communication channels to pre-screen and schedule interviews."
            ),
            where_it_appears="Top contact header",
            how_to_fix=f"Include your {' and '.join(missing_contacts)} prominently at the top.",
            action_items=[f"Add your {item} in the header block" for item in missing_contacts],
            example_improvement=f"{contact.get('name') or 'Candidate Name'} | email@domain.com | linkedin.com/in/username | github.com/username"
        ))

    # 3. Lack of Quantitative Metrics (Medium)
    metric_count = 0
    number_patterns = [r'\d+%', r'\$\d+', r'\d+[kKmMbB]', r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+']
    for exp in exp_entries:
        desc = exp.get('description') or ''
        for pat in number_patterns:
            metric_count += len(re.findall(pat, desc))
            
    if metric_count == 0 and exp_entries:
        title_ev = exp_entries[0].get('job_title', 'Developer')
        comp_ev = exp_entries[0].get('company', 'Vercel')
        detected.append(IssueDetail(
            issue_title="No Quantifiable Achievements Found",
            severity_level="Medium",
            ats_impact="Medium",
            explanation=(
                f"Your role as '{title_ev}' at '{comp_ev}' lists general duties but does not contain any business metrics. "
                "Recruiters and automated screens seek evidence of scale, performance improvement, or savings."
            ),
            where_it_appears=f"Work experience: {title_ev} at {comp_ev}",
            how_to_fix="Quantify achievements by answering: 'How much?', 'How many?', or 'By what percentage?'.",
            action_items=[
                f"Identify metrics in '{title_ev}' (e.g. latency reduction, users served, data size)",
                "Rewrite bullets starting with action verbs followed by a measurable metric"
            ],
            example_improvement=(
                "Before: Maintained backend API endpoints.\n"
                "After: Managed 12+ API microservices, reducing average response latency by 35%."
            )
        ))

    # 4. Unverified/Unvalidated Skills (Medium)
    unval = skill_validation.get('unvalidated_skills', [])
    if unval:
        unsupported_list = ', '.join(unval[:5])
        detected.append(IssueDetail(
            issue_title="Technical Skills Lack Supporting Context",
            severity_level="Medium",
            ats_impact="High",
            explanation=(
                f"The following listed skills lack supporting evidence or project details: {unsupported_list}. "
                "Recruiters flag unverified listings as keyword stuffing if they are not integrated into actual experience descriptions."
            ),
            where_it_appears=f"Unverified list: {unsupported_list}",
            how_to_fix="Integrate these technologies naturally inside your work experience bullets or project tech lists.",
            action_items=[f"Add context/mentions for '{s}' inside your project/work bullets" for s in unval[:3]],
            example_improvement=f"Project details: Built a platform using {unval[0]}, validating my core proficiency in production."
        ))

    # 5. Red Flag Gaps in Employment (Medium)
    # We report gaps if flagged in scorer
    if scores.get('red_flags'):
        gaps = [rf for rf in scores.get('red_flags', []) if "Employment Gaps" in rf or "Gaps" in rf]
        if gaps:
            detected.append(IssueDetail(
                issue_title="Employment Gap Flagged",
                severity_level="Medium",
                ats_impact="Medium",
                explanation="Work history contains consecutive duration gaps > 6 months. Recruiters look for continuous timeline threads.",
                where_it_appears="Experience timeline dates",
                how_to_fix="Add structured entries for freelance contracts, independent studies, or certifications during timeline gaps.",
                action_items=["Account for gaps by listing self-studies, freelancing, or professional certifications"],
                example_improvement="Jan 2024 - Present | Freelance Consulting / Certification Studies"
            ))

    # 7. Candidate-Specific Weaknesses (Medium/High)
    cand_weaknesses = parsed_resume.get('candidate_weaknesses') or []
    for idx, cw in enumerate(cand_weaknesses):
        detected.append(IssueDetail(
            issue_title=f"Hiring Concern: {cw[:55]}...",
            severity_level="Medium",
            ats_impact="Medium",
            explanation=cw,
            where_it_appears="Resume overall profile and credentials",
            how_to_fix="Address this concern to improve pre-screening pass rates.",
            action_items=[cw],
            example_improvement="Tailor experience descriptions to address this gap explicitly."
        ))

    # 8. Per-Project Detailed Evaluations (Medium)
    for p in proj_entries:
        title = p.get('title') or 'Unnamed Project'
        p_weakness = p.get('weakness') or p.get('weaknesses')
        p_strength = p.get('strength') or p.get('strengths')
        
        if p_weakness:
            detected.append(IssueDetail(
                issue_title=f"Project Critique: {title}",
                severity_level="Medium",
                ats_impact="Medium",
                explanation=f"Project '{title}' weakness: {p_weakness}. (Project strength: {p_strength or 'Valid implementation'})",
                where_it_appears=f"Project details: {title}",
                how_to_fix=f"Improve the '{title}' description: {p_weakness}",
                action_items=[f"Address '{p_weakness}' in project '{title}'"],
                example_improvement=f"Add unit testing, deployment context, or business metrics to '{title}'."
            ))

    # 6. Detailed Explanations for Score categories
    explainable = scores.get('explainable_cards', {})
    for cat_name, details in explainable.items():
        detected.append(IssueDetail(
            issue_title=f"Category explanation: {cat_name}",
            severity_level="Low",
            ats_impact="Traceability",
            explanation=(
                f"Score: {details.get('score')}/100. "
                f"Why: {details.get('reason')} "
                f"Evidence: {details.get('evidence')}"
            ),
            where_it_appears=f"Overall {cat_name} Card",
            how_to_fix=details.get('improvement', 'Optimize items.'),
            action_items=[details.get('improvement', 'Adjust details.')],
            example_improvement=f"Adjust parameters to optimize this score category."
        ))

    # Sort issues by severity: High -> Medium -> Low
    severity_rank = {"High": 1, "Medium": 2, "Low": 3}
    detected.sort(key=lambda x: severity_rank.get(x.severity_level, 4))
    return detected

def generate_issues_summary(detected_issues: List[IssueDetail]) -> List[str]:
    return [
        issue.issue_title 
        for issue in detected_issues 
        if not issue.issue_title.startswith("Category explanation:")
    ]

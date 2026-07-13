# what is specifically wrong in my resume?

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
        contact_info: Optional[Dict]=None, 
) -> List[IssueDetail]:
    
    detected: List[IssueDetail] = []

    exp_entries  = [e for e in parsed_resume.get('experience', []) if isinstance(e, dict)]
    edu_entries  = [e for e in parsed_resume.get('education',  []) if isinstance(e, dict)]
    proj_entries = [p for p in parsed_resume.get('projects',   []) if isinstance(p, dict)]
    summary      = (parsed_resume.get('professional_summary') or '').strip()

    resume_lower = resume_text.lower()

    # 1. Missing Projects Section (High)
    if not proj_entries and len(projects) == 0:
        detected.append(IssueDetail(
            issue_title="Missing Projects Section",
            severity_level="High",
            ats_impact="High",
            explanation=(
                "Your resume does not have a dedicated Projects section. "
                "Recruiters and ATS filters look for concrete projects to validate "
                "that your listed skills have been applied in practice, especially for tech roles."
            ),
            where_it_appears="Resume structure — no projects were parsed or detected",
            how_to_fix="Add a 'PROJECTS' section heading and detail 2-3 personal or academic projects.",
            action_items=[
                "Add a 'PROJECTS' header below your Experience section",
                "List 2–3 projects detailing the technologies used and what you built",
                "Use bullet points to describe project outcomes"
            ],
            example_improvement=(
                "PROJECTS\n"
                "• ResuMatch — Built an AI-powered resume analyzer using Python, FastAPI, and Streamlit.\n"
                "  Implemented phrase-level semantic matching, boosting parsing accuracy by 40%."
            )
        ))

    # 2. Incomplete Contact Details (High)
    if contact_info:
        missing_contacts = []
        if not contact_info.get('email'):
            missing_contacts.append('email address')
        if not contact_info.get('phone'):
            missing_contacts.append('phone number')
        if not contact_info.get('linkedin'):
            missing_contacts.append('LinkedIn profile')

        if missing_contacts:
            detected.append(IssueDetail(
                issue_title="Incomplete Contact Information",
                severity_level="High",
                ats_impact="High",
                explanation=(
                    f"Your contact header is missing: {', '.join(missing_contacts)}. "
                    "ATS systems and hiring managers require direct contact options to proceed "
                    "with scheduling interviews."
                ),
                where_it_appears="Top header section of the resume",
                how_to_fix=f"Include your {' and '.join(missing_contacts)} clearly in the contact header.",
                action_items=[f"Add your {item} at the top of the page" for item in missing_contacts],
                example_improvement=(
                    f"{parsed_resume.get('name') or 'John Doe'}\n"
                    f"{'email@address.com' if 'email address' in missing_contacts else contact_info.get('email')} | "
                    f"{'+91 99034 27270' if 'phone number' in missing_contacts else contact_info.get('phone')} | "
                    f"{'linkedin.com/in/username' if 'LinkedIn profile' in missing_contacts else contact_info.get('linkedin')}"
                )
            ))

    # 3. No Quantifiable Achievements (Medium)
    number_patterns = [
        r'\d+%',
        r'\$\d+',
        r'\d+[kKmMbB]',
        r'\d+\s*(?:users|customers|clients|projects|hours|days|months|years)',
        r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+',
    ]
    achievement_count = sum(len(re.findall(p, resume_text, re.IGNORECASE)) for p in number_patterns)
    if achievement_count == 0 and exp_entries:
        title_ev = exp_entries[0].get('job_title') or "your professional roles"
        comp_ev = exp_entries[0].get('company') or "your companies"
        detected.append(IssueDetail(
            issue_title="No Quantifiable Achievements Found",
            severity_level="Medium",
            ats_impact="Medium",
            explanation=(
                f"Your experience descriptions (such as your role as '{title_ev}' at '{comp_ev}') "
                "do not contain any numerical metrics, percentages, or dollar values. "
                "ATS systems and recruiters heavily favor bullet points that prove impact using metrics."
            ),
            where_it_appears="Experience section — bullet point descriptions",
            how_to_fix="Add metrics to at least 50% of your experience bullets, detailing scale, users, or performance improvements.",
            action_items=[
                f"Review bullets for '{title_ev}' and ask: 'How much?', 'How many?', 'By what %?'",
                "Add metrics like: load time reduced by X%, API requests handled, or team size led",
                "Estimate numbers reasonably if exact metrics are unavailable (e.g. 'serving ~500 users')"
            ],
            example_improvement=(
                "Before:\n"
                "• Managed a crowdfunding platform UI and integrated backend services.\n\n"
                "After:\n"
                "• Developed 12+ responsive UI components with React, serving 500+ active users.\n"
                "• Optimized REST APIs, reducing page latency by 35%."
            )
        ))

    # 4. Skills Lack Evidence (Medium/Low)
    unvalidated = skill_validation.get('unvalidated_skills', [])
    validated   = skill_validation.get('validated_skills', [])
    total_skills = len(unvalidated) + len(validated)

    if total_skills > 0 and len(unvalidated) > 0:
        unsupported_list = ', '.join(unvalidated[:5])
        pct_unsupported = round((len(unvalidated) / total_skills) * 100)
        action_items_skills = [
            f"Add context or mention '{skill}' in a project description or experience bullet" 
            for skill in unvalidated[:4]
        ]
        if len(unvalidated) > 4:
            action_items_skills.append(f"Review the remaining {len(unvalidated) - 4} unvalidated skills")

        detected.append(IssueDetail(
            issue_title="Skills Lack Supporting Evidence",
            severity_level="Medium",
            ats_impact="High",
            explanation=(
                f"{pct_unsupported}% of your technical skills ({len(unvalidated)} out of {total_skills}) "
                "are listed in your Skills section but do not appear in any of your experience or project descriptions. "
                "Recruiters cross-reference skills against actual work to check credibility."
            ),
            where_it_appears=f"Unvalidated skills: {unsupported_list}",
            how_to_fix="Integrate your technical skills naturally into your project and job descriptions.",
            action_items=action_items_skills,
            example_improvement=(
                f"Your skill '{unvalidated[0]}' has no supporting project context.\n\n"
                f"Fix: Add to a project bullet:\n"
                f"• Integrated '{unvalidated[0]}' database services to handle user authentication, securing 500+ accounts."
            )
        ))

    # 5. Weak Action Verbs (Low)
    if action_verbs and len(action_verbs) < 5:
        detected.append(IssueDetail(
            issue_title="Inconsistent Use of Action Verbs",
            severity_level="Low",
            ats_impact="Medium",
            explanation=(
                f"Only {len(action_verbs)} action verbs (e.g. {', '.join(action_verbs)}) were detected in your bullet points. "
                "ATS systems look for strong, action-oriented openings for each bullet point."
            ),
            where_it_appears="Experience and Projects sections",
            how_to_fix="Ensure every bullet point begins with a strong past-tense action verb.",
            action_items=[
                "Rewrite bullets starting with passive language like 'Responsible for' or 'Helped with'",
                "Use strong verbs: Developed, Optimized, Integrated, Automated, Maintained"
            ],
            example_improvement=(
                "Before: Responsible for maintaining Git repositories.\n"
                "After: Managed Git version control workflow, coordinating branch merges for a team of 4."
            )
        ))

    # Sort issues by severity: High -> Medium -> Low
    severity_rank = {"High": 1, "Medium": 2, "Low": 3}
    detected.sort(key=lambda x: severity_rank.get(x.severity_level, 4))

    # 6. Score Breakdown Card (Append at the end)
    fs = scores.get('formatting_score', 0)
    ks = scores.get('keywords_score', 0)
    cs = scores.get('content_score', 0)
    sv = scores.get('skill_validation_score', 0)
    ac = scores.get('ats_compatibility_score', 0)
    os_score = scores.get('overall_score', 0)

    breakdown_text = (
        f"Formatting: {fs}/20  |  Keywords: {ks}/25  |  Content: {cs}/25  |  "
        f"Skill Validation: {sv}/15  |  ATS Compatibility: {ac}/15"
    )

    detected.append(IssueDetail(
        issue_title="ATS Score Breakdown & Explanation",
        severity_level="Low",
        ats_impact="Traceability",
        explanation=(
            f"Your overall ATS score is {os_score}/100. Below is the step-by-step breakdown "
            "of how your score was calculated across the five key evaluation categories."
        ),
        where_it_appears=breakdown_text,
        how_to_fix="Focus on improving the high-priority issues above to boost your score.",
        action_items=[
            f"Formatting ({fs}/20): Points awarded for section presence (Exp, Edu, Skills, Projects) and bullet structure.",
            f"Keywords ({ks}/25): Based on number of technical terms ({len(skills)} skills detected).",
            f"Content ({cs}/25): Earned for action verb count ({len(action_verbs)}) and metric presence.",
            f"Skill Validation ({sv}/15): Proportional to skills validated ({len(validated)}/{total_skills} skills, {skill_validation.get('validation_percentage', 0)*100:.1f}%).",
            f"ATS Compatibility ({ac}/15): Base score minus location privacy or special character layout penalties."
        ],
        example_improvement=(
            "Mathematical Aggregation:\n"
            f"1. Formatting Pct: {fs/20*100:.1f}%\n"
            f"2. Keywords Pct: {ks/25*100:.1f}%\n"
            f"3. Content Pct: {cs/25*100:.1f}%\n"
            f"4. Skill Validation Pct: {sv/15*100:.1f}%\n"
            f"5. ATS Compatibility Pct: {ac/15*100:.1f}%\n\n"
            f"Overall weighted aggregate base score: {os_score:.1f}/100"
        )
    ))

    return detected

def generate_issues_summary(detected_issues: List[IssueDetail]) -> List[str]:
    """Extract issue titles to formulate the issues_summary list."""
    return [issue.issue_title for issue in detected_issues if issue.issue_title != "ATS Score Breakdown & Explanation"]

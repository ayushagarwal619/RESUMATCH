import re
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger('ats_resume_scorer')

# ── Role-Specific Rubrics Configurations ──
ROLE_RUBRICS = {
    "Software Engineer": {
        "weights": {"formatting": 0.15, "completeness": 0.15, "skills": 0.20, "projects": 0.25, "experience": 0.25},
        "critical_skills": ["git", "github", "testing", "agile", "rest api", "docker", "ci/cd"]
    },
    "Backend Developer": {
        "weights": {"formatting": 0.10, "completeness": 0.15, "skills": 0.25, "projects": 0.25, "experience": 0.25},
        "critical_skills": ["python", "java", "node.js", "databases", "sql", "apis", "rest", "backend"]
    },
    "Frontend Developer": {
        "weights": {"formatting": 0.15, "completeness": 0.15, "skills": 0.20, "projects": 0.30, "experience": 0.20},
        "critical_skills": ["react", "javascript", "typescript", "html", "css", "vue", "angular", "responsive"]
    },
    "Full Stack Developer": {
        "weights": {"formatting": 0.10, "completeness": 0.10, "skills": 0.25, "projects": 0.30, "experience": 0.25},
        "critical_skills": ["frontend", "backend", "react", "node.js", "databases", "sql", "apis"]
    },
    "AI/ML Engineer": {
        "weights": {"formatting": 0.10, "completeness": 0.10, "skills": 0.30, "projects": 0.30, "experience": 0.20},
        "critical_skills": ["python", "pytorch", "tensorflow", "ai", "ml", "machine learning", "deep learning", "nlp", "llm"]
    },
    "Data Scientist": {
        "weights": {"formatting": 0.10, "completeness": 0.10, "skills": 0.30, "projects": 0.25, "experience": 0.25},
        "critical_skills": ["python", "sql", "pandas", "data science", "statistics", "machine learning", "r"]
    },
    "DevOps Engineer": {
        "weights": {"formatting": 0.10, "completeness": 0.10, "skills": 0.25, "projects": 0.25, "experience": 0.30},
        "critical_skills": ["aws", "docker", "kubernetes", "ci/cd", "jenkins", "terraform", "bash", "linux"]
    },
    "Cybersecurity": {
        "weights": {"formatting": 0.10, "completeness": 0.15, "skills": 0.25, "projects": 0.25, "experience": 0.25},
        "critical_skills": ["security", "penetration testing", "networking", "firewalls", "cryptography", "owasp", "linux"]
    },
    "Mobile Developer": {
        "weights": {"formatting": 0.15, "completeness": 0.15, "skills": 0.20, "projects": 0.30, "experience": 0.20},
        "critical_skills": ["flutter", "react native", "swift", "kotlin", "ios", "android", "mobile apis"]
    },
    "Product/Business roles": {
        "weights": {"formatting": 0.15, "completeness": 0.20, "skills": 0.15, "projects": 0.20, "experience": 0.30},
        "critical_skills": ["product management", "agile", "scrum", "analytics", "kpis", "sql", "jira", "strategy"]
    }
}

CERTIFICATE_PROVIDERS = [
    "aws", "azure", "gcp", "google", "oracle", "cisco", "red hat", "meta", "ibm", 
    "nvidia", "mongodb", "microsoft", "coursera", "nptel", "kubernetes", "scrum"
]

OUTDATED_TECHNOLOGIES = [
    "cobol", "fortran", "pascal", "silverlight", "flash", "actionscript"
]

def _find_skill_evidence(skill: str, text: str) -> bool:
    skill_clean = skill.strip().lower()
    text_lower = text.lower()
    if not skill_clean or not text_lower:
        return False
        
    if skill_clean in ("react.js", "reactjs"):
        skill_clean = "react"
    if skill_clean in ("node.js", "nodejs"):
        skill_clean = "node"
        
    if len(skill_clean) <= 2:
        pattern = rf'\b{re.escape(skill_clean)}\b'
        match = re.search(pattern, text_lower)
        if match:
            end = match.end()
            if skill_clean == "c" and end < len(text_lower) and text_lower[end] in ('+', '#'):
                return False
            return True
        return False
    else:
        pattern = rf'\b{re.escape(skill_clean)}\b'
        if re.search(pattern, text_lower):
            return True
        if skill_clean in text_lower:
            return True
    return False

def validate_skills_with_projects(
    skills: List[str],
    projects: List[Dict],
    experience_entries: List[Dict],
    embedder: Optional[SentenceTransformer] = None,
    threshold: float = 0.65
) -> Dict:
    validated_skills = []
    unvalidated_skills = []
    skill_project_mapping = {}

    for skill in skills:
        sources = []
        
        # Check in projects
        for proj in projects:
            title = proj.get('title') or ''
            desc = proj.get('description') or ''
            techs = " ".join(proj.get('technologies_used') or [])
            combined_proj = f"{title} {desc} {techs}"
            if _find_skill_evidence(skill, combined_proj):
                sources.append(f"Project: {title or 'Unnamed'}")

        # Check in experiences
        for exp in experience_entries:
            title = exp.get('job_title') or ''
            company = exp.get('company') or ''
            desc = exp.get('description') or ''
            techs = " ".join(exp.get('technologies_used') or [])
            combined_exp = f"{title} {company} {desc} {techs}"
            if _find_skill_evidence(skill, combined_exp):
                sources.append(f"Experience: {title} at {company}")

        if sources:
            # Determine proficiency based on number of evidence sources
            if len(sources) >= 3:
                proficiency = "Advanced"
                confidence = 0.95
            elif len(sources) == 2:
                proficiency = "Intermediate"
                confidence = 0.85
            else:
                proficiency = "Beginner"
                confidence = 0.70
                
            validated_skills.append({
                'skill': skill,
                'projects': sources,
                'proficiency': proficiency,
                'confidence': confidence
            })
            skill_project_mapping[skill] = sources
        else:
            unvalidated_skills.append(skill)
            skill_project_mapping[skill] = []

    total_skills = len(skills)
    validation_percentage = len(validated_skills) / total_skills if total_skills > 0 else 0.0

    return {
        'validated_skills': validated_skills,
        'unvalidated_skills': unvalidated_skills,
        'validation_percentage': validation_percentage,
        'skill_project_mapping': skill_project_mapping,
        'validation_score': validation_percentage * 100.0,
    }

def calculate_overall_score(
    text: str,
    parsed_resume: Dict,
    skills: List[str],
    keywords: List[str],
    action_verbs: List[str],
    skill_validation_results: Dict,
    grammar_results: Dict,
    location_results: Dict,
    jd_keywords: Optional[List[str]] = None,
    experience_months: int = 0,
) -> Dict[str, Any]:
    
    role = parsed_resume.get('detected_role', 'Software Engineer')
    if role not in ROLE_RUBRICS:
        role = 'Software Engineer'
    rubric = ROLE_RUBRICS[role]
    weights = rubric["weights"]

    # 1. Formatting Score (0 - 100)
    # Checks for presence of bullet formats and headers
    formatting_score = 0.0
    formatting_reasons = []
    
    bullet_count = sum(1 for line in text.split('\n') if re.match(r'^\s*[•\-\*\◦]', line) or re.match(r'^\s*\d+\.', line))
    if bullet_count >= 15:
        formatting_score += 40
        formatting_reasons.append(f"Strong structural layout with {bullet_count} clean bullet points.")
    elif bullet_count >= 5:
        formatting_score += 25
        formatting_reasons.append(f"Moderate bullet usage ({bullet_count} bullets). Add more lists to separate experiences.")
    else:
        formatting_reasons.append("Very low bullet layout usage. Use bullet points instead of paragraphs for readability.")

    # Section counts
    sections_found = []
    if parsed_resume.get('experience'): sections_found.append("Experience")
    if parsed_resume.get('education'): sections_found.append("Education")
    if parsed_resume.get('skills', {}).get('technical_skills'): sections_found.append("Skills")
    if parsed_resume.get('projects'): sections_found.append("Projects")
    
    sec_pts = len(sections_found) * 15
    formatting_score += sec_pts
    formatting_reasons.append(f"Found {len(sections_found)} key sections: {', '.join(sections_found)}.")

    # Contact indicators
    contact = parsed_resume.get('personal_info', {})
    if contact.get('email') and contact.get('phone'):
        formatting_score += 20
        formatting_reasons.append("Contact header contains both email and phone details.")
    else:
        formatting_score += 10
        formatting_reasons.append("Email or phone is missing from the header.")

    formatting_score = min(100.0, max(0.0, formatting_score))

    # 2. Completeness Score (0 - 100)
    completeness_score = 0.0
    completeness_reasons = []
    missing_sections = []
    
    # 11 points evaluation list
    completeness_matrix = [
        ('name', bool(contact.get('name'))),
        ('email', bool(contact.get('email'))),
        ('phone', bool(contact.get('phone'))),
        ('linkedin', bool(contact.get('linkedin'))),
        ('github', bool(contact.get('github'))),
        ('portfolio', bool(contact.get('portfolio'))),
        ('summary', bool(parsed_resume.get('summary'))),
        ('technical_skills', bool(parsed_resume.get('skills', {}).get('technical_skills'))),
        ('projects', bool(parsed_resume.get('projects'))),
        ('experience', bool(parsed_resume.get('experience'))),
        ('education', bool(parsed_resume.get('education')))
    ]
    
    present_count = sum(1 for k, present in completeness_matrix if present)
    for k, present in completeness_matrix:
        if not present:
            missing_sections.append(k.replace('_', ' ').title())
            
    completeness_score = (present_count / 11) * 100.0
    completeness_reasons.append(f"Resume completeness is at {completeness_score:.0f}% with {present_count} out of 11 items present.")
    if missing_sections:
        completeness_reasons.append(f"Missing items: {', '.join(missing_sections)}.")

    # 3. Technical Skills Score (0 - 100)
    skills_score = 0.0
    skills_reasons = []
    tech_skills = parsed_resume.get('skills', {}).get('technical_skills', [])
    
    if len(tech_skills) >= 15:
        skills_score += 60
        skills_reasons.append(f"Broad technical skill set with {len(tech_skills)} skills listed.")
    elif len(tech_skills) >= 5:
        skills_score += 45
        skills_reasons.append(f"Found {len(tech_skills)} technical skills.")
    else:
        skills_score += 20
        skills_reasons.append("Very short skills listing. Expand your skills section.")

    # Critical skill matches
    critical_matches = []
    for cs in rubric["critical_skills"]:
        if any(cs in ts.lower() for ts in tech_skills):
            critical_matches.append(cs)
            
    if critical_matches:
        skills_score += min(40, len(critical_matches) * 10)
        skills_reasons.append(f"Matched role-specific critical skills: {', '.join(critical_matches)}.")
    else:
        skills_reasons.append(f"No critical skills for {role} found in your technical skills.")

    skills_score = min(100.0, max(0.0, skills_score))

    # 4. Projects Quality Score (0 - 100)
    projects_score = 0.0
    projects_reasons = []
    projects_list = parsed_resume.get('projects', [])
    
    if projects_list:
        project_scores = []
        for p in projects_list:
            p_score = 0
            # 1. Complexity
            complexity = p.get('complexity', 'Beginner')
            if complexity == "Advanced": p_score += 25
            elif complexity == "Intermediate": p_score += 18
            else: p_score += 10
            # 2. Impact
            if len(p.get('business_impact') or '') > 20: p_score += 20
            
            # 3. Diversity
            techs_count = len(p.get('technologies_used') or [])
            if techs_count >= 5: p_score += 20
            elif techs_count >= 3: p_score += 15
            else: p_score += 10
            
            # 4. Production readiness flags
            readiness = 0
            if p.get('has_deployment'): readiness += 12
            if p.get('has_testing'): readiness += 6
            if p.get('has_cicd'): readiness += 7
            p_score += readiness
            
            # 5. Innovation (AI/ML or Cloud)
            if p.get('has_aiml') or p.get('has_cloud'):
                p_score += 10
                
            project_scores.append(p_score)
            
        avg_p_score = sum(project_scores) / len(project_scores)
        projects_score = avg_p_score
        projects_reasons.append(f"Analyzed {len(projects_list)} projects with average rating of {avg_p_score:.0f}%.")
    else:
        projects_reasons.append("No projects found in the resume.")

    projects_score = min(100.0, max(0.0, projects_score))

    # 5. Work Experience Score (0 - 100)
    experience_score = 0.0
    experience_reasons = []
    experience_list = parsed_resume.get('experience', [])
    
    # Months of experience mapping
    if experience_months >= 60:
        experience_score += 50
        experience_reasons.append(f"Senior level experience detected: {experience_months/12:.1f} years.")
    elif experience_months >= 24:
        experience_score += 40
        experience_reasons.append(f"Mid-level experience detected: {experience_months/12:.1f} years.")
    elif experience_months > 0:
        experience_score += 25
        experience_reasons.append(f"Junior level experience: {experience_months/12:.1f} years.")
    else:
        experience_reasons.append("No work experience duration resolved.")

    # Quantified achievements in experience
    metric_count = 0
    number_patterns = [r'\d+%', r'\$\d+', r'\d+[kKmMbB]', r'(?:increased|decreased|improved|reduced|grew|saved)\s+(?:by\s+)?\d+']
    for exp in experience_list:
        desc = exp.get('description', '')
        for pat in number_patterns:
            metric_count += len(re.findall(pat, desc))
            
    if metric_count >= 5:
        experience_score += 30
        experience_reasons.append(f"Excellent evidence-based metrics ({metric_count} quantitative indicators found).")
    elif metric_count >= 1:
        experience_score += 15
        experience_reasons.append(f"Found {metric_count} measurable achievements in job descriptions.")
    else:
        experience_reasons.append("No measurable metrics or business outcomes in experiences.")

    # Leadership verb checks
    lead_verbs = ['led', 'managed', 'supervised', 'directed', 'coordinated', 'architected']
    lead_count = sum(1 for exp in experience_list if any(verb in exp.get('description', '').lower() for verb in lead_verbs))
    if lead_count > 0:
        experience_score += 20
        experience_reasons.append("Leadership and ownership verbs detected in experience entries.")

    experience_score = min(100.0, max(0.0, experience_score))

    # 6. Certifications Score (0 - 100)
    certs_score = 0.0
    certs_reasons = []
    certs_list = parsed_resume.get('certifications', [])
    
    if certs_list:
        found_providers = []
        for cert in certs_list:
            c_name = cert.get('name', '').lower()
            c_prov = cert.get('provider', '').lower()
            for provider in CERTIFICATE_PROVIDERS:
                if provider in c_name or provider in c_prov:
                    found_providers.append(provider.upper())
                    
        if found_providers:
            certs_score = min(100.0, 50.0 + len(set(found_providers)) * 25.0)
            certs_reasons.append(f"Holds industry credentials from: {', '.join(set(found_providers))}.")
        else:
            certs_score = 40.0
            certs_reasons.append("Found certifications from general provider networks.")
    else:
        certs_reasons.append("No professional certifications listed.")

    # ── CALCULATE RESUME QUALITY SCORE (Presentation, Experience & Projects) ──
    # Weighted average: Formatting (20%), Completeness (20%), Experience (30%), Projects (30%)
    qual_score = (formatting_score * 0.20) + (completeness_score * 0.20) + (experience_score * 0.30) + (projects_score * 0.30)
    resume_quality_score = min(100.0, max(0.0, qual_score))

    # ── CALCULATE ATS COMPATIBILITY SCORE (Structural details, no blockers) ──
    ats_score_val = 100.0
    ats_reasons = []
    
    # Blocker check
    special_chars = len(re.findall(r'[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]', text))
    if special_chars > 15:
        ats_score_val -= 20
        ats_reasons.append(f"Deducted 20 pts: High special character count ({special_chars}). Avoid layout columns.")
    else:
        ats_reasons.append("No layout columns or blocking characters detected.")

    # Location privacy
    privacy_risk = location_results.get('privacy_risk', 'none')
    if privacy_risk == 'high':
        ats_score_val -= 15
        ats_reasons.append("Deducted 15 pts: Direct street address or zip code leaks privacy.")
    else:
        ats_reasons.append("Location privacy is safe (City, State layout).")

    # Layout completeness
    if not parsed_resume.get('experience') or not parsed_resume.get('education'):
        ats_score_val -= 25
        ats_reasons.append("Deducted 25 pts: Missing core Experience or Education section.")
        
    ats_compatibility_score = min(100.0, max(0.0, ats_score_val))

    # ── CALCULATE JOB MATCH SCORE (only when JD provided) ──
    job_match_score = None
    job_reasons = []
    
    if jd_keywords:
        match_score_val = 0.0
        all_resume_skills = [s.lower() for s in tech_skills]
        
        # Skill alignment
        matched_jd_skills = [k for k in jd_keywords if any(k.lower() in rs for rs in all_resume_skills)]
        match_pct = len(matched_jd_skills) / len(jd_keywords) if jd_keywords else 0.0
        match_score_val += (match_pct * 60.0)
        job_reasons.append(f"Matched {len(matched_jd_skills)} / {len(jd_keywords)} job description keywords ({match_pct*100:.0f}%).")
        
        # Role match
        if any(rubric["critical_skills"]):
            role_matches = sum(1 for cs in rubric["critical_skills"] if any(cs in rs for rs in all_resume_skills))
            role_pct = role_matches / len(rubric["critical_skills"])
            match_score_val += (role_pct * 40.0)
            job_reasons.append(f"Alignment with target role '{role}' is {role_pct*100:.0f}%.")
            
        job_match_score = min(100.0, max(0.0, match_score_val))

    # Composite overall score for backward compatibility
    if job_match_score is not None:
        overall = (resume_quality_score + ats_compatibility_score + job_match_score) / 3.0
    else:
        overall = (resume_quality_score + ats_compatibility_score) / 2.0

    # ── Recruiter Red Flags ──
    red_flags = []
    
    # 1. Unverified skills
    unval = skill_validation_results.get('unvalidated_skills', [])
    if len(unval) > 3:
        red_flags.append(f"Unverified Skills: {len(unval)} skills listed in the technical list lack evidence in work/projects.")
        
    # 2. Keyword stuffing
    if len(tech_skills) > 25 and len(text) < 1600:
        red_flags.append("Keyword Stuffing: High technical skill density compared to descriptive text.")
        
    # 3. Missing Links
    no_links = True
    for proj in projects_list:
        desc_p = proj.get('description', '')
        if "github" in desc_p.lower() or "http" in desc_p.lower():
            no_links = False
    if no_links and projects_list:
        red_flags.append("Missing Links: Projects lack URLs or GitHub repository links.")
        
    # 4. Outdated Tech
    outdated_found = []
    for ts in tech_skills:
        for ot in OUTDATED_TECHNOLOGIES:
            if ot in ts.lower():
                outdated_found.append(ts)
    if outdated_found:
        red_flags.append(f"Outdated Technologies: Resume lists older frameworks/tools: {', '.join(outdated_found)}.")

    # ── Recruiter Insights ──
    strengths = parsed_resume.get("candidate_strengths") or []
    if not strengths:
        if formatting_score >= 80: strengths.append("Formatting: Structured hierarchy with consistent list bullet items.")
        if len(tech_skills) >= 10: strengths.append(f"Skills diversity: Broad coverage of {len(tech_skills)} development tools.")
        if len(projects_list) >= 2: strengths.append(f"Applied portfolio: Candidate showcases {len(projects_list)} active projects.")
        if experience_months >= 24: strengths.append(f"Commercial exposure: {experience_months/12:.1f} years of professional field experience.")
        if metric_count >= 3: strengths.append(f"Quantified achievements: {metric_count} business outcomes backed by metrics.")
    
    if not strengths:
        strengths.append("Structured resume sections (Education, Experience, Skills) present.")
    
    concerns = parsed_resume.get("candidate_weaknesses") or []
    if not concerns:
        if not projects_list: concerns.append("Hiring Concern: Lacks projects showing hands-on implementation.")
        if len(unval) > 4: concerns.append(f"Hiring Concern: {len(unval)} listed skills lack project context.")
        if metric_count == 0: concerns.append("Hiring Concern: Experience bullets lack quantitative business metrics.")
        if not contact.get('linkedin') and not contact.get('github'): concerns.append("Hiring Concern: No LinkedIn or GitHub links provided.")
        if Outdated_found := outdated_found: concerns.append("Hiring Concern: Presence of legacy tech dependencies.")
    
    if not concerns:
        concerns.append("No critical concerns identified. Optimize keywords alignment.")

    # Employability and Readiness (independent of formatting)
    parsed_insights = parsed_resume.get("recruiter_insights") or {}
    recommendation = parsed_insights.get("overall_recommendation") or ""
    readiness = parsed_insights.get("interview_readiness") or ""

    if not recommendation or not readiness:
        tech_depth_score = (len(tech_skills) * 4) + (len(projects_list) * 10) + (experience_months * 0.5)
        if tech_depth_score >= 80:
            recommendation = "Strong Hire"
            readiness = "Advanced. Demonstrates technical depth, multiple projects, and commercial field experience."
        elif tech_depth_score >= 50:
            recommendation = "Hire"
            readiness = "Competent. Candidate has core development experience and portfolio projects."
        elif tech_depth_score >= 25:
            recommendation = "Borderline"
            readiness = "Entry-level. Candidate has skills but lacks work experience or project validations."
        else:
            recommendation = "No Hire"
            readiness = "Incomplete. Missing project context, skills are unverified, and work experience is lacking."

    # Explainable score cards
    explainable_cards = {
        "Resume Quality": {
            "score": round(resume_quality_score, 1),
            "evidence": f"Found {present_count}/11 completeness items. Job experience duration resolved: {experience_months/12:.1f} years.",
            "reason": " ".join(formatting_reasons + completeness_reasons),
            "improvement": "Add a summary, portfolio link, or certifications to hit 100% completeness. Quantify experience bullets."
        },
        "ATS Compatibility": {
            "score": round(ats_compatibility_score, 1),
            "evidence": f"Special chars: {special_chars}. Privacy risk level: {privacy_risk}.",
            "reason": " ".join(ats_reasons),
            "improvement": "Remove full home address details. Keep layout single-column with simple headers."
        }
    }
    if job_match_score is not None:
        explainable_cards["Job Match"] = {
            "score": round(job_match_score, 1),
            "evidence": f"Matched JD keywords: {len(matched_jd_skills)}/{len(jd_keywords)}.",
            "reason": " ".join(job_reasons),
            "improvement": "Tailor your experience bullets to explicitly match missing keywords from the job description."
        }

    # Backward compatibility component scores mapping (max values: 20, 25, 25, 15, 15)
    return {
        'overall_score': round(overall, 1),
        'ats_score': round(overall, 1),
        'resume_quality_score': round(resume_quality_score, 1),
        'ats_compatibility_score': round(ats_compatibility_score, 1),
        'job_match_score': round(job_match_score, 1) if job_match_score is not None else None,
        
        # Backward compatibility maps
        'formatting_score': round((formatting_score / 100.0) * 20.0, 1),
        'keywords_score': round((skills_score / 100.0) * 25.0, 1),
        'content_score': round((experience_score / 100.0) * 25.0, 1),
        'skill_validation_score': round((skill_validation_results.get('validation_score', 0) / 100.0) * 15.0, 1),
        'ats_compatibility_score_raw': round((ats_compatibility_score / 100.0) * 15.0, 1),
        
        'overall_interpretation': f"Role detected: {role}. {readiness}",
        'penalties': {},
        'bonuses': {},
        'explainable_cards': explainable_cards,
        'recruiter_insights': {
            'strengths': strengths,
            'hiring_concerns': concerns,
            'interview_readiness': readiness,
            'overall_recommendation': recommendation
        },
        'red_flags': red_flags,
        'resume_completeness_pct': round(completeness_score, 1),
        'completeness_percentage': round(completeness_score, 1)
    }

def generate_strengths(*args, **kwargs) -> List[str]:
    # Backward compatibility fallback
    return []

def generate_critical_issues(*args, **kwargs) -> List[str]:
    # Backward compatibility fallback
    return []

def generate_improvements(*args, **kwargs) -> List[str]:
    # Backward compatibility fallback
    return []
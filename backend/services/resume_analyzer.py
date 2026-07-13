import spacy
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional
from backend.models.schemas import IssueDetail
from backend.services.groq_parser import parse_resume, parse_job_description
from backend.services.jd_matcher import compare_resume_with_jd
from backend.services.feedback_engine import analyze_issues, generate_issues_summary
from backend.services.ats_scorer import calculate_overall_score, validate_skills_with_projects


def analyze_full_resume(
    resume_text: str,
    nlp: spacy.Language,
    embedder: SentenceTransformer,
    job_description: Optional[str] = None,
) -> Dict:
    import logging
    logger = logging.getLogger('ats_resume_scorer')
    parsed_resume = parse_resume(resume_text)
    logger.info(f"Groq parsed summary: {parsed_resume.get('professional_summary', '')[:100]!r}")
    logger.info(f"Groq parsed skills count: {len(parsed_resume.get('skills', []))}")
    logger.info(f"Groq parsed experience count: {len(parsed_resume.get('experience', []))}")

    skills          = parsed_resume.get('skills', [])
    projects        = parsed_resume.get('projects', [])
    keywords        = parsed_resume.get('keywords', [])
    action_verbs    = parsed_resume.get('action_verbs', [])

    experience_months = sum(
        int(e.get('duration_months', 0))
        for e in parsed_resume.get('experience', [])
        if isinstance(e, dict)
    )

    contact_info = {
        'email':     parsed_resume.get('email'),
        'phone':     parsed_resume.get('phone'),
        'linkedin':  parsed_resume.get('linkedin'),
        'github':    parsed_resume.get('github'),
        'portfolio': None,
    }
    skill_validation = validate_skills_with_projects(
        skills=skills,
        projects=projects,
        experience_entries=parsed_resume.get('experience', []),
        embedder=embedder,
    )

    jd_comparison_result = None
    jd_keywords = None
    if job_description and job_description.strip():
        parsed_jd = parse_job_description(job_description.strip())
        jd_keywords = list(set(
            parsed_jd.get('keywords', []) +
            parsed_jd.get('required_skills', []) +
            parsed_jd.get('preferred_skills', [])
        ))
        jd_comparison_result = compare_resume_with_jd(
            resume_text=resume_text,
            resume_keywords=keywords,
            resume_skills=skills,
            jd_text=job_description.strip(),
            jd_keywords=jd_keywords,
            embedder=embedder,
            nlp=nlp,
        )

    from backend.utils.file_utils import (
        get_default_grammar_results, get_default_location_results,
    )
    grammar_results  = get_default_grammar_results()
    location_results = get_default_location_results()

    scores = calculate_overall_score(
        text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        keywords=keywords,
        action_verbs=action_verbs,
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        jd_keywords=jd_keywords,
        experience_months=experience_months,
    )
    detailed_feedback = analyze_issues(
        resume_text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        projects=projects,
        action_verbs=action_verbs,
        skill_validation=skill_validation,
        scores=scores,
        contact_info=contact_info,
    )

    issues_summary = generate_issues_summary(detailed_feedback)

    validated_raw   = skill_validation.get('validated_skills', [])
    unvalidated_raw = skill_validation.get('unvalidated_skills', [])
    total_skills    = len(validated_raw) + len(unvalidated_raw)
    val_pct         = round((len(validated_raw) / total_skills * 100) if total_skills > 0 else 0, 1)

    skill_validation_details = {
        "validated": [
            {
                "skill":    item['skill'],
                "projects": item.get('projects', []),
            }
            for item in validated_raw
        ],
        "unvalidated":     unvalidated_raw,
        "total":           total_skills,
        "validated_count": len(validated_raw),
        "validation_pct":  val_pct,
    }

    return {
        "ATS_score":          scores['overall_score'],
        "ats_score":          scores['overall_score'],
        "component_scores": {
            "formatting":       scores['formatting_score'],
            "keywords":         scores['keywords_score'],
            "content":          scores['content_score'],
            "skill_validation": scores['skill_validation_score'],
            "ats_compatibility": scores['ats_compatibility_score'],
        },
        "issues_summary":    issues_summary,
        "detailed_feedback": detailed_feedback,
        "jd_match_analysis": jd_comparison_result,
        "jd_comparison":     jd_comparison_result,
        "skills":            skills,
        "matched_keywords":  (
            jd_comparison_result['matched_keywords']
            if jd_comparison_result else list(keywords[:20])
        ),
        "missing_keywords":  (
            jd_comparison_result['missing_keywords']
            if jd_comparison_result else []
        ),
        "strengths": _generate_strengths(parsed_resume, skills, projects, action_verbs, skill_validation, scores),
        "interpretation":    scores.get('overall_interpretation', ''),
        "skill_validation_details": skill_validation_details,
        "experience_months": experience_months,
    }


def _generate_strengths(
    parsed_resume: Dict, skills: List, projects: List,
    action_verbs: List, skill_validation: Dict, scores: Dict,
) -> List[str]:
    """Generate a list of things the resume does well, based on actual structured data."""
    strengths = []

    # 1. Experience
    exp_entries = parsed_resume.get('experience', [])
    if exp_entries:
        companies = [e.get('company') for e in exp_entries if e.get('company')]
        titles = [e.get('job_title') for e in exp_entries if e.get('job_title')]
        if companies and titles:
            strengths.append(f"Professional work experience as {titles[0]} at {companies[0]}")
        else:
            strengths.append("Structured professional work history section is present")

    # 2. Projects
    proj_entries = parsed_resume.get('projects', []) or projects
    if proj_entries:
        titles = []
        for p in proj_entries:
            if isinstance(p, dict) and p.get('title'):
                titles.append(p.get('title'))
            elif isinstance(p, str):
                titles.append(p)
        if len(titles) >= 2:
            strengths.append(f"Strong project portfolio with {len(proj_entries)} projects, including {titles[0]} and {titles[1]}")
        elif len(titles) == 1:
            strengths.append(f"Project portfolio featuring {titles[0]}")
        else:
            strengths.append("Includes a dedicated Projects section showcasing applied skills")

    # 3. Education
    edu_entries = parsed_resume.get('education', [])
    if edu_entries:
        degrees = [e.get('degree') for e in edu_entries if e.get('degree')]
        insts = [e.get('institution') for e in edu_entries if e.get('institution')]
        if degrees and insts:
            # Clean up casing
            deg_clean = str(degrees[0]).title()
            inst_clean = str(insts[0]).title()
            strengths.append(f"Academic foundation in {deg_clean} from {inst_clean}")
        elif insts:
            inst_clean = str(insts[0]).title()
            strengths.append(f"Academic background from {inst_clean}")
        else:
            strengths.append("Education section is present with academic history")

    # 4. Technical Skills
    if skills:
        top_skills = skills[:5]
        strengths.append(f"Broad technical skill set of {len(skills)} skills, featuring {', '.join(top_skills)}")

    # 5. Certifications
    certs = parsed_resume.get('certifications', [])
    if certs:
        strengths.append(f"Holds professional certifications, including {', '.join(certs[:3])}")

    # 6. Action Verbs
    if action_verbs:
        strengths.append(f"Bullet points use strong action verbs like {', '.join(action_verbs[:4])}")

    # 7. Formatting & ATS
    if scores.get('formatting_score', 0) >= 14:
        strengths.append("Consistent ATS-friendly layout with clear section dividers and bullet points")

    # 8. Quantified Achievements
    if scores.get('content_score', 0) >= 16:
        strengths.append("Includes measurable outcomes and metrics to quantify job and project impact")

    # Fallback to make sure it's never empty
    if not strengths:
        strengths.append("Resume contains core sections (Skills, Experience, Education) required by recruiters")

    return strengths

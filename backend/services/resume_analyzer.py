import spacy
import re
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Optional
from backend.models.schemas import IssueDetail
from backend.services.groq_parser import parse_resume, parse_job_description, COMMON_ACTION_VERBS
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
    
    # 1. Groq Parse (uses sha256 cache internally)
    parsed_resume = parse_resume(resume_text)
    
    if not isinstance(parsed_resume, dict):
        parsed_resume = {}
        
    personal_info = parsed_resume.get('personal_info')
    if not isinstance(personal_info, dict):
        personal_info = {}
    parsed_resume['personal_info'] = personal_info

    skills_dict = parsed_resume.get('skills')
    if not isinstance(skills_dict, dict):
        skills_dict = {}
    parsed_resume['skills'] = skills_dict

    skills = skills_dict.get('technical_skills')
    if not isinstance(skills, list):
        skills = []
    skills_dict['technical_skills'] = skills

    soft_skills = skills_dict.get('soft_skills')
    if not isinstance(soft_skills, list):
        soft_skills = []
    skills_dict['soft_skills'] = soft_skills

    projects = parsed_resume.get('projects')
    if not isinstance(projects, list):
        projects = []
    parsed_resume['projects'] = projects

    experience_entries = parsed_resume.get('experience')
    if not isinstance(experience_entries, list):
        experience_entries = []
    parsed_resume['experience'] = experience_entries

    certifications = parsed_resume.get('certifications')
    if not isinstance(certifications, list):
        certifications = []
    parsed_resume['certifications'] = certifications

    confidence_scores = parsed_resume.get('confidence_scores')
    if not isinstance(confidence_scores, dict):
        confidence_scores = {}
    parsed_resume['confidence_scores'] = confidence_scores
    
    # Compute deterministic action verbs
    local_verbs = []
    text_lower = resume_text.lower()
    for verb in COMMON_ACTION_VERBS:
        if re.search(rf'\b{re.escape(verb)}\b', text_lower):
            local_verbs.append(verb.capitalize() if '-' not in verb else '-'.join(w.capitalize() for w in verb.split('-')))
    action_verbs = local_verbs

    experience_months = sum(
        int(e.get('duration_months', 0))
        for e in parsed_resume.get('experience', [])
        if isinstance(e, dict)
    )

    contact_info = {
        'email':     parsed_resume.get('personal_info', {}).get('email'),
        'phone':     parsed_resume.get('personal_info', {}).get('phone'),
        'linkedin':  parsed_resume.get('personal_info', {}).get('linkedin'),
        'github':    parsed_resume.get('personal_info', {}).get('github'),
        'portfolio': parsed_resume.get('personal_info', {}).get('portfolio'),
    }

    # 2. Skill Evidence validation (projects & experiences)
    skill_validation = validate_skills_with_projects(
        skills=skills,
        projects=projects,
        experience_entries=parsed_resume.get('experience', []),
        embedder=embedder,
    )

    jd_comparison_result = None
    jd_keywords = []
    if job_description and job_description.strip():
        parsed_jd = parse_job_description(job_description.strip())
        jd_keywords = list(set(
            parsed_jd.get('keywords', []) +
            parsed_jd.get('required_skills', []) +
            parsed_jd.get('preferred_skills', [])
        ))
        
        # Merge technical skills + soft skills for JD keyword check
        all_skills_combined = skills + parsed_resume.get('skills', {}).get('soft_skills', [])
        jd_comparison_result = compare_resume_with_jd(
            resume_text=resume_text,
            resume_keywords=all_skills_combined,
            resume_skills=skills,
            jd_text=job_description.strip(),
            jd_keywords=jd_keywords,
            embedder=embedder,
            nlp=nlp,
        )

    from backend.utils.file_utils import (
        get_default_grammar_results, get_default_location_results,
    )
    grammar_results = get_default_grammar_results()
    location_results = get_default_location_results()

    # 3. Base python scores calculation (pre-insights)
    base_scores = calculate_overall_score(
        text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        keywords=skills, # pass skills as keywords
        action_verbs=action_verbs,
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        jd_keywords=jd_keywords,
        experience_months=experience_months,
    )

    # 4. Stage 3 Recruiter Feedback (LLM reasoning call)
    from backend.services.groq_parser import generate_recruiter_feedback
    feedback = generate_recruiter_feedback(parsed_resume, jd_keywords, base_scores)

    # 5. Merge feedback back into parsed_resume for final scoring/evaluation
    parsed_resume['candidate_strengths'] = feedback.get('candidate_strengths', [])
    parsed_resume['candidate_weaknesses'] = feedback.get('candidate_weaknesses', [])
    parsed_resume['personalized_suggestions'] = feedback.get('personalized_suggestions', [])
    parsed_resume['recruiter_insights'] = feedback.get('recruiter_insights', {})
    parsed_resume['skill_analysis'] = feedback.get('skill_analysis', {})
    parsed_resume['experience_analysis'] = feedback.get('experience_analysis', {})

    # Merge project evaluations strength & weakness
    proj_evals = feedback.get('project_evaluations', {})
    for proj in parsed_resume.get('projects', []):
        title = proj.get('title')
        eval_info = proj_evals.get(title, {}) if title else {}
        proj['strength'] = eval_info.get('strength') or "Valid implementation"
        proj['weakness'] = eval_info.get('weakness') or "No critical weaknesses"

    # 6. Recalculate overall scores with merged recruiter insights
    scores = calculate_overall_score(
        text=resume_text,
        parsed_resume=parsed_resume,
        skills=skills,
        keywords=skills, # pass skills as keywords
        action_verbs=action_verbs,
        skill_validation_results=skill_validation,
        grammar_results=grammar_results,
        location_results=location_results,
        jd_keywords=jd_keywords,
        experience_months=experience_months,
    )

    # 7. Detailed Feedback recommendations
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

    validated_raw = skill_validation.get('validated_skills', [])
    unvalidated_raw = skill_validation.get('unvalidated_skills', [])
    total_skills = len(validated_raw) + len(unvalidated_raw)
    val_pct = round((len(validated_raw) / total_skills * 100) if total_skills > 0 else 0, 1)

    skill_validation_details = {
        "validated": [
            {
                "skill": item['skill'],
                "projects": item.get('projects', []),
                "proficiency": item.get('proficiency', 'Beginner'),
                "confidence": item.get('confidence', 0.85)
            }
            for item in validated_raw
        ],
        "unvalidated": unvalidated_raw,
        "total": total_skills,
        "validated_count": len(validated_raw),
        "validation_pct": val_pct,
    }

    # Generate custom strengths & concern items
    custom_strengths = scores.get('recruiter_insights', {}).get('strengths', [])
    if not custom_strengths:
        custom_strengths = ["Resume structure meets basic ATS parsing requirements."]

    # Personalized suggestions checklist
    suggestions = list(parsed_resume.get("personalized_suggestions") or [])
    if jd_comparison_result:
        for kw in jd_comparison_result.get("missing_keywords", []):
            suggestions.append(f"Add missing keyword '{kw}' to align with job description.")
    if not suggestions:
        suggestions = ["Optimize your experience section with more action verbs and quantified achievements."]

    return {
        "ATS_score": scores['overall_score'],
        "ats_score": scores['overall_score'],
        "resume_quality_score": scores['resume_quality_score'],
        "ats_compatibility_score": scores['ats_compatibility_score'],
        "job_match_score": scores['job_match_score'],
        "suggestions": suggestions,
        "component_scores": {
            "formatting": scores['formatting_score'],
            "keywords": scores['keywords_score'],
            "content": scores['content_score'],
            "skill_validation": scores['skill_validation_score'],
            "ats_compatibility": scores['ats_compatibility_score_raw'],
        },
        "issues_summary": issues_summary,
        "detailed_feedback": detailed_feedback,
        "jd_match_analysis": jd_comparison_result,
        "jd_comparison": jd_comparison_result,
        "skills": skills,
        "matched_keywords": (
            jd_comparison_result['matched_keywords']
            if jd_comparison_result else list(skills[:20])
        ),
        "missing_keywords": (
            jd_comparison_result['missing_keywords']
            if jd_comparison_result else []
        ),
        "strengths": custom_strengths,
        "interpretation": scores.get('overall_interpretation', ''),
        "skill_validation_details": skill_validation_details,
        "experience_months": experience_months,
        
        # New Recruiter Insights properties
        "recruiter_insights": scores.get('recruiter_insights', {}),
        "red_flags": scores.get('red_flags', []),
        "critical_issues": scores.get('red_flags', []),
        "confidence_scores": parsed_resume.get('confidence_scores', {}),
        "resume_completeness_pct": float(scores.get('resume_completeness_pct') or 100.0) if scores.get('resume_completeness_pct') is not None else 100.0,
        "completeness_percentage": float(scores.get('completeness_percentage') or 100.0) if scores.get('completeness_percentage') is not None else 100.0,
        "explainable_cards": scores.get('explainable_cards', {})
    }

import os
import json 
import logging
import re
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from groq import Groq

logger = logging.getLogger('ats_resume_scorer')

GROQ_MODEL = 'llama-3.1-8b-instant'

_client = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        _client = Groq(api_key=api_key)
    return _client

def _get_cache_db_path() -> str:
    p = Path(__file__).resolve().parent.parent / "database" / "parser_cache.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)

def _init_cache_db() -> None:
    try:
        db_path = _get_cache_db_path()
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS parse_cache (
                text_hash TEXT PRIMARY KEY,
                parsed_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to initialize parser cache DB: {e}")

def _get_cached_parse(raw_text: str) -> dict | None:
    try:
        _init_cache_db()
        db_path = _get_cache_db_path()
        text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
        conn = sqlite3.connect(db_path, timeout=2.0)
        cursor = conn.cursor()
        cursor.execute("SELECT parsed_json FROM parse_cache WHERE text_hash = ?", (text_hash,))
        row = cursor.fetchone()
        conn.close()
        if row:
            logger.info("Found cached parsed resume JSON!")
            return json.loads(row[0])
    except Exception as e:
        logger.warning(f"Cache lookup failed: {e}")
    return None

def _set_cached_parse(raw_text: str, parsed_dict: dict) -> None:
    try:
        _init_cache_db()
        db_path = _get_cache_db_path()
        text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()
        conn = sqlite3.connect(db_path, timeout=2.0)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO parse_cache (text_hash, parsed_json) VALUES (?, ?)", 
                       (text_hash, json.dumps(parsed_dict)))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")

RESUME_SYSTEM_PROMPT = (
    "You are a professional recruiter-grade ATS resume parser. Extract information from the resume "
    "and return ONLY a valid JSON object. Do not include any explanations, warnings, markdown code blocks, or text outside the JSON."
)

RESUME_USER_PROMPT = """Extract the following structural schema from this resume and return strictly as JSON:
{{
  "personal_info": {{
    "name": "full name or empty string",
    "email": "email address or null",
    "phone": "phone number or null",
    "linkedin": "LinkedIn profile URL or null",
    "github": "GitHub profile URL or null",
    "portfolio": "personal website or portfolio URL or null",
    "languages": ["list of languages spoken"]
  }},
  "summary": "professional summary or profile text",
  "detected_role": "Detect the closest matching role from this list: Software Engineer | Backend Developer | Frontend Developer | Full Stack Developer | AI/ML Engineer | Data Scientist | DevOps Engineer | Cybersecurity | Mobile Developer | Product/Business roles",
  "skills": {{
    "technical_skills": ["technical skills, languages, frameworks, developer tools"],
    "soft_skills": ["interpersonal, leadership, or communication skills"]
  }},
  "experience": [
    {{
      "job_title": "title of the role",
      "company": "company name",
      "start_date": "MM/YYYY or Year",
      "end_date": "MM/YYYY, Year, or Present",
      "duration_months": 12,
      "description": "responsibilities described in the experience section",
      "achievements": ["bulleted achievements in this role, especially metrics"],
      "technologies_used": ["technologies referenced in this experience"]
    }}
  ],
  "projects": [
    {{
      "title": "project name",
      "description": "project description and architecture",
      "technologies_used": ["tech used in this project"],
      "complexity": "Beginner | Intermediate | Advanced",
      "business_impact": "impact description or metrics",
      "has_aiml": true/false,
      "has_frontend": true/false,
      "has_backend": true/false,
      "has_database": true/false,
      "has_cloud": true/false,
      "has_apis": true/false,
      "has_auth": true/false,
      "has_deployment": true/false,
      "has_testing": true/false,
      "has_cicd": true/false
    }}
  ],
  "education": [
    {{
      "degree": "degree and major",
      "institution": "university or school name",
      "year": "graduation year"
    }}
  ],
  "certifications": [
    {{
      "name": "certification name, e.g. AWS Certified Solutions Architect",
      "provider": "AWS, Azure, Google, Cisco, Red Hat, Meta, IBM, NVIDIA, MongoDB, Oracle, Microsoft, Coursera, NPTEL, or Other",
      "year": "completion year if present, otherwise null"
    }}
  ],
  "publications": ["list of publications if present"],
  "achievements": ["general list of achievements or awards"],
  "awards": ["list of awards received"],
  "confidence_scores": {{
    "personal_info": 0.95,
    "skills": 0.90,
    "experience": 0.90,
    "projects": 0.85,
    "certifications": 0.90
  }}
}}

Resume Text:
{raw_text}"""

FEEDBACK_SYSTEM_PROMPT = "You are a professional recruiter-grade ATS advisor. Analyze the structured resume profile and score metadata, and return ONLY a valid JSON object."

FEEDBACK_USER_PROMPT = """Analyze the candidate profile and ATS scores to generate professional pre-screening feedback.

Structured Resume:
{resume_json}

Target Role: {detected_role}
Base Scores: Formatting: {formatting}/20, Completeness: {completeness}/100, Experience: {experience}/100, Projects: {projects}/100, Skill Validation: {validation}/100.
{jd_keywords_section}

Return strictly as JSON with this schema:
{{
  "candidate_strengths": ["At least 3 highly candidate-specific strengths referencing actual projects/experience evidence on this resume"],
  "candidate_weaknesses": ["At least 3 highly candidate-specific profile weaknesses or gaps referencing actual gaps"],
  "personalized_suggestions": ["At least 3 personalized, highly actionable improvement suggestions referencing specific projects/experiences on this resume"],
  "recruiter_insights": {{
    "overall_recommendation": "Strong Hire | Hire | Borderline | No Hire",
    "interview_readiness": "Detailed readiness summary describing candidate's alignment, technical depth, and communication capability based on their profile",
    "hiring_concerns": ["At least 3 specific recruiter concerns, or none if exceptional"]
  }},
  "skill_analysis": {{
    "tech_skill_name": {{
      "proficiency": "Beginner | Intermediate | Advanced",
      "evidence": "Detailed evidence statement showing specific projects/experiences where it was demonstrated"
    }}
  }},
  "experience_analysis": {{
    "observations": ["At least 3 candidate-specific observations about job duties, growth, and metrics from this resume"],
    "technical_ownership": "Observation of systems design and ownership demonstrated",
    "leadership": "Evidence of mentoring, leading teams, or collaboration",
    "impact_and_metrics": "Analysis of their business outcomes and quantitative metrics"
  }},
  "project_evaluations": {{
    "project_title": {{
      "strength": "Project implementation strength referencing tech choices",
      "weakness": "Project implementation weakness or missing details"
    }}
  }}
}}

Important:
- Return ONLY valid JSON. No markdown code fences, no explanation.
- Ensure all strengths, weaknesses, and suggestions reference actual resume entities (e.g. project names, company names).
"""

def estimate_tokens(text: str) -> int:
    return len(text) // 4

def truncate_resume_text(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    logger.info(f"Resume text length ({len(text)} chars) exceeds maximum. Truncating...")
    half = max_chars // 2
    return text[:half] + "\n... [truncated for token limit] ...\n" + text[-half:]

def _call_groq(client: Groq, system_prompt: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=GROQ_MODEL, 
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ],
        temperature=0.0,
        seed=42,
        max_tokens=4096
    )
    return response.choices[0].message.content.strip()

def _try_parse_json(text: str) -> dict | None:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        first_newline = cleaned.index("\n") if "\n" in cleaned else len(cleaned)
        cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return None

def parse_resume(raw_text: str) -> Dict:
    cached = _get_cached_parse(raw_text)
    if cached is not None:
        return cached

    client = _get_client()
    
    # Intelligently truncate extremely long raw resume text
    raw_text_truncated = truncate_resume_text(raw_text, max_chars=12000)
    prompt = RESUME_USER_PROMPT.format(raw_text=raw_text_truncated)
    
    # Token estimation & control
    estimated_tokens = estimate_tokens(prompt) + estimate_tokens(RESUME_SYSTEM_PROMPT)
    print(f"Estimated token count for prompt: {estimated_tokens}")
    
    if estimated_tokens > 5000:
        logger.info(f"Estimated tokens ({estimated_tokens}) exceed 5000. Shortening user prompt...")
        # Auto-shorten by truncating raw_text_truncated further
        raw_text_truncated = truncate_resume_text(raw_text, max_chars=8000)
        prompt = RESUME_USER_PROMPT.format(raw_text=raw_text_truncated)
        new_estimated = estimate_tokens(prompt) + estimate_tokens(RESUME_SYSTEM_PROMPT)
        print(f"New estimated token count after shortening: {new_estimated}")

    raw_response = _call_groq(client, RESUME_SYSTEM_PROMPT, prompt)
    result = _try_parse_json(raw_response)

    if result is not None:
        validated = _validate_resume_result(result, raw_text)
        _set_cached_parse(raw_text, validated)
        return validated
    
    logger.warning("Groq resume parse: first attempt returned invalid JSON, retrying...")
    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt
    )
    raw_response = _call_groq(client, RESUME_SYSTEM_PROMPT, strict_prompt)
    result = _try_parse_json(raw_response)
    if result is not None:
        validated = _validate_resume_result(result, raw_text)
        _set_cached_parse(raw_text, validated)
        return validated

    raise ValueError(
        f"Groq returned unparseable response after retry. Raw response:\n{raw_response[:500]}"
    )

def _validate_feedback_result(result: dict, parsed_resume: dict) -> dict:
    if not isinstance(result, dict):
        result = {}

    for list_key in ["candidate_strengths", "candidate_weaknesses", "personalized_suggestions"]:
        if not isinstance(result.get(list_key), list):
            result[list_key] = []
        result[list_key] = [str(x) for x in result[list_key] if x is not None]

    ri = result.get("recruiter_insights")
    if not isinstance(ri, dict):
        ri = {}
    cleaned_ri = {
        "overall_recommendation": ri.get("overall_recommendation") or "Borderline",
        "interview_readiness": ri.get("interview_readiness") or "",
        "hiring_concerns": ri.get("hiring_concerns") or []
    }
    if not isinstance(cleaned_ri["hiring_concerns"], list):
        cleaned_ri["hiring_concerns"] = []
    cleaned_ri["hiring_concerns"] = [str(x) for x in cleaned_ri["hiring_concerns"] if x is not None]
    result["recruiter_insights"] = cleaned_ri

    sa = result.get("skill_analysis")
    if not isinstance(sa, dict):
        sa = {}
    cleaned_sa = {}
    for k, val in sa.items():
        if not isinstance(val, dict):
            val = {}
        cleaned_sa[str(k)] = {
            "proficiency": val.get("proficiency") or "Beginner",
            "evidence": val.get("evidence") or "Listed in skills section"
        }
    result["skill_analysis"] = cleaned_sa

    ea = result.get("experience_analysis")
    if not isinstance(ea, dict):
        ea = {}
    cleaned_ea = {
        "observations": ea.get("observations") or [],
        "technical_ownership": ea.get("technical_ownership") or "",
        "leadership": ea.get("leadership") or "",
        "impact_and_metrics": ea.get("impact_and_metrics") or ""
    }
    if not isinstance(cleaned_ea["observations"], list):
        cleaned_ea["observations"] = []
    cleaned_ea["observations"] = [str(x) for x in cleaned_ea["observations"] if x is not None]
    result["experience_analysis"] = cleaned_ea

    pe = result.get("project_evaluations")
    if not isinstance(pe, dict):
        pe = {}
    cleaned_pe = {}
    for k, val in pe.items():
        if not isinstance(val, dict):
            val = {}
        cleaned_pe[str(k)] = {
            "strength": val.get("strength") or "Valid implementation",
            "weakness": val.get("weakness") or "No critical weaknesses"
        }
    result["project_evaluations"] = cleaned_pe

    return result

def _init_feedback_cache_db() -> None:
    try:
        db_path = _get_cache_db_path()
        conn = sqlite3.connect(db_path, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_cache (
                cache_key TEXT PRIMARY KEY,
                feedback_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to initialize feedback cache DB: {e}")

def _get_cached_feedback(parsed_resume: dict, jd_keywords: list, scores: dict) -> dict | None:
    try:
        _init_feedback_cache_db()
        db_path = _get_cache_db_path()

        concise = {
            "summary": parsed_resume.get("summary", ""),
            "experience": [exp.get("job_title") for exp in parsed_resume.get("experience", [])],
            "projects": [proj.get("title") for proj in parsed_resume.get("projects", [])],
            "skills": parsed_resume.get("skills", {})
        }

        key_data = {
            "resume": concise,
            "jd_keywords": jd_keywords,
            "scores": {
                "formatting_score": scores.get("formatting_score", 0),
                "completeness_score": scores.get("completeness_score", 0),
                "experience_score": scores.get("experience_score", 0),
                "projects_score": scores.get("projects_score", 0),
                "skill_validation_score": scores.get("skill_validation_score", 0)
            }
        }

        serialized = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

        conn = sqlite3.connect(db_path, timeout=2.0)
        cursor = conn.cursor()
        cursor.execute("SELECT feedback_json FROM feedback_cache WHERE cache_key = ?", (cache_key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            logger.info("Found cached recruiter feedback JSON!")
            return json.loads(row[0])
    except Exception as e:
        logger.warning(f"Feedback cache lookup failed: {e}")
    return None

def _set_cached_feedback(parsed_resume: dict, jd_keywords: list, scores: dict, feedback_dict: dict) -> None:
    try:
        _init_feedback_cache_db()
        db_path = _get_cache_db_path()

        concise = {
            "summary": parsed_resume.get("summary", ""),
            "experience": [exp.get("job_title") for exp in parsed_resume.get("experience", [])],
            "projects": [proj.get("title") for proj in parsed_resume.get("projects", [])],
            "skills": parsed_resume.get("skills", {})
        }

        key_data = {
            "resume": concise,
            "jd_keywords": jd_keywords,
            "scores": {
                "formatting_score": scores.get("formatting_score", 0),
                "completeness_score": scores.get("completeness_score", 0),
                "experience_score": scores.get("experience_score", 0),
                "projects_score": scores.get("projects_score", 0),
                "skill_validation_score": scores.get("skill_validation_score", 0)
            }
        }

        serialized = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.sha256(serialized.encode('utf-8')).hexdigest()

        conn = sqlite3.connect(db_path, timeout=2.0)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO feedback_cache (cache_key, feedback_json) VALUES (?, ?)",
                       (cache_key, json.dumps(feedback_dict)))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Feedback cache write failed: {e}")

def generate_recruiter_feedback(parsed_resume: dict, jd_keywords: list, scores: dict) -> dict:
    # Try fetching from feedback cache first
    cached_feedback = _get_cached_feedback(parsed_resume, jd_keywords, scores)
    if cached_feedback is not None:
        return cached_feedback

    concise_resume = {
        "summary": parsed_resume.get("summary", ""),
        "detected_role": parsed_resume.get("detected_role", "Software Engineer"),
        "skills": parsed_resume.get("skills", {}),
        "experience": [
            {
                "job_title": exp.get("job_title"),
                "company": exp.get("company"),
                "achievements": exp.get("achievements", [])[:3]
            }
            for exp in parsed_resume.get("experience", [])
        ],
        "projects": [
            {
                "title": proj.get("title"),
                "description": proj.get("description", "")[:200],
                "technologies_used": proj.get("technologies_used", [])
            }
            for proj in parsed_resume.get("projects", [])
        ],
        "certifications": [c.get("name") for c in parsed_resume.get("certifications", [])]
    }

    resume_json = json.dumps(concise_resume, indent=2)
    jd_section = f"Job Description Keywords: {', '.join(jd_keywords)}" if jd_keywords else "No target Job Description provided."

    prompt = FEEDBACK_USER_PROMPT.format(
        resume_json=resume_json,
        detected_role=concise_resume["detected_role"],
        formatting=scores.get("formatting_score", 0),
        completeness=scores.get("completeness_score", 0),
        experience=scores.get("experience_score", 0),
        projects=scores.get("projects_score", 0),
        validation=scores.get("skill_validation_score", 0),
        jd_keywords_section=jd_section
    )

    estimated_tokens = estimate_tokens(prompt) + estimate_tokens(FEEDBACK_SYSTEM_PROMPT)
    print(f"Estimated token count for Feedback prompt: {estimated_tokens}")

    if estimated_tokens > 5000:
        logger.info(f"Feedback prompt exceeds 5000 tokens. Shortening resume details...")
        concise_resume["experience"] = [
            {"job_title": exp.get("job_title"), "company": exp.get("company")}
            for exp in concise_resume["experience"]
        ]
        concise_resume["projects"] = [
            {"title": proj.get("title"), "technologies_used": proj.get("technologies_used")}
            for proj in concise_resume["projects"]
        ]
        resume_json = json.dumps(concise_resume, indent=2)
        prompt = FEEDBACK_USER_PROMPT.format(
            resume_json=resume_json,
            detected_role=concise_resume["detected_role"],
            formatting=scores.get("formatting_score", 0),
            completeness=scores.get("completeness_score", 0),
            experience=scores.get("experience_score", 0),
            projects=scores.get("projects_score", 0),
            validation=scores.get("skill_validation_score", 0),
            jd_keywords_section=jd_section
        )
        new_estimated = estimate_tokens(prompt) + estimate_tokens(FEEDBACK_SYSTEM_PROMPT)
        print(f"New estimated token count for Feedback prompt after shortening: {new_estimated}")

    client = _get_client()
    raw_response = _call_groq(client, FEEDBACK_SYSTEM_PROMPT, prompt)
    result = _try_parse_json(raw_response)

    if result is not None:
        validated_result = _validate_feedback_result(result, parsed_resume)
        _set_cached_feedback(parsed_resume, jd_keywords, scores, validated_result)
        return validated_result

    logger.warning("Groq Feedback parse: first attempt returned invalid JSON, retrying...")
    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt
    )
    raw_response = _call_groq(client, FEEDBACK_SYSTEM_PROMPT, strict_prompt)
    result = _try_parse_json(raw_response)
    if result is not None:
        validated_result = _validate_feedback_result(result, parsed_resume)
        _set_cached_feedback(parsed_resume, jd_keywords, scores, validated_result)
        return validated_result

    logger.warning("Groq Feedback parse: retry failed. Returning empty defaults.")
    empty_result = _validate_feedback_result({}, parsed_resume)
    return empty_result

JD_SYSTEM_PROMPT = (
    "You are a job description parser. Extract information and "
    "return ONLY a valid JSON object. No explanation, no markdown."
)

JD_USER_PROMPT = """Extract the following from this job description and return as JSON:
{{
  "job_title": "",
  "required_skills": ["list of must-have skills"],
  "preferred_skills": ["list of nice-to-have skills"],
  "experience_required": "",
  "education_required": "",
  "key_responsibilities": ["list of responsibilities"],
  "keywords": ["important keywords and phrases for ATS matching"]
}}

Important instructions:
- required_skills: skills explicitly stated as required or must-have.
- preferred_skills: skills stated as preferred, nice-to-have, or bonus.
- keywords: extract ALL important terms an ATS system would match against,
  including skills, technologies, certifications, and domain terms.
- Return ONLY valid JSON. No markdown code fences, no explanation.

Job Description Text:
{raw_text}"""

def parse_job_description(raw_text: str) -> Dict:
    client = _get_client()
    prompt = JD_USER_PROMPT.format(raw_text=raw_text)

    raw_response = _call_groq(client, JD_SYSTEM_PROMPT, prompt)
    result = _try_parse_json(raw_response)
    if result is not None:
        return _validate_jd_result(result)

    logger.warning("Groq JD parse: first attempt returned invalid JSON, retrying...")
    strict_prompt = (
        "Your previous response was not valid JSON. "
        "Return ONLY the raw JSON object, no markdown, no explanation, no code fences.\n\n"
        + prompt
    )
    raw_response = _call_groq(client, JD_SYSTEM_PROMPT, strict_prompt)
    result = _try_parse_json(raw_response)
    if result is not None:
        return _validate_jd_result(result)

    raise ValueError(
        f"Groq returned unparseable response after retry. Raw response:\n{raw_response[:500]}"
    )

def _validate_jd_result(result: dict) -> dict:
    defaults = {
        "job_title": "",
        "required_skills": [],
        "preferred_skills": [],
        "experience_required": "",
        "education_required": "",
        "key_responsibilities": [],
        "keywords": [],
    }
    for key, default in defaults.items():
        if key not in result or result[key] is None:
            result[key] = default
        if isinstance(default, list) and not isinstance(result[key], list):
            result[key] = default
    return result

def _normalize_and_deduplicate(lst: list) -> list:
    if not isinstance(lst, list):
        return []
    seen = set()
    normalized = []
    for item in lst:
        if not item:
            continue
        item_str = str(item).strip()
        if not item_str:
            continue
        item_lower = item_str.lower()
        if item_lower not in seen:
            seen.add(item_lower)
            normalized.append(item_str)
    return normalized

COMMON_ACTION_VERBS = {
    'led', 'managed', 'developed', 'built', 'designed', 'implemented', 'created',
    'optimized', 'co-developed', 'contributed', 'collaborated', 'engineered', 
    'architected', 'programmed', 'formulated', 'analyzed', 'executed', 'generated',
    'increased', 'decreased', 'saved', 'reduced', 'improved', 'integrated', 
    'automated', 'deployed', 'launched', 'directed', 'coordinated', 'administered'
}

# Schema Definitions for parser safety
PERSONAL_INFO_SCHEMA = {
    "name": "",
    "email": None,
    "phone": None,
    "linkedin": None,
    "github": None,
    "portfolio": None,
    "languages": []
}

SKILLS_SCHEMA = {
    "technical_skills": [],
    "soft_skills": []
}

CONFIDENCE_SCORES_SCHEMA = {
    "personal_info": 0.90,
    "skills": 0.85,
    "experience": 0.85,
    "projects": 0.80,
    "certifications": 0.85
}

EXPERIENCE_SCHEMA = {
    "job_title": "",
    "company": "",
    "start_date": "",
    "end_date": "",
    "duration_months": 0,
    "description": "",
    "achievements": [],
    "technologies_used": []
}

PROJECT_SCHEMA = {
    "title": "",
    "description": "",
    "technologies_used": [],
    "complexity": "Intermediate",
    "business_impact": "",
    "has_aiml": False,
    "has_frontend": False,
    "has_backend": False,
    "has_database": False,
    "has_cloud": False,
    "has_apis": False,
    "has_auth": False,
    "has_deployment": False,
    "has_testing": False,
    "has_cicd": False
}

EDUCATION_SCHEMA = {
    "degree": "",
    "institution": "",
    "year": ""
}

CERTIFICATION_SCHEMA = {
    "name": "",
    "provider": "Other",
    "year": ""
}

def _normalize_dict(d: Any, schema: dict) -> dict:
    if not isinstance(d, dict):
        d = {}
    cleaned = {}
    for k, default_val in schema.items():
        val = d.get(k)
        if val is None:
            cleaned[k] = default_val
        elif default_val is not None and not isinstance(val, type(default_val)):
            cleaned[k] = default_val
        else:
            cleaned[k] = val
    return cleaned

def _normalize_list_of_dicts(lst: Any, schema: dict) -> list:
    if not isinstance(lst, list):
        return []
    cleaned = []
    for item in lst:
        if not isinstance(item, dict):
            continue
        cleaned.append(_normalize_dict(item, schema))
    return cleaned

def _validate_resume_result(result: dict, raw_text: str = "") -> dict:
    if not isinstance(result, dict):
        result = {}

    result["personal_info"] = _normalize_dict(result.get("personal_info"), PERSONAL_INFO_SCHEMA)
    result["skills"] = _normalize_dict(result.get("skills"), SKILLS_SCHEMA)
    result["confidence_scores"] = _normalize_dict(result.get("confidence_scores"), CONFIDENCE_SCORES_SCHEMA)

    result["summary"] = result.get("summary") or ""
    if not isinstance(result["summary"], str):
        result["summary"] = str(result["summary"])

    result["detected_role"] = result.get("detected_role") or "Software Engineer"
    if not isinstance(result["detected_role"], str):
        result["detected_role"] = str(result["detected_role"])

    # Enforce lists of dicts
    result["experience"] = _normalize_list_of_dicts(result.get("experience"), EXPERIENCE_SCHEMA)
    result["projects"] = _normalize_list_of_dicts(result.get("projects"), PROJECT_SCHEMA)
    result["education"] = _normalize_list_of_dicts(result.get("education"), EDUCATION_SCHEMA)
    result["certifications"] = _normalize_list_of_dicts(result.get("certifications"), CERTIFICATION_SCHEMA)

    # Handle simple lists
    result["publications"] = _normalize_and_deduplicate(result.get("publications", []))
    result["achievements"] = _normalize_and_deduplicate(result.get("achievements", []))
    result["awards"] = _normalize_and_deduplicate(result.get("awards", []))

    # Skill lists deduplication and normalization
    result["skills"]["technical_skills"] = _normalize_and_deduplicate(result["skills"].get("technical_skills", []))
    result["skills"]["soft_skills"] = _normalize_and_deduplicate(result["skills"].get("soft_skills", []))

    # Inner attributes sanitization
    for exp in result["experience"]:
        exp["achievements"] = [str(x) for x in exp["achievements"] if x is not None]
        exp["technologies_used"] = [str(x) for x in exp["technologies_used"] if x is not None]
        try:
            exp["duration_months"] = int(exp["duration_months"])
        except (ValueError, TypeError):
            exp["duration_months"] = 0

    for proj in result["projects"]:
        proj["technologies_used"] = [str(x) for x in proj["technologies_used"] if x is not None]

    return result

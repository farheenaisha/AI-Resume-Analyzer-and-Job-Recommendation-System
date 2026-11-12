import io
import re
from pathlib import Path
from collections import Counter

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pypdf import PdfReader
from docx import Document

BASE_DIR = Path(__file__).parent

# Skills supported by the current sample job dataset.
SKILLS = [
    "python", "java", "javascript", "html", "css", "react", "node.js",
    "sql", "sqlite", "mysql", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "scikit-learn", "streamlit",
    "flask", "django", "git", "github", "docker", "aws", "communication",
    "teamwork", "problem solving", "project management", "excel",
    "power bi", "tableau", "data visualization", "c++", "c#", "php",
    "rest api", "linux", "testing", "selenium", "statistics",
    "data cleaning", "oop"
]

SKILL_ALIASES = {
    "scikit-learn": ["scikit learn", "sklearn"],
    "javascript": ["js"],
    "node.js": ["nodejs", "node js"],
    "rest api": ["restful api", "rest apis"],
    "power bi": ["powerbi"],
    "c++": ["cpp"],
    "c#": ["c sharp"],
    "problem solving": ["problem-solving"],
    "machine learning": ["ml"],
    "data analysis": ["data analytics"],
}

SKILL_CATEGORIES = {
    "Programming": ["python", "java", "javascript", "c++", "c#", "php", "html", "css", "oop"],
    "Data & AI": ["machine learning", "deep learning", "data analysis", "pandas", "numpy",
                  "scikit-learn", "data visualization", "excel", "power bi", "tableau",
                  "statistics", "data cleaning"],
    "Web & Backend": ["react", "node.js", "flask", "django", "streamlit", "rest api"],
    "Databases": ["sql", "sqlite", "mysql"],
    "Tools & DevOps": ["git", "github", "docker", "aws", "linux", "testing", "selenium"],
    "Soft skills": ["communication", "teamwork", "problem solving", "project management"],
}
CATEGORIES = {
    "Programming": SKILL_CATEGORIES["Programming"],
    "Web": SKILL_CATEGORIES["Web & Backend"],
    "Data & AI": SKILL_CATEGORIES["Data & AI"],
    "Databases": SKILL_CATEGORIES["Databases"],
    "Tools & DevOps": SKILL_CATEGORIES["Tools & DevOps"],
    "Soft skills": SKILL_CATEGORIES["Soft skills"],
}

SECTIONS = ["education", "experience", "skills", "projects"]
SECTION_PATTERNS = {
    "education": r"\b(education|academic background|qualification)\b",
    "experience": r"\b(experience|employment|internship|work history)\b",
    "skills": r"\b(skills|technical skills|core competencies)\b",
    "projects": r"\b(projects|academic projects|personal projects)\b",
}

# Weights are deliberately explicit so every job score can be explained.
MATCH_WEIGHTS = {
    "required_skills": 40,
    "preferred_skills": 10,
    "projects": 15,
    "experience": 15,
    "education": 10,
    "text_relevance": 10,
}

SOFT_SKILLS = {"communication", "teamwork", "problem solving", "project management"}

CORE_SKILLS = {
    "python", "java", "javascript", "sql", "machine learning", "react",
    "html", "css", "aws", "power bi", "excel", "testing", "node.js"
}

def _normalise(text):
    text = str(text or "").lower()
    text = text.replace("&", " and ")
    return re.sub(r"\s+", " ", text).strip()

def _contains_term(text, term):
    """Match a skill as a phrase, avoiding partial-word matches."""
    t = re.escape(_normalise(term))
    return bool(re.search(r"(?<![a-z0-9])" + t + r"(?![a-z0-9])", _normalise(text)))

def extract_resume_text(uploaded):
    data = uploaded.getvalue()
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        chunks = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                chunks.append(" | ".join(cell.text for cell in row.cells))
        return "\n".join(chunks)
    return data.decode("utf-8", errors="ignore")

def _detect_skills(text):
    low = _normalise(text)
    found = []
    evidence = {}
    for skill in SKILLS:
        variants = [skill] + SKILL_ALIASES.get(skill, [])
        matches = []
        for variant in variants:
            pattern = r"(?<![a-z0-9])" + re.escape(_normalise(variant)) + r"(?![a-z0-9])"
            matches.extend(re.finditer(pattern, low))
        if matches:
            found.append(skill)
            evidence[skill] = len(matches)
    return found, evidence

def _is_section_heading(line, section):
    cleaned = re.sub(r"[:：|•\\-]+$", "", line.strip())
    if not cleaned or len(cleaned) > 55 or len(cleaned.split()) > 6:
        return False
    return bool(re.fullmatch(SECTION_PATTERNS[section], cleaned, re.I))

def _section_text(text, section):
    """Return text following a standalone section heading until the next heading."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if _is_section_heading(line, section):
            start = i + 1
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start, len(lines)):
        if any(_is_section_heading(lines[i], key) for key in SECTIONS if key != section):
            end = i
            break
    return "\n".join(lines[start:end])

def _estimate_experience_years(text):
    low = _normalise(text)
    patterns = [
        r"(\d+(?:\.\d+)?)\+?\s+years?\s+(?:of\s+)?(?:professional\s+)?experience",
        r"experience\s+of\s+(\d+(?:\.\d+)?)\+?\s+years?"
    ]
    for pattern in patterns:
        match = re.search(pattern, low)
        if match:
            return float(match.group(1))
    return 0.0

def _education_relevance(text):
    low = _normalise(text)
    degree_terms = [
        "computer science", "software engineering", "information technology",
        "data science", "computer engineering", "statistics", "mathematics"
    ]
    return any(_contains_term(low, term) for term in degree_terms)

def analyze_resume(text):
    text = str(text or "")
    low = _normalise(text)
    words = re.findall(r"\b[\w+#.-]+\b", text)
    skills, skill_counts = _detect_skills(text)
    section_blocks = {name: _section_text(text, name) for name in SECTIONS}
    sections_present = [name for name, block in section_blocks.items()
                        if block.strip() or any(_is_section_heading(line, name) for line in text.splitlines())]
    missing_sections = [name for name in SECTIONS if name not in sections_present]

    # Evidence labels are based on resume evidence, not a claim of verified mastery.
    skill_evidence = {}
    for skill in skills:
        count = skill_counts.get(skill, 1)
        in_project = _contains_term(section_blocks["projects"], skill)
        in_experience = _contains_term(section_blocks["experience"], skill)
        if count >= 2 and (in_project or in_experience):
            label = "Strong evidence"
        elif count >= 2 or in_project or in_experience:
            label = "Developing evidence"
        else:
            label = "Mentioned"
        skill_evidence[skill] = {
            "mentions": count,
            "project_evidence": in_project,
            "experience_evidence": in_experience,
            "level": label,
        }

    # Transparent resume completeness score (not a certified ATS score).
    technical_count = len([skill for skill in skills if skill not in SOFT_SKILLS])
    soft_count = len([skill for skill in skills if skill in SOFT_SKILLS])
    skill_points = min(30, technical_count * 3 + soft_count * 1.5)
    section_points = len(sections_present) * 6.25
    project_points = 15 if section_blocks["projects"].strip() else 0
    detail_points = min(20, max(0, len(words) // 15))
    contact_points = 10 if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text) else 0
    readiness = round(min(100, skill_points + section_points + project_points + detail_points + contact_points))
    breakdown = {
        "Relevant skills": (round(skill_points), 30),
        "Resume sections": (round(section_points), 25),
        "Project evidence": (round(project_points), 15),
        "Content detail": (round(detail_points), 20),
        "Contact information": (round(contact_points), 10),
    }

    suggestions = []
    if "education" in missing_sections:
        suggestions.append("Add an Education section with degree, institution and expected graduation date.")
    if "projects" in missing_sections:
        suggestions.append("Add 2–3 relevant projects and explain your personal contribution.")
    if "experience" in missing_sections:
        suggestions.append("If you have no formal job experience, include internships, volunteer work or academic experience.")
    if len(skills) < 5:
        suggestions.append("Add relevant skills that you can demonstrate through coursework or projects.")
    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text):
        suggestions.append("Add a professional email address for recruiter contact.")
    if not re.search(r"\b\d+(?:\.\d+)?%?\b", text):
        suggestions.append("Add honest measurable outcomes to project descriptions, such as dataset size or time saved.")
    if not suggestions:
        suggestions.append("Your resume has a useful foundation. Strengthen it with measurable project outcomes and role-specific keywords.")

    return {
        "readiness_score": readiness,
        "skills": skills,
        "technical_skills": [skill for skill in skills if skill not in SOFT_SKILLS],
        "soft_skills": [skill for skill in skills if skill in SOFT_SKILLS],
        "skill_evidence": skill_evidence,
        "word_count": len(words),
        "sections_present": sections_present,
        "sections_missing": missing_sections,
        "breakdown": breakdown,
        "suggestions": suggestions,
        "experience_years": _estimate_experience_years(text),
        "education_relevant": _education_relevance(text),
    }

def score_label(score):
    if score >= 70:
        return "Strong"
    if score >= 40:
        return "Good start"
    return "Needs work"

def categorize_skills(skills):
    out = {}
    have = {s.lower() for s in skills}
    for category, members in SKILL_CATEGORIES.items():
        found = [skill for skill in members if skill in have]
        if found:
            out[category] = found
    return out

def skill_gaps(skills, jobs, top_n=3):
    have = {s.lower() for s in skills}
    counter = Counter()
    for job in jobs[:top_n]:
        for skill in job.get("missing", []):
            counter[skill.lower()] += 1
    return [skill for skill, _ in counter.most_common()]

def load_jobs():
    return pd.read_csv(BASE_DIR / "data" / "jobs.csv").fillna("")


ESSENTIAL_SKILLS = {
    "junior python developer": [{"python"}],
    "frontend developer intern": [{"html"}, {"css"}, {"javascript"}],
    "data analyst intern": [{"python", "sql"}, {"pandas"}],
    "machine learning intern": [{"python"}, {"machine learning"}],
    "qa engineer trainee": [{"testing", "selenium"}],
    "backend developer intern": [{"python", "node.js"}, {"rest api"}],
    "ui developer": [{"html"}, {"css"}, {"javascript"}],
    "database assistant": [{"sql"}],
    "bi analyst intern": [{"excel", "power bi"}],
    "java developer trainee": [{"java"}],
    "cloud support intern": [{"aws", "linux"}],
    "project coordinator intern": [{"project management", "excel"}, {"communication"}],
}

def _essential_requirements_met(title, have):
    requirements = ESSENTIAL_SKILLS.get(str(title).lower(), [])
    return all(bool(options & have) for options in requirements)

def _weighted_skill_coverage(required, have):
    if not required:
        return 0.0
    weights = [1.5 if skill.lower() in CORE_SKILLS else 1.0 for skill in required]
    earned = sum(weight for skill, weight in zip(required, weights) if skill.lower() in have)
    return earned / sum(weights) if sum(weights) else 0.0

def _job_experience_score(level, years):
    level = str(level).lower()
    if "intern" in level:
        return 1.0 if years <= 1 else 0.9
    if "entry" in level or "junior" in level or "trainee" in level:
        return 0.70 if years == 0 else (1.0 if years <= 2 else 0.85)
    if "mid" in level:
        return 1.0 if years >= 2 else 0.35
    if "senior" in level:
        return 1.0 if years >= 5 else 0.15
    return 0.75

def _project_coverage(required, project_text):
    # Projects are evaluated against technical requirements, not soft-skill keywords.
    technical_required = [skill for skill in required if skill not in SOFT_SKILLS]
    if not technical_required or not project_text.strip():
        return 0.0
    return sum(1 for skill in technical_required if _contains_term(project_text, skill)) / len(technical_required)

def recommend_jobs(resume_text, skills, analysis=None):
    jobs = load_jobs()
    analysis = analysis or analyze_resume(resume_text)
    have = {str(skill).lower() for skill in skills}
    project_text = _section_text(resume_text, "projects")
    experience_text = _section_text(resume_text, "experience")
    years = analysis.get("experience_years", 0.0)

    job_docs = [
        f"{row['title']} {row['description']} {row['skills']}"
        for _, row in jobs.iterrows()
    ]
    try:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=5000)
        matrix = vectorizer.fit_transform([resume_text] + job_docs)
        similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    except ValueError:
        similarities = [0.0] * len(jobs)

    results = []
    for index, (_, row) in enumerate(jobs.iterrows()):
        required = [item.strip().lower() for item in str(row["skills"]).split(",") if item.strip()]
        preferred_raw = str(row.get("preferred_skills", "")).strip()
        preferred = [item.strip().lower() for item in preferred_raw.split(",") if item.strip()]

        matched = [skill for skill in required if skill in have]
        missing = [skill for skill in required if skill not in have]
        preferred_matched = [skill for skill in preferred if skill in have]
        preferred_missing = [skill for skill in preferred if skill not in have]

        technical_required = [skill for skill in required if skill not in SOFT_SKILLS]
        soft_required = [skill for skill in required if skill in SOFT_SKILLS]
        technical_ratio = _weighted_skill_coverage(technical_required, have)
        soft_ratio = _weighted_skill_coverage(soft_required, have)
        # Keep the required-skills total at 40 points. If a job has no soft-skill
        # requirements, its technical skills use all 40 points (and vice versa).
        if technical_required and soft_required:
            technical_max, soft_max = 32, 8
        elif technical_required:
            technical_max, soft_max = 40, 0
        elif soft_required:
            technical_max, soft_max = 0, 40
        else:
            technical_max, soft_max = 0, 0
        required_score = technical_ratio * technical_max + soft_ratio * soft_max
        req_ratio = required_score / MATCH_WEIGHTS["required_skills"]
        pref_ratio = _weighted_skill_coverage(preferred, have) if preferred else 0.0
        project_ratio = _project_coverage(required, project_text)
        exp_ratio = _job_experience_score(row["level"], years)

        # A student/graduate can meet entry-level education through a relevant degree.
        edu_ratio = 1.0 if analysis.get("education_relevant") else (0.6 if "education" in analysis.get("sections_present", []) else 0.25)
        text_ratio = min(1.0, float(similarities[index]) / 0.35)

        components = {
            "Technical skills": round(technical_ratio * technical_max, 1),
            "Soft skills": round(soft_ratio * soft_max, 1),
            "Preferred skills": round(pref_ratio * MATCH_WEIGHTS["preferred_skills"], 1),
            "Relevant projects": round(project_ratio * MATCH_WEIGHTS["projects"], 1),
            "Experience fit": round(exp_ratio * MATCH_WEIGHTS["experience"], 1),
            "Education relevance": round(edu_ratio * MATCH_WEIGHTS["education"], 1),
            "Description relevance": round(text_ratio * MATCH_WEIGHTS["text_relevance"], 1),
        }
        score = round(sum(components.values()))
        # Do not recommend roles where none of the essential requirements are evidenced.
        suitable = req_ratio >= 0.25 and _essential_requirements_met(row["title"], have)
        if not suitable:
            tier = "Not recommended yet"
        elif score >= 75:
            tier = "Strong match"
        elif score >= 55:
            tier = "Potential match"
        else:
            tier = "Skill gap to address"

        reasons = []
        if technical_required:
            reasons.append(f"Technical skill match: {len([x for x in technical_required if x in have])}/{len(technical_required)} required technical skills found.")
        if soft_required:
            reasons.append(f"Soft-skill match: {len([x for x in soft_required if x in have])}/{len(soft_required)} required soft skills found.")
        if project_ratio >= 0.5:
            reasons.append("Your Projects section shows practical evidence related to this role.")
        elif project_text.strip():
            reasons.append("Your Projects section exists, but it does not yet demonstrate many of this role's required skills.")
        if missing:
            reasons.append("Important skills not found in the resume: " + ", ".join(missing[:5]) + ".")
        if not suitable:
            reasons.append("This role is not shown as a suitable match because one or more essential skills for this job are missing.")
        if not analysis.get("education_relevant"):
            reasons.append("Your resume does not clearly show a degree related to this role.")
        if years == 0 and "experience" in str(row["level"]).lower():
            reasons.append("Add relevant internship or work experience if you have it.")

        results.append({
            "id": int(row["id"]),
            "title": str(row["title"]),
            "company": str(row["company"]),
            "area": str(row["area"]),
            "level": str(row["level"]),
            "description": str(row["description"]),
            "skills": required,
            "matched": matched,
            "missing": missing,
            "technical_matched": [skill for skill in matched if skill not in SOFT_SKILLS],
            "technical_missing": [skill for skill in missing if skill not in SOFT_SKILLS],
            "soft_matched": [skill for skill in matched if skill in SOFT_SKILLS],
            "soft_missing": [skill for skill in missing if skill in SOFT_SKILLS],
            "preferred_matched": preferred_matched,
            "preferred_missing": preferred_missing,
            "match_score": max(0, min(100, score)),
            "score_breakdown": components,
            "score_breakdown_max": {
                "Technical skills": technical_max,
                "Soft skills": soft_max,
                "Preferred skills": MATCH_WEIGHTS["preferred_skills"],
                "Relevant projects": MATCH_WEIGHTS["projects"],
                "Experience fit": MATCH_WEIGHTS["experience"],
                "Education relevance": MATCH_WEIGHTS["education"],
                "Description relevance": MATCH_WEIGHTS["text_relevance"],
            },
            "recommendation": tier,
            "suitable": suitable,
            "reasons": reasons,
        })

    # Relevant roles appear first; unsuitable roles remain available for transparency,
    # but are placed at the bottom and clearly labelled.
    return sorted(results, key=lambda job: (job["suitable"], job["match_score"]), reverse=True)

def build_report(result, jobs):
    lines = [
        "CAREERLENS AI - RESUME ANALYSIS REPORT",
        "=" * 44,
        f"Resume readiness guidance score: {result['readiness_score']}/100 ({score_label(result['readiness_score'])})",
        "Note: This is a resume-completeness estimate, not a certified ATS score.",
        f"Words detected: {result['word_count']}",
        "Detected skills: " + (", ".join(result["skills"]) or "None"),
        "Sections found: " + (", ".join(result["sections_present"]) or "None"),
        "Sections missing: " + (", ".join(result.get("sections_missing", [])) or "None"),
        "", "SUGGESTIONS"
    ]
    lines += ["- " + item for item in result["suggestions"]]
    lines += ["", "JOB MATCH SCORE METHOD"]
    lines += [
        "- Required skills: up to 40 points (normally 32 technical + 8 soft skills when both are required; if a role has only one type, it uses the full 40 points)",
        "- Preferred skills: 10 points",
        "- Relevant projects: 15 points",
        "- Experience fit: 15 points",
        "- Education relevance: 10 points",
        "- Description relevance (TF-IDF): 10 points",
    ]
    lines += ["Scores are weighted evidence estimates, not hiring probabilities."]
    lines += ["", "TOP JOB MATCHES"]
    for job in jobs[:8]:
        lines.append(f"- {job['title']} — {job['match_score']}% ({job['recommendation']})")
        for factor, points in job.get("score_breakdown", {}).items():
            maximum = job.get("score_breakdown_max", {}).get(factor, 0)
            lines.append(f"    {factor}: {points}/{maximum}")
        if job.get("matched"):
            lines.append("    Matched skills: " + ", ".join(job["matched"]))
        if job.get("missing"):
            lines.append("    Missing required skills: " + ", ".join(job["missing"]))
        for reason in job.get("reasons", []):
            lines.append("    Explanation: " + reason)
    lines += ["", "Important: job records are sample listings in the local dataset, not live vacancies."]
    return "\n".join(lines)

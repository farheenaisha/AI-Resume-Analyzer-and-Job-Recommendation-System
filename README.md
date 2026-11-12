# CareerLens AI — Resume Analyzer & Job Recommendation System

A student-friendly, explainable resume analyzer built with Python, Streamlit, SQLite and scikit-learn.

## Features
- PDF, DOCX and TXT resume extraction
- Resume completeness/readiness guidance score with a visible breakdown
- Skill detection with aliases (for example, `sklearn` / `scikit-learn`)
- Skill evidence levels based on mentions and whether a skill appears in project or experience text
- Job recommendations using weighted skill coverage, project evidence, experience fit, education relevance and TF-IDF text relevance
- Required and preferred skill gaps for each role
- Job-by-job percentage explanation showing points earned out of each factor's maximum
- Filters, saved jobs, analysis history and downloadable reports
- SQLite accounts and per-user analysis storage

## How job matching works

Each sample job receives a score out of 100:

| Factor | Maximum points |
|---|---:|
| Required skill coverage | 40 |
| Preferred skill coverage | 10 |
| Relevant project evidence | 15 |
| Experience fit | 15 |
| Education relevance | 10 |
| TF-IDF description relevance | 10 |
| **Total** | **100** |

Required skills are weighted more heavily when they are central to the role. Some roles also have essential-skill rules. For example, the Java Developer role is not shown as a suitable recommendation if Java is not evidenced in the resume. Roles with less than 25% required-skill coverage or missing essential skills are hidden by default, but can be shown with the optional filter.

The score is an explainable estimate based on the text in the resume and the local sample-job dataset. It is **not** a probability of getting hired, a verified measure of someone's real ability, or a certified ATS score.

## Skill evidence labels

- **Strong evidence:** the skill appears more than once and is also found in a Projects or Experience section.
- **Developing evidence:** the skill appears more than once, or appears in a Projects/Experience section.
- **Mentioned:** the skill appears in the resume but has limited supporting context.

These labels describe evidence in the document; they do not prove proficiency. A candidate should only list skills they can genuinely demonstrate.

## Machine-learning explanation

- TF-IDF converts resume and job-description text into numerical vectors.
- Cosine similarity estimates text relevance between the resume and each job description.
- Weighted matching combines this NLP relevance signal with explicit skill, project, experience and education evidence.

This version uses TF-IDF and a transparent weighted scoring layer. It does **not** claim to train a supervised classifier: a reliable supervised model would require a larger, labelled dataset of resumes and job-role outcomes. The current `jobs.csv` contains illustrative sample roles, not live vacancies.

## Resume readiness score

The readiness score is separate from job match. It evaluates resume completeness using detected relevant skills, section coverage, project evidence, content detail and contact information. It is a guidance score, not a certified ATS score.

## Run on Windows (VS Code terminal)

1. Extract the ZIP.
2. Open the `CareerLens_AI_Full` folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

5. Register an account, sign in and open Resume Analyzer.
6. Use the included sample resume to test the project.

## Database and privacy

The app creates `careerlens.db` in the project folder on first run. It stores account details, profile fields, analysis history and saved jobs. Passwords are stored as salted PBKDF2 hashes, not plain text. This is a local educational app; do not upload sensitive personal documents to an untrusted deployment.

## Current limitations
- The job list is a small illustrative dataset, not live vacancies.
- Skill detection is dictionary/keyword-based and may miss synonyms or context.
- Skill evidence labels are inferred from resume text, not validated by an employer or skills test.
- Experience years are estimated only when an explicit years-of-experience phrase is present.
- Scanned/image-only PDFs may require OCR.
- A real production system would need a larger verified job dataset, broader skill ontology, labelled evaluation data, privacy/security review and human oversight.


## How CareerLens AI calculates scores

**Resume readiness (0–100)** is a resume-completeness guide, not a certified ATS score:
- Relevant skills: up to 30 points (technical skills contribute more than soft-skill keywords)
- Resume sections: up to 25 points
- Project evidence: up to 15 points
- Content detail: up to 20 points
- Contact information: up to 10 points

**Job match (0–100)** uses a weighted combination of evidence:
- Required skills: up to 40 points. When a role requires both types, 32 points are for technical skills and 8 for soft skills. If it requires only one type, that type can earn all 40 points.
- Preferred skills: 10 points
- Relevant technical project evidence: 15 points
- Experience fit: 15 points
- Education relevance: 10 points
- Resume/job-description text relevance using TF-IDF and cosine similarity: 10 points

Each job card shows the points earned for every factor, matched skills, missing skills, and an explanation. Technical skills are treated as the main role-specific evidence; soft skills support the match but do not replace required technical skills.

**Limitations:** skills are detected from a maintained keyword list and aliases, so a synonym may be missed. Evidence labels are based on text mentions and do not verify real proficiency. Job records are examples in the local CSV dataset, not live vacancies. Scores are guidance estimates, not a prediction of hiring success.

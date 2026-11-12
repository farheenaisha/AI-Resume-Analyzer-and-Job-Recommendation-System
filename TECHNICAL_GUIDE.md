# CareerLens AI — Simple Technical Guide

## 1. What does this project do?
CareerLens AI reads a resume, identifies known skills, checks resume completeness, and compares the resume with job examples stored in `data/jobs.csv`. It then ranks suitable sample roles and explains the score and skill gaps.

## 2. How does it work?
1. **Upload:** The user uploads a PDF, DOCX, or TXT resume.
2. **Text extraction:** `analyzer.py` extracts readable text with `pypdf` (PDF), `python-docx` (DOCX), or normal text decoding (TXT).
3. **Skill detection:** The program checks the text against its skill dictionary and aliases. It separates technical skills from soft skills. This is keyword-based detection; it does not verify someone's real ability.
4. **Resume readiness:** It calculates a completeness score from skills, sections, project evidence, content detail, and contact information.
5. **Job matching:** It reads the sample jobs from `data/jobs.csv`, compares the resume with each job, and calculates a weighted score.
6. **Explanation:** The app shows matched/missing skills and the points earned for each score factor.
7. **Saving:** `database.py` uses SQLite to store user accounts, previous analyses, and saved jobs.

## 3. Job match score (100 points)
| Factor | Maximum points | What it checks |
|---|---:|---|
| Required technical skills | Usually 32; 40 if no soft skills are required | How many role-specific technical skills appear in the resume |
| Required soft skills | Usually 8; 40 if no technical skills are required | Communication, teamwork, problem solving, project management, etc. |
| Preferred skills | 10 | Extra skills mentioned as preferred by the job |
| Relevant projects | 15 | Whether technical job skills are evidenced in the Projects section |
| Experience fit | 15 | Whether the resume's stated years fit the role level |
| Education relevance | 10 | Whether a relevant education background/section is shown |
| Description relevance | 10 | Text similarity between the resume and job description using TF-IDF + cosine similarity |

When a role requires both technical and soft skills, required-skill points are split 32/8. If it requires only technical skills, technical skills can earn all 40 required-skill points. If it requires only soft skills, soft skills can earn all 40. Therefore, the total possible score remains 100.

## 4. Resume readiness score (100 points)
- Relevant skills: up to 30 points. Technical skills contribute more than soft-skill keywords.
- Resume sections: up to 25 points.
- Project evidence: up to 15 points.
- Content detail: up to 20 points.
- Contact information: up to 10 points.

This is a resume-completeness guide, not a certified ATS score. It is different from a job match score.

## 5. Techniques and libraries
- **Keyword matching:** detects skills using a maintained list and aliases.
- **TF-IDF:** converts resume/job text into numerical text features.
- **Cosine similarity:** measures how similar the resume text is to each job description.
- **Weighted scoring:** combines separate evidence factors into a score out of 100.
- **pypdf / python-docx:** read text from supported resume formats.
- **Pandas:** reads the job CSV and prepares tabular data.
- **Streamlit:** provides the web interface.
- **Plotly:** displays score and skill charts.
- **SQLite:** stores local application data.

**Training clarification:** This version does not train a supervised model on labelled resumes. TF-IDF and cosine similarity are NLP techniques used to compare text; keyword skill detection and the weighted scoring formula are transparent programmed logic.

## 6. How to run it
Open the project folder in VS Code. Activate the existing virtual environment, then run:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the Local URL printed in the terminal (normally `http://localhost:8501`). The installation command is normally needed only once per virtual environment, or when requirements change. To use the app again later, activate the same environment and run the Streamlit command; do not recreate the environment each time.

## 7. Important limitations
- Job listings are examples in the local CSV file, not live vacancies.
- Skill detection can miss a synonym that is not in the dictionary.
- Mentioning a skill does not prove proficiency.
- A scanned/image-only PDF may not contain extractable text and may need OCR.
- Percentages are guidance estimates, not hiring probabilities or guarantees.

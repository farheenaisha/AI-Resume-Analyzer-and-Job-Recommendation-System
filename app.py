import re, json
from html import escape
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import (init_db, create_user, verify_user, get_user, update_profile, save_analysis,
                      get_analyses, save_job, get_saved_jobs, delete_saved_job, delete_analysis)
from analyzer import extract_resume_text, analyze_resume, recommend_jobs, build_report, CATEGORIES

BASE = Path(__file__).resolve().parent
st.set_page_config(page_title="CareerLens AI", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
init_db()

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
:root{--ink:#1f2140;--muted:#5f5d78;--brand:#5745a5;--brand-d:#3e327f;--line:#e3e0f5;--soft:#f0edff;}
html,body,.stApp,[data-testid="stMarkdownContainer"],label,input,textarea,button{font-family:'DM Sans',sans-serif;}
.stApp{background:linear-gradient(135deg,#f6f5ff 0%,#f8fbff 60%,#f3f8ff 100%);color:var(--ink);}
h1,h2,h3,h4{font-family:Manrope,sans-serif!important;color:var(--ink);}
[data-testid="stHeader"]{background:transparent;} footer,#MainMenu{visibility:hidden;}
.block-container{padding-top:2rem;max-width:1180px;}
/* sidebar */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1f1946,#34266a);}
[data-testid="stSidebar"] :is(h1,h2,h3,p,label,span,div,li){color:#f3f0ff;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] *{color:#b9b2e6!important;}
[data-testid="stSidebar"] hr{border-color:#ffffff30;}
[data-testid="stSidebar"] [role="radiogroup"] label{padding:9px 12px;border-radius:10px;width:100%;margin-bottom:2px;}
[data-testid="stSidebar"] [role="radiogroup"] label:hover{background:#ffffff18;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#ffffff26;font-weight:700;}
[data-testid="stSidebar"] .stButton button{background:#ffffff1f;color:#fff;border:1px solid #ffffff40;}
[data-testid="stSidebar"] .stButton button:hover{background:#ffffff38;color:#fff;border-color:#fff;}
[data-testid="stSidebar"] .stButton button p{color:#fff!important;}
/* hero + cards */
.hero{padding:28px 32px;border-radius:22px;background:linear-gradient(115deg,#29205d,#5943a5 62%,#7565c9);margin-bottom:22px;box-shadow:0 14px 38px #3d2d8030;}
.hero h1{font-size:32px;font-weight:800;margin:0 0 6px;color:#fff!important;}
.hero p{color:#ece8ff!important;font-size:15px;margin:0;}
.panel,[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid var(--line)!important;border-radius:18px;box-shadow:0 6px 22px #30265d0d;}
.panel{padding:20px 22px;margin-bottom:14px;height:100%;}
.panel h3{margin:4px 0 8px;font-size:19px;} .panel p,.panel li{color:var(--muted);font-size:14px;line-height:1.55;}
.metric{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 20px;box-shadow:0 6px 22px #30265d0a;}
.metric .num{font-size:28px;font-weight:800;color:var(--brand-d);font-family:Manrope,sans-serif;}
.metric .lbl{font-size:12px;color:var(--muted);font-weight:700;text-transform:uppercase;letter-spacing:.7px;}
.metric .note{font-size:13px;color:var(--muted);}
.muted{color:var(--muted);font-size:13.5px;}
.tag{display:inline-block;background:var(--soft);color:#43348a;padding:4px 11px;border-radius:20px;margin:3px 4px 3px 0;font-size:12.5px;font-weight:600;}
.tag.ok{background:#e0f5e8;color:#14633a;} .tag.miss{background:#fff0d2;color:#7d4a00;}
.bar{margin:10px 0}.bar .t{display:flex;justify-content:space-between;font-size:13px;color:var(--ink);font-weight:600;margin-bottom:4px}
.bar .b{height:9px;background:#ece9fa;border-radius:9px;overflow:hidden}.bar .b i{display:block;height:100%;background:linear-gradient(90deg,#5745a5,#8a77e0);border-radius:9px}
.big{font-size:34px;font-weight:800;color:var(--brand-d);font-family:Manrope,sans-serif;line-height:1}
/* inputs */
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div{background:#fff!important;border:1px solid #cfc9ee!important;border-radius:10px!important;}
input,textarea{color:var(--ink)!important;-webkit-text-fill-color:var(--ink)!important;}
input::placeholder,textarea::placeholder{color:#8d8aa6!important;-webkit-text-fill-color:#8d8aa6!important;}
[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within{border-color:var(--brand)!important;box-shadow:0 0 0 2px #5745a533;}
label p,[data-testid="stWidgetLabel"] p{color:var(--ink)!important;font-weight:600;}
[data-testid="stForm"]{border:0;padding:0;background:transparent;}
[data-testid="stFileUploaderDropzone"]{background:#f6f4ff;border:1.5px dashed #a99be0;border-radius:14px;}
[data-testid="stFileUploaderDropzone"] *{color:var(--ink);}
[data-testid="stFileUploaderDropzone"] button{background:#fff;color:var(--brand);border:1px solid var(--brand);}
.stTabs [data-baseweb="tab"]{font-weight:600;color:var(--muted);} .stTabs [aria-selected="true"]{color:var(--brand);}
.main .stButton button,.main .stDownloadButton button{border-radius:11px;font-weight:700;padding:8px 18px;}
.main .stButton button[kind="secondary"],.main .stDownloadButton button{background:#fff;color:var(--brand);border:1.5px solid var(--brand);}
.main .stButton button[kind="secondary"]:hover,.main .stDownloadButton button:hover{background:var(--soft);color:var(--brand-d);}
.main .stButton button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind^="primary"]{background:var(--brand);color:#fff;border:0;}
.main .stButton button[kind="primary"]:hover{background:var(--brand-d);}
.main button[kind="primary"] p{color:#fff!important;}
</style>""", unsafe_allow_html=True)

def h(s): return re.sub(r"\n\s*", "", s)
def hero(t, sub): st.markdown(h(f'<div class="hero"><h1>{escape(t)}</h1><p>{escape(sub)}</p></div>'), unsafe_allow_html=True)
def metric(l, v, n=""): st.markdown(h(f'<div class="metric"><div class="lbl">{escape(str(l))}</div><div class="num">{escape(str(v))}</div><div class="note">{escape(n)}</div></div>'), unsafe_allow_html=True)
def tags(items, cls=""): return "".join(f'<span class="tag {cls}">{escape(str(i))}</span>' for i in items)
def bar(label, val, mx): return f'<div class="bar"><div class="t"><span>{escape(label)}</span><span>{val}/{mx}</span></div><div class="b"><i style="width:{val/mx*100:.0f}%"></i></div></div>'
def level(s): return "Strong" if s >= 70 else "Good start" if s >= 40 else "Needs work"
def go_to(p): st.session_state.nav = p
def fix_fig(fig, height=260):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#1f2140", family="DM Sans"), margin=dict(t=30, b=20, l=10, r=10))
    return fig

def logout():
    for k in ["user_id", "user_name", "nav", "analysis_result", "resume_text", "recommendations"]: st.session_state.pop(k, None)
    st.rerun()

def auth_screen():
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        st.markdown(h('''<div style="padding:50px 10px 10px 0">
        <div style="font-size:13px;font-weight:800;letter-spacing:2px;color:#5745a5">CAREERLENS AI</div>
        <h1 style="font-size:44px;line-height:1.12;margin:10px 0 14px">Your next career move starts here.</h1>
        <p style="font-size:17px;color:#5f5d78;line-height:1.6">Understand your resume, discover matching roles and build a clear path forward.</p>
        <div style="margin-top:24px"><span class="tag">AI Resume Insights</span><span class="tag">Smart Job Matching</span><span class="tag">Skill Gap Analysis</span></div></div>'''), unsafe_allow_html=True)
    with right:
        st.write("")
        with st.container(border=True):
            t1, t2 = st.tabs(["Sign in", "Create account"])
            with t1:
                st.subheader("Welcome back")
                with st.form("login_form"):
                    email = st.text_input("Email address", placeholder="you@example.com")
                    pw = st.text_input("Password", type="password")
                    ok = st.form_submit_button("Sign in", type="primary", use_container_width=True)
                if ok:
                    u = verify_user(email.strip().lower(), pw)
                    if u:
                        st.session_state.user_id, st.session_state.user_name, st.session_state.nav = u["id"], u["name"], "Overview"
                        st.rerun()
                    else: st.error("Email or password is incorrect.")
            with t2:
                st.subheader("Create your free account")
                with st.form("register_form"):
                    name = st.text_input("Full name")
                    e2 = st.text_input("Email address", key="reg_email")
                    p2 = st.text_input("Password", type="password", key="reg_pass", help="Use at least 8 characters.")
                    cf = st.text_input("Confirm password", type="password")
                    ok2 = st.form_submit_button("Create account", type="primary", use_container_width=True)
                if ok2:
                    if not name.strip() or not e2.strip() or not p2: st.error("Please complete all fields.")
                    elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", e2.strip()): st.error("Please enter a valid email address.")
                    elif len(p2) < 8: st.error("Password must contain at least 8 characters.")
                    elif p2 != cf: st.error("Passwords do not match.")
                    else:
                        done, msg = create_user(name.strip(), e2.strip().lower(), p2)
                        st.success("Account created. You can now sign in.") if done else st.error(msg)

if "user_id" not in st.session_state:
    auth_screen(); st.stop()
user = get_user(st.session_state.user_id)
if not user: logout()

PAGES = {"Overview": "🏠", "Resume Analyzer": "📄", "Job Recommendations": "🎯"}
st.session_state.setdefault("nav", "Overview")
with st.sidebar:
    st.markdown("## 🎯 CareerLens AI")
    st.caption("Your intelligent career companion")
    st.markdown("---")
    st.markdown(f"Hello, **{escape(user['name'])}** 👋")
    st.radio("Workspace", list(PAGES), key="nav", format_func=lambda p: f"{PAGES[p]}  {p}", label_visibility="collapsed")
    st.markdown("---")
    if st.button("Log out", use_container_width=True): logout()
page = st.session_state.nav
uid = st.session_state.user_id

if page == "Overview":
    hero(f"Welcome, {user['name'].split()[0]}!", "Upload your resume, understand your skills and explore suitable sample jobs.")
    analyses = get_analyses(uid)
    c = st.columns(3)
    with c[0]: metric("Resume analyses", len(analyses), "Completed analyses")
    with c[1]: metric("Latest score", f"{analyses[0]['readiness_score']}/100" if analyses else "—", level(analyses[0]['readiness_score']) if analyses else "No analysis yet")
    latest_jobs = json.loads(analyses[0]["jobs_json"]) if analyses else []
    with c[2]: metric("Best job match", f"{latest_jobs[0]['match_score']}%" if latest_jobs else "—", latest_jobs[0]["title"] if latest_jobs else "Analyze a resume")
    st.markdown("### Your career workflow")
    steps = [("01", "Analyze your resume", "Upload a PDF, DOCX or TXT file to find your skills and improvement areas.", "Resume Analyzer"),
             ("02", "Explore job matches", "See which sample jobs match your resume.", "Job Recommendations")]
    for col, (n, t, d, tgt) in zip(st.columns(2, gap="medium"), steps):
        with col:
            st.markdown(h(f'<div class="panel"><div style="color:#8a77e0;font-weight:800">{n}</div><h3>{t}</h3><p>{d}</p></div>'), unsafe_allow_html=True)
            st.button(f"Open {tgt}", key=f"go_{n}", on_click=go_to, args=(tgt,), use_container_width=True)
    if analyses:
        st.markdown("### Recent activity")
        st.dataframe(pd.DataFrame(analyses[:5])[["created_at", "file_name", "readiness_score"]].rename(columns={"created_at": "Date", "file_name": "Resume", "readiness_score": "Readiness score"}), use_container_width=True, hide_index=True)

elif page == "Resume Analyzer":
    hero("Resume Analyzer", "Turn your resume into clear, actionable career insights.")
    with st.container(border=True):
        uploaded = st.file_uploader("Upload your resume", type=["pdf", "docx", "txt"])
        use_sample = st.checkbox("Use the included sample resume instead")
        go_btn = st.button("Analyze resume", type="primary", use_container_width=True)
    if go_btn:
        try:
            raw, fname = "", ""
            if use_sample: raw, fname = (BASE / "data/sample_resume.txt").read_text(encoding="utf-8"), "sample_resume.txt"
            elif uploaded: raw, fname = extract_resume_text(uploaded), uploaded.name
            else: st.warning("Please upload a resume or select the sample resume.")
            if raw.strip():
                with st.spinner("Analyzing your resume..."):
                    res = analyze_resume(raw); jobs = recommend_jobs(raw, res["skills"], res)
                    save_analysis(uid, fname, res["readiness_score"], res, jobs)
                st.session_state.analysis_result, st.session_state.resume_text, st.session_state.recommendations = res, raw, jobs
                st.success("Resume analyzed and saved to your history.")
            elif fname: st.error("No readable text found. Scanned/image-only PDFs need OCR.")
        except Exception as e: st.error(f"Could not analyze this file: {e}")
    r = st.session_state.get("analysis_result")
    if r:
        jobs = st.session_state.get("recommendations", [])
        st.markdown("### Your resume snapshot")
        c = st.columns(3)
        with c[0]: metric("Readiness score", f"{r['readiness_score']}/100", level(r["readiness_score"]))
        with c[1]: metric("Skills detected", len(r["skills"]), "Recognized keywords")
        with c[2]: metric("Words detected", r["word_count"], "Extracted resume text")
        t1, t2, t3 = st.tabs(["Score", "Skills", "Improve & roadmap"])
        with t1:
            a, b = st.columns([1, 1], gap="large")
            with a:
                s = r["readiness_score"]
                fig = go.Figure(go.Indicator(mode="gauge+number", value=s, number={"suffix": "/100", "font": {"size": 38}},
                    gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#5745a5"},
                           "steps": [{"range": [0, 40], "color": "#fde4e4"}, {"range": [40, 70], "color": "#fff1d2"}, {"range": [70, 100], "color": "#dff4e6"}]}))
                st.plotly_chart(fix_fig(fig, 250), use_container_width=True)
            with b:
                st.markdown(h('<div class="panel"><h3>Resume readiness score</h3>' + "".join(bar(k, v, m) for k, (v, m) in r.get("breakdown", {}).items()) +
                    '<p>Sections found: ' + (tags(r["sections_present"]) or "none") + '</p>' +
                    '<p><b>How to read this:</b> This score checks resume completeness and evidence. It is separate from the job match percentage.</p></div>'), unsafe_allow_html=True)
        with t2:
            st.markdown(h('<div class="panel"><h3>Technical skills</h3>' + (tags(r.get("technical_skills", [])) or "No known technical skills detected.") +
                '<h3 style="margin-top:16px">Soft skills</h3>' + (tags(r.get("soft_skills", [])) or "No known soft skills detected.") + '</div>'), unsafe_allow_html=True)
            if r.get("skill_evidence"):
                st.markdown("#### Skill evidence (based on resume mentions)")
                evidence_rows = []
                for skill, info in r["skill_evidence"].items():
                    evidence_rows.append({
                        "Skill": skill.title(),
                        "Evidence level": info["level"],
                        "Mentions": info["mentions"],
                        "In projects": "Yes" if info["project_evidence"] else "No",
                        "In experience": "Yes" if info["experience_evidence"] else "No",
                    })
                st.dataframe(pd.DataFrame(evidence_rows), use_container_width=True, hide_index=True)
                st.caption("Evidence levels are estimates from resume text. They do not prove a person's actual proficiency.")
            have = set(r["skills"]); cats = list(CATEGORIES)
            got = [len([x for x in CATEGORIES[k] if x in have]) for k in cats]
            fig = go.Figure([go.Bar(y=cats, x=got, orientation="h", name="Detected", marker_color="#5745a5"),
                             go.Bar(y=cats, x=[len(CATEGORIES[k]) - g for k, g in zip(cats, got)], orientation="h", name="Not found", marker_color="#d9d4f3")])
            fig.update_layout(barmode="stack", legend=dict(orientation="h", y=1.15), yaxis=dict(autorange="reversed"))
            st.plotly_chart(fix_fig(fig, 280), use_container_width=True)
        with t3:
            st.markdown(h('<div class="panel"><h3>Suggestions</h3><ul>' + "".join(f"<li>{escape(t)}</li>" for t in r["suggestions"]) + '</ul></div>'), unsafe_allow_html=True)
            gap = {}
            for j in jobs[:5]:
                for m in j.get("missing", []): gap[m] = gap.get(m, 0) + 1
            top = [k for k, _ in sorted(gap.items(), key=lambda x: -x[1])[:6]]
            if top:
                st.markdown(h('<div class="panel"><h3>Learning roadmap</h3><p>Skills most often missing from your top matches:</p>' + tags(top, "miss") +
                    '<p><b>1.</b> Pick the first 2 skills and build one small project for each.<br><b>2.</b> Add the projects and measurable results to your resume.<br><b>3.</b> Re-run the analysis and compare your score in Analysis History.</p></div>'), unsafe_allow_html=True)
        st.download_button("⬇ Download analysis report", build_report(r, jobs), file_name="careerlens_resume_report.txt", mime="text/plain")

elif page == "Job Recommendations":
    hero("Job recommendations", "Search sample jobs that match your resume.")
    jobs = st.session_state.get("recommendations", [])
    if not jobs:
        st.info("Analyze a resume first to generate personalized job recommendations.")
        st.button("Go to Resume Analyzer", type="primary", on_click=go_to, args=("Resume Analyzer",))
    else:
        q = st.text_input("Search for a job", placeholder="e.g. Python Developer, Data Analyst, SQL")
        search_text = q.strip().lower()
        keep = [
            j for j in jobs
            if j.get("suitable", True)
            and (
                not search_text
                or search_text in (
                    j["title"] + " " + j["company"] + " " +
                    j["area"] + " " + " ".join(j["skills"])
                ).lower()
            )
        ]
        saved_ids = {str(s["id"]) for s in get_saved_jobs(uid)}
        if not keep:
            st.warning("Sorry! No jobs found matching your search. Try another job title or skill.")
        else:
            st.caption(f"{len(keep)} matching job(s) found. These are sample jobs from the project's dataset, not live vacancies.")
        for j in keep:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1.2])
                with c1:
                    st.markdown(h(f'<h3 style="margin:0">{escape(j["title"])}</h3><div class="muted">{escape(j["company"])} • {escape(j["area"])} • {escape(j["level"])}</div>'
                        f'<p style="margin:10px 0">{escape(j["description"])}</p>'
                        + ('<div class="muted">Technical skills you have</div>' + tags(j.get("technical_matched", []), "ok") if j.get("technical_matched") else "")
                        + ('<div class="muted">Technical skills to learn</div>' + tags(j.get("technical_missing", []), "miss") if j.get("technical_missing") else "")
                        + ('<div class="muted">Soft skills found</div>' + tags(j.get("soft_matched", []), "ok") if j.get("soft_matched") else "")
                        + ('<div class="muted">Soft skills not found</div>' + tags(j.get("soft_missing", []), "miss") if j.get("soft_missing") else "")
                        + f'<p class="muted"><b>{escape(j.get("recommendation", "Match"))}</b></p>'), unsafe_allow_html=True)
                    with st.expander("Why did this job get this score?"):
                        for factor, points in j.get("score_breakdown", {}).items():
                            maximum = j.get("score_breakdown_max", {}).get(factor, 0)
                            if maximum:
                                st.write(f"**{factor}:** {points}/{maximum}")
                                st.progress(min(1.0, points / maximum))
                        for reason in j.get("reasons", []):
                            st.caption("• " + reason)
                with c2:
                    st.markdown(f'<div class="muted">Match</div><div class="big">{j["match_score"]}%</div>', unsafe_allow_html=True)
                    st.progress(min(j["match_score"], 100) / 100)
                    if str(j["id"]) in saved_ids: st.button("✓ Saved", key=f"s_{j['id']}", disabled=True, use_container_width=True)
                    elif st.button("☆ Save job", key=f"s_{j['id']}", use_container_width=True):
                        save_job(uid, j); st.rerun()

elif page == "Saved Jobs":
    hero("Saved jobs", "Keep interesting roles together in one place.")
    saved = get_saved_jobs(uid)
    if not saved: st.info("You have not saved any jobs yet. Explore Job Recommendations to save roles.")
    for j in saved:
        with st.container(border=True):
            c1, c2 = st.columns([5, 1.2])
            with c1:
                st.markdown(h(f'<h3 style="margin:0">{escape(j["title"])}</h3><div class="muted">{escape(j["company"])} • {escape(j["area"])} • {escape(j["level"])}</div>'
                    f'<p style="margin:10px 0">{escape(j["description"])}</p>' + tags(j.get("skills", []))), unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="big">{j["match_score"]}%</div><div class="muted">match</div>', unsafe_allow_html=True)
                if st.button("Remove", key=f"del_{j['id']}", use_container_width=True):
                    delete_saved_job(uid, j["job_key"]); st.rerun()

elif page == "Analysis History":
    hero("Analysis history", "Review your previous resume checks.")
    hist = get_analyses(uid)
    if not hist: st.info("No analyses yet. Your completed reports will appear here.")
    else:
        df = pd.DataFrame(hist)
        st.dataframe(df[["created_at", "file_name", "readiness_score"]].rename(columns={"created_at": "Date", "file_name": "Resume", "readiness_score": "Score"}), use_container_width=True, hide_index=True)
        fig = go.Figure(go.Scatter(x=df["created_at"][::-1], y=df["readiness_score"][::-1], mode="lines+markers", line=dict(color="#5745a5", width=3)))
        fig.update_layout(title="Readiness score over time", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fix_fig(fig, 300), use_container_width=True)
        pick = st.selectbox("Open a report", hist, format_func=lambda a: f"{a['created_at']} — {a['file_name']} ({a['readiness_score']}/100)")
        r, jb = json.loads(pick["result_json"]), json.loads(pick["jobs_json"])
        with st.container(border=True):
            st.markdown(h('<h3 style="margin:0 0 8px">Report details</h3>' + tags(r["skills"]) + '<ul>' + "".join(f"<li>{escape(t)}</li>" for t in r["suggestions"]) + '</ul>'
                '<div class="muted">Top matches: ' + escape(", ".join(f"{j['title']} ({j['match_score']}%)" for j in jb[:3])) + '</div>'), unsafe_allow_html=True)
            st.download_button("⬇ Download this report", build_report(r, jb), file_name="careerlens_report.txt", mime="text/plain", key="dl_hist")
            if st.button("Delete this report"): delete_analysis(uid, pick["id"]); st.rerun()

elif page == "My Profile":
    hero("My profile", "Manage your account information.")
    with st.container(border=True):
        with st.form("profile_form"):
            name = st.text_input("Full name", value=user["name"])
            st.text_input("Email address", value=user["email"], disabled=True)
            goal = st.text_input("Career goal", value=user.get("career_goal", ""), placeholder="e.g. Data Analyst intern")
            bio = st.text_area("Short professional summary", value=user.get("bio", ""), height=120)
            sub = st.form_submit_button("Save profile", type="primary")
    if sub:
        if not name.strip(): st.error("Name cannot be empty.")
        else: update_profile(uid, name.strip(), goal.strip(), bio.strip()); st.success("Profile updated."); st.rerun()
    st.caption("Your account is private to this local application database.")

else:
    hero("About CareerLens AI", "An educational machine-learning project for resume understanding and job exploration.")
    st.markdown(h('''<div class="panel"><h3>How the system works</h3><ol>
    <li><b>Text extraction:</b> reads text from PDF, DOCX and TXT resumes.</li>
    <li><b>Skill detection:</b> finds known technical and professional skill keywords.</li>
    <li><b>Job matching:</b> technical skills, soft skills, preferred skills, project evidence, experience, education and TF-IDF text relevance produce an explainable score out of 100. Technical skills receive the larger share when both skill types are required.</li>
    <li><b>Skill gap:</b> compares your skills with each role to show what you have and what to learn.</li>
    <li><b>Persistence:</b> SQLite stores accounts, profile data, analysis history and saved jobs.</li></ol>
    <h3>Important limitations</h3><p>Job listings are illustrative sample data, not live vacancies. Match percentages are weighted evidence estimates, not hiring chances. The readiness score is a transparent heuristic, not a certified ATS score. Scanned PDFs may need OCR and keyword detection may miss synonyms.</p></div>'''), unsafe_allow_html=True)

import os
from pathlib import Path
import streamlit as st
from sqlalchemy.orm import Session
from app.main import (
    SessionLocal, User, Profile, Job, Application, pwd, profile_for,
    score_job, extract_text, DATA_DIR, UPLOAD_DIR
)

st.set_page_config(page_title="Job Search Assistance", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {font-family: Inter, sans-serif;}
.stApp {background: radial-gradient(circle at 12% 0%, #173c35 0%, #101820 38%, #0b1118 100%); color:#edf4f2;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#101c23,#0c131a); border-right:1px solid #263b3d;}
.block-container {padding-top:2rem; max-width:1280px;}
.hero {padding:30px 34px;border:1px solid #31574e;border-radius:24px;background:linear-gradient(120deg,rgba(23,74,61,.95),rgba(20,36,44,.94));box-shadow:0 20px 60px rgba(0,0,0,.25);margin-bottom:24px;}
.hero h1 {font-size:2.25rem;font-weight:800;letter-spacing:-1.2px;margin:0;color:#f5fbf8;}
.hero p {color:#b7cec5;margin:.5rem 0 0 0;font-size:1rem;}
.metric {background:linear-gradient(145deg,#182b31,#142128);border:1px solid #2b4848;border-radius:18px;padding:18px 20px;min-height:112px;}
.metric-label {color:#9eb9b1;font-size:.85rem;font-weight:600;}
.metric-value {font-size:2rem;font-weight:800;color:#f3faf7;margin-top:5px;}
.panel {background:rgba(20,33,40,.88);border:1px solid #294448;border-radius:18px;padding:20px 22px;margin:12px 0;}
.small-muted {color:#a8bbb8;font-size:.88rem;}
div.stButton > button {border-radius:11px;border:1px solid #3c7565;background:linear-gradient(120deg,#246b56,#1d5949);color:white;font-weight:650;min-height:42px;}
div.stButton > button:hover {border-color:#77c5a7;color:white;}
.stTextInput input,.stTextArea textarea,.stNumberInput input,.stSelectbox div[data-baseweb="select"] {background:#111e25;color:#edf4f2;border-radius:10px;}
hr {border-color:#294047;}
</style>
""", unsafe_allow_html=True)

STATUSES = ["Saved", "Preparing", "Applied", "Interview", "Rejected", "Offer", "Withdrawn"]

def db_session():
    return SessionLocal()

def set_user(user_id):
    st.session_state.user_id = user_id
    st.session_state.authenticated = True

def get_user(db):
    return db.query(User).filter(User.id == st.session_state.user_id).first()

def save_cv(db, user, uploaded):
    ext = Path(uploaded.name).suffix.lower()
    if ext not in [".pdf", ".docx", ".doc", ".txt"]:
        st.error("Please upload a PDF, DOCX, DOC or TXT file.")
        return
    content = uploaded.getvalue()
    if len(content) > 8 * 1024 * 1024:
        st.error("Maximum CV size is 8 MB.")
        return
    p = profile_for(db, user)
    if p.cv_filename:
        old = UPLOAD_DIR / p.cv_filename
        if old.exists(): old.unlink()
    filename = f"user_{user.id}_{os.urandom(8).hex()}{ext}"
    target = UPLOAD_DIR / filename
    target.write_bytes(content)
    p.cv_filename = filename
    p.cv_text = extract_text(target)
    db.commit()
    st.success(f"CV saved privately to your account. Extracted {len(p.cv_text or '')} characters.")

def auth_screen():
    st.markdown('<div class="hero"><h1>Job Search Assistance</h1><p>Your career search workspace. Build your profile, discover relevant roles and manage applications.</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown('<div class="panel"><h3>Welcome back</h3><p class="small-muted">Sign in to access your private job-search workspace.</p></div>', unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Sign in", use_container_width=True)
            if submitted:
                with db_session() as db:
                    user = db.query(User).filter(User.email == email.strip().lower()).first()
                    if user and pwd.verify(password, user.password_hash):
                        set_user(user.id); st.rerun()
                    else: st.error("Email or password is incorrect.")
    with right:
        st.markdown('<div class="panel"><h3>Create your account</h3><p class="small-muted">Your profile, CV and applications are separated from other users.</p></div>', unsafe_allow_html=True)
        with st.form("register_form"):
            name = st.text_input("Full name")
            new_email = st.text_input("Email address")
            new_password = st.text_input("Password (at least 10 characters)", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)
            if submitted:
                if len(new_password) < 10: st.error("Use a password with at least 10 characters.")
                elif new_password != confirm: st.error("Passwords do not match.")
                elif "@" not in new_email: st.error("Enter a valid email address.")
                else:
                    with db_session() as db:
                        if db.query(User).filter(User.email == new_email.strip().lower()).first(): st.error("An account with this email already exists.")
                        else:
                            user = User(email=new_email.strip().lower(), name=name.strip(), password_hash=pwd.hash(new_password))
                            db.add(user); db.commit(); db.refresh(user)
                            p = profile_for(db, user); p.countries = "Worldwide"; p.min_match = 81; db.commit()
                            set_user(user.id); st.success("Account created."); st.rerun()

def main_app():
    with db_session() as db:
        user = get_user(db)
        if not user:
            st.session_state.clear(); st.rerun()
        p = profile_for(db, user)
        with st.sidebar:
            st.markdown("## 🎯 Job Search Assistance")
            st.caption(f"Signed in as {user.email}")
            page = st.radio("Workspace", ["Overview", "Find Jobs", "My Applications", "My Profile", "Settings"], label_visibility="collapsed")
            st.divider()
            if st.button("Sign out", use_container_width=True):
                st.session_state.clear(); st.rerun()
        st.markdown(f'<div class="hero"><h1>{page}</h1><p>Welcome{", " + user.name if user.name else ""}. Your career search, organized in one place.</p></div>', unsafe_allow_html=True)

        if page == "Overview":
            jobs = db.query(Job).all()
            apps = db.query(Application).filter(Application.user_id == user.id).all()
            scores = [score_job(p, j) for j in jobs]
            threshold = p.min_match or 81
            readiness = sum(bool(getattr(p, k)) for k in ["headline", "skills", "experience", "education", "languages", "cv_text"]) * 100 // 6
            cols = st.columns(4)
            metrics = [("Jobs in workspace", len(jobs)), ("Strong matches", sum(x >= threshold for x in scores)), ("Applications", len(apps)), ("Profile readiness", f"{readiness}%")]
            for col, (label, value) in zip(cols, metrics):
                with col: st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)
            st.markdown("### Your next steps")
            c1,c2 = st.columns(2)
            with c1:
                st.markdown('<div class="panel"><h4>Complete your career profile</h4><p class="small-muted">Add skills, experience and your CV to improve matching quality.</p></div>', unsafe_allow_html=True)
                if st.button("Update profile", key="go_profile"): st.session_state.nav_override = "My Profile"; st.rerun()
            with c2:
                st.markdown('<div class="panel"><h4>Add job opportunities</h4><p class="small-muted">Add a vacancy manually. Live job-board discovery is not connected in this MVP.</p></div>', unsafe_allow_html=True)
                if st.button("Explore jobs", key="go_jobs"): st.session_state.nav_override = "Find Jobs"; st.rerun()
            st.info("Matching is a transparent keyword-based estimate, not a guarantee of suitability. Only roles scoring at least your selected threshold are highlighted.")

        elif page == "My Profile":
            with st.form("profile_form"):
                headline = st.text_input("Professional headline", p.headline or "")
                skills = st.text_area("Skills (comma-separated)", p.skills or "", height=100)
                experience = st.text_area("Professional experience", p.experience or "", height=130)
                education = st.text_area("Education", p.education or "", height=90)
                languages = st.text_input("Languages", p.languages or "")
                industries = st.text_input("Industries", p.industries or "")
                roles = st.text_input("Preferred job titles", p.preferred_roles or "")
                countries = st.text_input("Countries", p.countries or "Worldwide", help="Enter Worldwide or specific countries.")
                locations = st.text_input("Preferred cities / regions", p.locations or "")
                work_mode = st.selectbox("Work mode", ["Any", "Remote", "Hybrid", "On-site"], index=["Any", "Remote", "Hybrid", "On-site"].index(p.work_mode if p.work_mode in ["Any", "Remote", "Hybrid", "On-site"] else "Any"))
                employment = st.selectbox("Employment type", ["Any", "Full-time", "Part-time", "Contract", "Temporary", "Internship"], index=["Any", "Full-time", "Part-time", "Contract", "Temporary", "Internship"].index(p.employment_type if p.employment_type in ["Any", "Full-time", "Part-time", "Contract", "Temporary", "Internship"] else "Any"))
                salary = st.number_input("Minimum annual salary (0 = no minimum)", min_value=0, value=int(p.salary_min or 0), step=1000)
                threshold = st.slider("Minimum job-match score", 50, 99, int(p.min_match or 81))
                save = st.form_submit_button("Save profile", use_container_width=True)
                if save:
                    p.headline=headline; p.skills=skills; p.experience=experience; p.education=education; p.languages=languages; p.industries=industries; p.preferred_roles=roles; p.countries=countries; p.locations=locations; p.work_mode=work_mode; p.employment_type=employment; p.salary_min=salary or None; p.min_match=threshold; db.commit(); st.success("Profile updated.")
            st.markdown("### Your CV")
            uploaded = st.file_uploader("Upload CV (PDF, DOCX, DOC or TXT; maximum 8 MB)", type=["pdf", "docx", "doc", "txt"])
            if uploaded and st.button("Save CV", use_container_width=False): save_cv(db, user, uploaded)
            if p.cv_filename:
                st.success(f"CV stored in your account: {p.cv_filename}")
                if st.button("Delete my CV"):
                    f=UPLOAD_DIR/p.cv_filename
                    if f.exists(): f.unlink()
                    p.cv_filename=""; p.cv_text=""; db.commit(); st.rerun()

        elif page == "Find Jobs":
            st.markdown("### Add a vacancy")
            with st.form("job_form", clear_on_submit=True):
                a,b = st.columns(2)
                with a: title=st.text_input("Job title *"); company=st.text_input("Company"); location=st.text_input("Location"); country=st.text_input("Country")
                with b: mode=st.selectbox("Work mode", ["Unknown","Remote","Hybrid","On-site"]); employment=st.selectbox("Employment type", ["", "Full-time","Part-time","Contract","Temporary"]); url=st.text_input("Vacancy URL")
                description=st.text_area("Job description", height=120); requirements=st.text_area("Requirements", height=100)
                add=st.form_submit_button("Add job", use_container_width=True)
                if add:
                    if not title.strip(): st.error("Job title is required.")
                    else:
                        job=Job(title=title.strip(),company=company.strip() or "Unknown employer",location=location,country=country,work_mode=mode,employment_type=employment,description=description,requirements=requirements,url=url,source="Manual")
                        db.add(job); db.commit(); st.success("Vacancy added to the shared job catalogue."); st.rerun()
            st.divider()
            query=st.text_input("Search saved vacancies", placeholder="Search title, company, location or description")
            jobs=db.query(Job).order_by(Job.created_at.desc()).all()
            rows=[]
            for j in jobs:
                if query.lower() not in (j.title+" "+j.company+" "+j.location+" "+j.description).lower(): continue
                score=score_job(p,j)
                if score >= (p.min_match or 81): rows.append((score,j))
            rows.sort(key=lambda x:x[0],reverse=True)
            st.caption(f"Showing {len(rows)} vacancies at or above your {p.min_match or 81}% match threshold. Add vacancies manually; live job-board integrations are not enabled yet.")
            for score,j in rows:
                with st.container(border=True):
                    left,right=st.columns([5,1])
                    with left:
                        st.markdown(f"#### {j.title}  ·  **{score:.0f}% match**")
                        st.write(f"{j.company}  |  {j.location}  |  {j.country}  |  {j.work_mode}")
                        st.write((j.description or j.requirements or "No description provided")[:600])
                        if j.url: st.markdown(f"[Open vacancy]({j.url})")
                    with right:
                        already=db.query(Application).filter(Application.user_id==user.id,Application.job_id==j.id).first()
                        if already: st.caption("Already saved")
                        elif st.button("Save job",key=f"save_{j.id}"):
                            db.add(Application(user_id=user.id,job_id=j.id,status="Saved"));db.commit();st.success("Saved.");st.rerun()
            if not rows: st.info("No vacancies meet your threshold yet. Add job descriptions and complete your profile to calculate matches.")

        elif page == "My Applications":
            apps=db.query(Application).filter(Application.user_id==user.id).order_by(Application.created_at.desc()).all()
            if not apps: st.info("You have not saved any jobs yet.")
            for a in apps:
                with st.container(border=True):
                    st.markdown(f"#### {a.job.title} — {a.job.company}")
                    st.caption(f"{a.job.location} · Added {a.created_at.strftime('%d %b %Y')}")
                    if a.job.url: st.markdown(f"[Open vacancy]({a.job.url})")
                    new_status=st.selectbox("Status",STATUSES,index=STATUSES.index(a.status) if a.status in STATUSES else 0,key=f"status_{a.id}")
                    notes=st.text_area("Notes",a.notes or "",key=f"notes_{a.id}",height=70)
                    x,y=st.columns(2)
                    with x:
                        if st.button("Save changes",key=f"update_{a.id}"):
                            a.status=new_status;a.notes=notes;db.commit();st.success("Updated.");st.rerun()
                    with y:
                        if st.button("Generate cover letter",key=f"letter_{a.id}"):
                            name=user.name or "Candidate"; skills=p.skills or "relevant professional skills"; exp=p.experience or "my professional experience"
                            a.cover_letter=f"Dear Hiring Team,\n\nI am writing to express my interest in the {a.job.title} position at {a.job.company}. My background includes {exp}. I can bring strengths in {skills}, and I am interested in applying these capabilities to the responsibilities described in your vacancy.\n\nI would welcome the opportunity to discuss how my experience and approach could contribute to your team. Thank you for your time and consideration.\n\nKind regards,\n{name}"
                            db.commit();st.rerun()
                    if a.cover_letter:
                        st.text_area("Cover letter draft",a.cover_letter,height=220,key=f"lettertext_{a.id}")

        elif page == "Settings":
            st.markdown("### Account settings")
            st.write(f"Account email: **{user.email}**")
            st.warning("Deleting your account permanently deletes your profile, CV file and application records from this app's database.")
            confirm=st.checkbox("I understand that this action cannot be undone.")
            if st.button("Delete my account",disabled=not confirm):
                if p.cv_filename:
                    f=UPLOAD_DIR/p.cv_filename
                    if f.exists(): f.unlink()
                db.query(Application).filter(Application.user_id==user.id).delete()
                db.delete(p);db.delete(user);db.commit();st.session_state.clear();st.success("Account deleted.");st.rerun()

if "authenticated" not in st.session_state: st.session_state.authenticated=False
if not st.session_state.authenticated: auth_screen()
else: main_app()

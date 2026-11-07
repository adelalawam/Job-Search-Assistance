# Job Search Assistance — Streamlit edition

This is a Streamlit conversion of the original FastAPI MVP for deployment on Streamlit Community Cloud.

## Deploy on Streamlit Community Cloud

1. Upload the contents of this folder to a GitHub repository (root level, not nested in another folder).
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Choose **Create app** → **Yup, I have an app**.
4. Select your repository and branch `main`.
5. Set **Main file path** to `streamlit_app.py`.
6. Click **Deploy**.

## Included

- Per-user registration and login with hashed passwords.
- Individual profiles and CV uploads (PDF, DOCX, DOC, TXT).
- Manual job vacancy catalogue.
- Keyword-based job matching and configurable threshold (default 81%).
- Application tracking and cover-letter draft generation.
- Account deletion.

## Important limitations

This is a prototype/MVP, not a production-ready commercial recruitment platform. Streamlit Community Cloud is free but resource-limited and apps hibernate after inactivity. The local SQLite database and uploaded CV files in this prototype are stored on the app's local filesystem. Do **not** use real users' sensitive CVs or rely on this storage for permanent records until you connect a managed persistent database and private object storage with backups and access controls. Streamlit Community Cloud's local filesystem should not be treated as durable storage.

The app does not yet discover live jobs automatically, use semantic AI matching, or submit applications automatically. Job vacancies are entered manually. The match score is a keyword heuristic and is not a guarantee of suitability.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

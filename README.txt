JOB SEARCH ASSISTANCE — ORIGINAL DESIGN RESTORE

This package restores the original premium dark Job Search Assistance interface
inside Streamlit. It includes the exact original design.html, including the
animated 3D orb/rings, navigation, cards, typography, and responsive CSS.

DEPLOYMENT FILES
- streamlit_app.py
- requirements.txt
- runtime.txt
- design.html
- .streamlit/config.toml

IMPORTANT
This package restores the original visual design. The original HTML is a
front-end prototype: its forms and buttons display preview interactions only.
It does not provide working multi-user authentication, persistent CV storage,
live job feeds, or automatic applications. Those backend capabilities must
be integrated separately before accepting real users or CVs.

PYTHON VERSION
runtime.txt pins Python 3.12 to avoid the Python 3.14 / pydantic-core build
failure shown in the previous deployment logs. This package removes FastAPI
and Pydantic from Streamlit's dependency installation.

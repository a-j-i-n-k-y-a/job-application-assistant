# Job Application Assistant

An AI-powered tool that analyzes your resume against a job description and returns a fit score, skill gaps, strengths, and a tailored cover letter.

## What it does
- Parses your resume PDF
- Compares it against any job description using Gemini AI
- Returns fit score (0-100), gaps, strengths, and cover letter
- Logs every application to a local database

## Tech Stack
- FastAPI
- Google Gemini API
- PyMuPDF (PDF parsing)
- SQLite
- Streamlit

## How to run
1. Clone the repo
2. Create a `.env` file with your `GOOGLE_API_KEY`
3. Install dependencies: `pip install -r requirements.txt`
4. Start backend: `uvicorn main:app --reload`
5. Start frontend: `streamlit run app.py`

## Endpoints
- `GET /hello` — health check
- `POST /analyze` — analyze resume vs JD
- `GET /history` — view past applications
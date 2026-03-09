from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv
import os
from google import genai
import fitz
import sqlite3
import datetime


load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

# Function for extracting text from resume
def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text= ""

    for page in doc:
        text += page.get_text()
    
    return text

# creating database
def init_db():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   company_name TEXT,
                   job_title TEXT,
                   fit_score INTEGER,
                   timestamp TEXT
                    )
    """)
    conn.commit()
    conn.close()

# logging each entry
def log_application(company_name : str, job_title : str, fit_score : int):
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO applications (company_name, job_title, fit_score, timestamp) VALUES (?, ?, ?, ?)",
                    (company_name, job_title, fit_score, datetime.datetime.now().isoformat()))
    conn.commit()
    conn.close()


init_db()

# Hello Endpoint just to test the Gemini API call
@app.get("/hello")
def hello():
    response = client.models.generate_content( model="gemini-2.5-flash", contents="Say Hi to Selena" )
    return {"message" : response.text}



# Resume + JD matching 
@app.post("/analyze")

async def analyze(resume : UploadFile = File(...), job_description : str = Form(...)):
    # 1. Read the File
    resume_bytes = await resume.read()
    resume_text = extract_text_from_pdf(resume_bytes)

    # 2. The Prompt
    prompt = f""" You are an expert recruiter and career coach.
            Given the resume and job description below, provide:
            1. Fit Score (0-100) with one line explanation
            2. Top 3 gaps between the resume and job requirements
            3. Strength the Candidate has respective the role
            4. A tailored cover letter (max 200 words)

            Resume:
            {resume_text}

            Job Description:
            {job_description}

            Respond in this exact format:
            COMPANY NAME: <name>

            FIT SCORE: <score>/100 - <one line reason>

            Job Title :
            < Relevant Job Title >

            GAPS:
            - <gap 1>
            - <gap 2>
            - <gap 3>

            STRENGTH:
            <Strengths here>

            COVER LETTER:
            <cover letter here> """
    
    # 3. Call gemini, give it the text, prompt
    response = client.models.generate_content(model = "gemini-2.5-flash", contents=prompt)

    # 4. Logging to DB
    lines = response.text.split("\n")

    # Find the line that starts with what you need
    company_line = next((l for l in lines if l.startswith("COMPANY NAME:")), None)
    score_line = next((l for l in lines if l.startswith("FIT SCORE:")), None)

    company_name = company_line.split(": ")[1].strip() if company_line else "Unknown"
    fit_score = int(score_line.split(": ")[1].split("/")[0].strip()) if score_line else 0

    log_application(company_name, job_description[:50], fit_score)

    return {"result" : response.text}


@app.get("/history")
def history():
    conn = sqlite3.connect("applications.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        results.append({
            "id" : row[0],
            "company name" : row[1],
            "job description" : row[2],
            "fit_score" : row[3],
            "timestamp" : row[4]
        })

    return {"applications" : results}



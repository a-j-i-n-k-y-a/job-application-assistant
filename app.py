import streamlit as st
import requests

st.title("Job Application Assistant")
st.write("Upload your resume and paste a job description to get your fit score, gaps, and a cover letter.")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
job_description = st.text_area("Paste your Job Description here")

if st.button("Analyze"):
    if not resume_file or not job_description:
        st.warning("Please upload a resume and Paste the Job Description")
    else:
        with st.spinner("Analyzing..."):
            response = requests.post(
                "http://localhost:8000/analyze",
                files={"resume" : resume_file},
                data={"job_description" : job_description}
            )
            result = response.json()["result"]
            st.markdown(result)
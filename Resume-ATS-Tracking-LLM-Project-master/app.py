import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json

# ✅ Configure Gemini API
genai.configure(api_key="AIzaSyAIEQ11AOp-x0CKdqD5LiBzz6aQGq2qOoQ")
model = genai.GenerativeModel("gemini-2.5-pro")

# ✅ Extract PDF Text
def extract_text_from_pdf(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    return "".join(page.extract_text() for page in reader.pages if page.extract_text())

# ✅ Improved Gemini Prompt for Better Accuracy
def get_gemini_feedback(resume_text, jd):
    prompt = f"""
You are an intelligent ATS (Applicant Tracking System) evaluator. Your task is to match a resume with a job description and return structured feedback.

Respond ONLY with a valid JSON in this exact format:
{{
  "JD Match": "percentage match of resume to JD (e.g., 85%)",
  "MissingKeywords": ["list of keywords or skills missing in the resume"],
  "Profile Summary": "1-2 sentence summary of the candidate’s suitability for the role"
}}

Guidelines:
- Do NOT include any explanation or markdown.
- Only return valid JSON.
- Focus on key technical and role-specific skills.
- Compare resume content strictly against job description.
- Make sure to be accurate and objective.

Resume:
\"\"\"
{resume_text}
\"\"\"

Job Description:
\"\"\"
{jd}
\"\"\"
"""
    try:
        response = model.generate_content(prompt).text.strip()
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        feedback = json.loads(response[json_start:json_end])
        return feedback
    except Exception as e:
        return {"error": str(e), "raw_output": response}

# ✅ Streamlit UI Setup
st.set_page_config(page_title="Smart ATS – Resume Evaluator", layout="centered")
st.title("💼 Smart ATS – Multi-Resume Evaluator")
st.markdown("Upload one or more resumes and evaluate them against a job description using Gemini AI.")

# ✅ Job Description Input
jd = st.text_area("📋 Paste the Job Description", height=200)

# ✅ Resume Upload
uploaded_files = st.file_uploader("📄 Upload One or More Resumes (PDF)", type="pdf", accept_multiple_files=True)

# ✅ On Submit
if st.button("🚀 Submit"):
    if uploaded_files and jd.strip():
        for uploaded_file in uploaded_files:
            with st.spinner(f"Evaluating {uploaded_file.name}..."):
                resume_text = extract_text_from_pdf(uploaded_file)
                feedback = get_gemini_feedback(resume_text, jd)

            st.subheader(f"🧠 Feedback for: {uploaded_file.name}")

            if "error" in feedback:
                st.error("⚠ Gemini could not parse the response:")
                st.code(feedback["raw_output"])
            else:
                # ✅ ONLY text color enhancement (no layout change)
                keywords_html = "".join(f"<li>{kw}</li>" for kw in feedback["MissingKeywords"])
                st.markdown(
                    f"""
                    <div style="background-color:#f5f7fa;padding:20px;border-radius:12px;border:1px solid #ccc;">
                        <h3 style="color:#007acc;">✨ Gemini Feedback</h3>
                        <p style="color:#333;font-size:16px;">
                            <strong style="color:#000;">✅ JD Match:</strong> 
                            <span style="color:#228B22;">{feedback['JD Match']}</span>
                        </p>
                        <p style="color:#333;font-size:16px;">
                            <strong style="color:#000;">🚫 Missing Keywords:</strong>
                        </p>
                        <ul style="color:#cc0000;font-size:16px;">
                            {keywords_html}
                        </ul>
                        <p style="color:#333;font-size:16px;">
                            <strong style="color:#000;">📝 Profile Summary:</strong><br>
                            {feedback['Profile Summary']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.warning("⚠ Please upload at least one resume and paste a job description.")

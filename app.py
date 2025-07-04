# app.py

import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import streamlit.components.v1 as components
import tempfile

from chains import Chain
from utils import clean_text, pdf_text_extractor, text_fields, text_to_pdf_bytes
from langchain_community.document_loaders import WebBaseLoader

# ✅ Set USER_AGENT to avoid warning
if not os.environ.get("USER_AGENT"):
    os.environ["USER_AGENT"] = "SkillMatcherBot/1.0 (+https://yourprojectsite.com)"


def create_streamlit_app(llm):
    st.set_page_config(layout="wide", page_title="Skills Matcher and Cover Letter Generator", page_icon="📑")
    st.title("📄 Skill Matcher and Cover Letter Generator")

    url_input = st.text_input("Enter Job URL:", value="https://www.amazon.jobs/en/jobs/2890079/software-dev-engineer-i-amazon-university-talent-acquisition")
    if not url_input:
        st.warning("Please enter a job posting URL.")

    col1, col2 = st.columns([4, 1])

    with col1:
        pdf_file = st.file_uploader("Upload Resume (PDF)", type=('pdf'))

    # Initialize session state for PDF viewer toggle
    if 'show_pdf' not in st.session_state:
        st.session_state['show_pdf'] = False

    with col2:
        if st.button("View PDF"):
            st.session_state['show_pdf'] = True
        if st.button("Close PDF"):
            st.session_state['show_pdf'] = False

    # ✅ View uploaded PDF if toggled
    if st.session_state['show_pdf'] and pdf_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_file_path = tmp_file.name

        st.subheader("📑 Uploaded Resume Preview")
        try:
            html_code = pdf_viewer(input=tmp_file_path, width=700)
            if html_code:
                components.html(html_code, height=600, scrolling=True)
        except Exception as e:
            st.error(f"Error rendering PDF: {e}")

    submit_button = st.button("Check Match")
    output = None

    # ✅ Check Match button logic
    if submit_button and pdf_file is not None:
        try:
            loader = WebBaseLoader([url_input])
            data = loader.load()
            cleaned_text = clean_text(data[0].page_content)
            jobs = llm.extract_jobs(cleaned_text)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(pdf_file.read())
                resume_content = pdf_text_extractor(tmp_file.name)

            match = llm.write_match(jobs, resume_content)
            output = text_fields(match)

            # ✅ Save to session_state for cover letter generation
            st.session_state['jobs'] = jobs
            st.session_state['resume_content'] = resume_content

        except Exception as e:
            st.error(f"An error occurred: {e}")

    # ✅ Display matching results if output available
    if output:
        st.text_area("Job Matching Score:", value=output.get('match_score', 'N/A'), height=100)
        col3, col4 = st.columns(2)

        with col3:
            st.text_area("Job Required Skills:", value="\n".join(output.get('required_skills', [])), height=200)
        with col4:
            st.text_area("Your Skills:", value="\n".join(output.get('your_skills', [])), height=200)

        st.text_area("Matching Skills:", value="\n".join(output.get('matching_skills', [])), height=150)
        st.text_area("Focus/Improve Skills:", value="\n".join(output.get('focus_skills', [])), height=150)

    # ✅ Cover letter generation
    if st.button("Generate Cover Letter"):
        if 'jobs' in st.session_state and 'resume_content' in st.session_state:
            try:
                cover_letter_text = llm.cover_letter(st.session_state['jobs'], st.session_state['resume_content'])
                st.session_state['cover_letter_text'] = cover_letter_text
            except Exception as e:
                st.error(f"An error occurred while generating cover letter: {e}")
        else:
            st.warning("Please run 'Check Match' first to load job description and resume.")

    # ✅ Display and download cover letter if available in session state
    if 'cover_letter_text' in st.session_state:
        st.text_area("Generated Cover Letter:", st.session_state['cover_letter_text'], height=500)

        if st.button("Download as PDF"):
            pdf_bytes = text_to_pdf_bytes(st.session_state['cover_letter_text'])
            st.download_button("📥 Click to Download PDF", data=pdf_bytes, file_name="cover_letter.pdf", mime="application/pdf")


if __name__ == "__main__":
    chain = Chain()
    create_streamlit_app(chain)

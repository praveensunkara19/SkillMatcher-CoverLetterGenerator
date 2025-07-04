# utils.py

import re
from langchain_community.document_loaders import PyPDFLoader
from fpdf import FPDF
from io import BytesIO

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)

    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

    # Remove special characters (keep only alphanumeric and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)

    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)

    # Trim leading and trailing whitespace
    text = text.strip()

    return text

def pdf_text_extractor(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()  
    
    resume_content = ""
    for page in pages:
        resume_content += page.page_content + '\n'
        
    return resume_content

    # all text_to_pdf_bytes code should be here
def text_to_pdf_bytes(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    return BytesIO(pdf_bytes)


def text_fields(output_text):

    match_score = re.search(r"\*\*Matching score\*\*: (.+?)\n", output_text).group(1).strip()

    required_skills = re.search(r"\*\*Required skills\*\*:[\s\S]*?\*\*Your skills", output_text).group(0)
    required_skills = re.findall(r"- (.+)", required_skills)

    your_skills = re.search(r"\*\*Your skills\*\*:[\s\S]*?\*\*Matching skills", output_text).group(0)
    your_skills = re.findall(r"- (.+)", your_skills)

    matching_skills = re.search(r"\*\*Matching skills\*\*:[\s\S]*?\*\*Focus/improve skills", output_text).group(0)
    matching_skills = re.findall(r"- (.+)", matching_skills)

    focus_skills = re.search(r"\*\*Focus/improve skills\*\*:([\s\S]*)", output_text).group(1)
    focus_skills = re.findall(r"- (.+)", focus_skills)

    return {
        "match_score": match_score,
        "required_skills": required_skills,
        "your_skills": your_skills,
        "matching_skills": matching_skills,
        "focus_skills": focus_skills
    }

# chains.py

import os
import json
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
         self.llm = ChatGroq(
            groq_api_key=os.getenv('GROQ_API_KEY'),
            model="llama-3.3-70b-versatile",
            temperature=0
         )

    def extract_jobs(self,clean_text):
        prompt_extract = PromptTemplate.from_template(
                """
                ### SCRAPED TEXT FROM WEBSITE
                {page_data}
                ### INSTRUCTION
                The scraped test is from the carrer's page of website.
                Your job is to extract the job posting and return them in JSON format contain the 
                following keys : 'company','role','experience','skills',and 'description'.
                Only return the valid JSON.
                ### VALID JSON (NO PREAMBLE):
                """
            )
        chain_extract = prompt_extract | self.llm
        try:
            respose = chain_extract.invoke({"page_data":clean_text})
            json_parser = JsonOutputParser()
            job_description = json_parser.parse(respose.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parser job(llm token limit:10000)")
        return job_description if isinstance(job_description,list) else [job_description]
    
    def write_match(self,job_description,resume_content):
        prompt_match = PromptTemplate.from_template(
    
            """
            ### RESUME DESCRIPTION
            {resume}
            As a smart skills checker compare the skills,experience,and all required description that allign the {job_description}.
            Analyse and give the view  wiht 'Maching score', 'Required skills', 'Your skills', 'Matching skills' and 'focus/improve skills' concise and on to poin.
            Do not provide preamble 
            ### Response (NO PREAMBEL):
            """
        )

        chain_match = prompt_match | self.llm
        response = chain_match.invoke({"job_description":str(job_description),"resume": str(resume_content)})
        return response.content
    
    def cover_letter(self,job_description,resume_content):
        prompt_coverletter = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### RESUME:
            {resume}

            You are a professional cover letter writer.

            Write a **professional, impactful, and concise cover letter** tailored for the above job. Follow these strict instructions:

            - Limit to **3 short paragraphs only**:
            1. Brief greeting with mention of hiring manager and company name, and motivation for applying.
            2. Summarise **only key skills and experiences relevant to the job** in clear bullet-like sentences if needed.
            3. Closing with gratitude and clear applicant contact details in a single line at the end.

            add a line that supports the your skills and company requirements.

            - Keep it **strictly within a single document page**, avoiding long sentences or redundant phrases.
            - Use a formal yet crisp tone to convey motivation, alignment, and impact effectively.

            At the end, mention:

            Name:[Your Full Name]
            Phone:[Your Phone]
            Email:[Your Email]

            ### Cover Letter:

            """
        )

        chain_coverletter = prompt_coverletter | self.llm
        coverletter = chain_coverletter.invoke({
            "job_description": job_description,
            "resume": resume_content
        })

        return coverletter.content


if __name__ == "__main__":
    chain = Chain()
    print("Chain initialized successfully.")

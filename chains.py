# import os
# from langchain_groq import ChatGroq
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import JsonOutputParser
# from langchain_core.exceptions import OutputParserException
# from dotenv import load_dotenv

# load_dotenv()

# class Chain:
#     def __init__(self):
#         self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

#     def extract_jobs(self, cleaned_text):
#         prompt_extract = PromptTemplate.from_template(
#             """
#             ### SCRAPED TEXT FROM WEBSITE:
#             {page_data}
#             ### INSTRUCTION:
#             The scraped text is from a career's page of a website.
#             Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
#             Only return the valid JSON.
#             ### VALID JSON (NO PREAMBLE):
#             """
#         )
#         chain_extract = prompt_extract | self.llm
#         res = chain_extract.invoke(input={"page_data": cleaned_text})
        
#         try:
#             json_parser = JsonOutputParser()
#             res = json_parser.parse(res.content)
#         except OutputParserException:
#             raise OutputParserException("Context too big. Unable to parse jobs.")
        
#         return res if isinstance(res, list) else [res]

#     def write_letter(self, job, links):
#         prompt_cover_letter = PromptTemplate.from_template(
#             """
#             ### JOB DESCRIPTION:
#             {job_description}
            
#             ### INSTRUCTION:
#             You are a job applicant seeking a position related to the job mentioned above. 
#             Your task is to write a compelling and personalized cover letter that highlights your relevant skills, experience, 
#             and how you can contribute to the company. 

#             Ensure the cover letter is:
#             - Professionally structured
#             - Tailored to the specific job description
#             - Showcases relevant skills and achievements
#             - Engaging and concise
            
#             Include references to the most relevant experiences, projects, or achievements that align with the job description.
            
#             ### COVER LETTER (NO PREAMBLE):
#             """
#         )
#         chain_cover_letter = prompt_cover_letter | self.llm
#         res = chain_cover_letter.invoke({"job_description": str(job)})
#         return res.content

#     def write_resume(self, job):
#         prompt_resume = PromptTemplate.from_template(
#             """
#             ### JOB DESCRIPTION:
#             {job_description}
            
#             ### INSTRUCTION:
#             You are creating a **tailored resume** for the above job description. 
#             The resume should be:
#             - **ATS-friendly** (Applicant Tracking System compliant)
#             - **Well-formatted** with proper sections like Summary, Skills, Experience, and Education
#             - **Optimized** to match the keywords from the job description
            
#             Ensure the resume is clean, concise, and follows professional standards.

#             ### RESUME (NO PREAMBLE):
#             """
#         )
#         chain_resume = prompt_resume | self.llm
#         res = chain_resume.invoke({"job_description": str(job)})
#         return res.content

#     def write_cold_email(self, job, links):
#         prompt_cold_email = PromptTemplate.from_template(
#             """
#             ### JOB DESCRIPTION:
#             {job_description}
            
#             ### INSTRUCTION:
#             You are a job seeker interested in the above job. 
#             Write a **cold email** to the hiring manager or recruiter, expressing interest in the position and requesting a chance to discuss further. 
#             The email should:
#             - Be **professionally structured**
#             - Have a **strong opening**
#             - Showcase your **skills and enthusiasm**
#             - End with a **clear call to action** (requesting an interview or discussion)
            
#             Also, include the most relevant links from the following to showcase the applicant's portfolio: {link_list}

#             ### COLD EMAIL (NO PREAMBLE):
#             """
#         )
#         chain_cold_email = prompt_cold_email | self.llm
#         res = chain_cold_email.invoke({"job_description": str(job), "link_list": links})
#         return res.content

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.3-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from a career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: 
            `role`, `company`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        
        return res if isinstance(res, list) else [res]

    def write_letter(self, job, portfolio_items):
        # Format portfolio items for the prompt
        portfolio_text = ""
        for item in portfolio_items:
            portfolio_text += f"- Tech stack: {item.get('techstack', '')}, Link: {item.get('links', '')}\n"
        
        if not portfolio_text:
            portfolio_text = "No specific portfolio items to highlight."
            
        prompt_cover_letter = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### PORTFOLIO INFORMATION:
            Relevant projects/skills to highlight:
            {portfolio_links}
            
            ### INSTRUCTION:
            You are a job applicant seeking a position related to the job mentioned above. 
            Your task is to write a compelling and personalized cover letter that highlights your relevant skills, experience, 
            and how you can contribute to the company. 

            Ensure the cover letter is:
            - Professionally structured
            - Tailored to the specific job description
            - Showcases relevant skills and achievements from your portfolio
            - Engaging and concise
            
            Include references to the most relevant experiences, projects, or achievements that align with the job description.
            
            ### COVER LETTER (NO PREAMBLE):
            """
        )
        chain_cover_letter = prompt_cover_letter | self.llm
        res = chain_cover_letter.invoke({"job_description": str(job), "portfolio_links": portfolio_text})
        return res.content

    def write_resume(self, job):
        prompt_resume = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### INSTRUCTION:
            You are creating a **tailored resume** for the above job description. 
            The resume should be:
            - **ATS-friendly** (Applicant Tracking System compliant)
            - **Well-formatted** with proper sections like Summary, Skills, Experience, and Education
            - **Optimized** to match the keywords from the job description
            
            Ensure the resume is clean, concise, and follows professional standards.

            ### RESUME (NO PREAMBLE):
            """
        )
        chain_resume = prompt_resume | self.llm
        res = chain_resume.invoke({"job_description": str(job)})
        return res.content

    def write_cold_email(self, job, portfolio_items, recruiter_email=None):
        # Format portfolio items for the prompt
        portfolio_text = ""
        for item in portfolio_items:
            portfolio_text += f"- Tech stack: {item.get('techstack', '')}, Link: {item.get('links', '')}\n"
        
        if not portfolio_text:
            portfolio_text = "No specific portfolio items to highlight."
            
        email_recipient = "the hiring manager"
        if recruiter_email:
            email_recipient = recruiter_email
            
        prompt_cold_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### PORTFOLIO INFORMATION:
            Relevant projects/skills to highlight:
            {portfolio_links}
            
            ### RECIPIENT:
            {email_recipient}
            
            ### INSTRUCTION:
            You are a job seeker interested in the above job. 
            Write a **cold email** to {email_recipient}, expressing interest in the position and requesting a chance to discuss further. 
            The email should:
            - Be **professionally structured** with an appropriate subject line
            - Have a **strong opening**
            - Showcase your **skills and enthusiasm** that match the job requirements
            - Reference your most relevant portfolio projects/experiences
            - End with a **clear call to action** (requesting an interview or discussion)
            
            ### COLD EMAIL (NO PREAMBLE):
            """
        )
        chain_cold_email = prompt_cold_email | self.llm
        res = chain_cold_email.invoke({
            "job_description": str(job), 
            "portfolio_links": portfolio_text,
            "email_recipient": email_recipient
        })
        return res.content
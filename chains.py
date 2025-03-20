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
#             The scraped text is from the career's page of a website.
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
#     """
#     ### JOB DESCRIPTION:
#     {job_description}
    
#     ### INSTRUCTION:
#     You are a job applicant seeking a position related to the job mentioned above. 
#     Your task is to write a compelling and personalized cover letter that highlights your relevant skills, experience, 
#     and how you can contribute to the company. 

#     Ensure the cover letter is:
#     - Professionally structured
#     - Tailored to the specific job description
#     - Showcases relevant skills and achievements
#     - Engaging and concise
    
#     Include references to the most relevant experiences, projects, or achievements that align with the job description.
    
#     ### COVER LETTER (NO PREAMBLE):
    
#     """
# )

#         chain_cover_letter = prompt_cover_letter | self.llm
#         res = chain_cover_letter.invoke({"job_description": str(job)})
#         print(res.content)
#         return res.content

# if __name__ == "__main__":
#     print(os.getenv("GROQ_API_KEY"))

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
            The scraped text is from a careers page of a website.
            Your job is to extract job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills`, and `description`.
            Only return valid JSON.
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

    def write_letter(self, job, links):
        prompt_cover_letter = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### INSTRUCTION:
            You are a job applicant seeking a position related to the job mentioned above. 
            Your task is to write a compelling and personalized cover letter that highlights your relevant skills, experience, 
            and how you can contribute to the company. 

            Ensure the cover letter is:
            - Professionally structured
            - Tailored to the specific job description
            - Showcases relevant skills and achievements
            - Engaging and concise
            
            Include references to the most relevant experiences, projects, or achievements that align with the job description.
            
            ### COVER LETTER (NO PREAMBLE):
            """
        )

        chain_cover_letter = prompt_cover_letter | self.llm
        res = chain_cover_letter.invoke({"job_description": str(job)})
        return res.content

    def write_resume(self, job, links):
        prompt_resume = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}
            
            ### INSTRUCTION:
            You are a job applicant creating a **tailored resume** for the job mentioned above. 
            Your task is to generate a **professionally formatted, ATS-friendly** resume that highlights:
            - **Relevant work experience**
            - **Skills that match the job description**
            - **Projects and achievements**
            - **Education and certifications** (if applicable)
            - **Keywords** from the job description to improve ATS ranking
            
            Ensure the resume follows this format:

            ```
            [Your Name]
            [Your Email] | [Your Phone Number] | [LinkedIn Profile] | [Portfolio/Website]
            
            PROFESSIONAL SUMMARY
            - Brief summary (2-3 sentences) of your expertise and how it aligns with the job role.
            
            SKILLS
            - Bullet points of skills relevant to the job description.
            
            EXPERIENCE
            - Job Title | Company Name | Dates of Employment
              - Key achievement or responsibility related to the job description.
              - Another key achievement or responsibility.
            
            PROJECTS (if applicable)
            - Project Name | Brief description and impact.
            
            EDUCATION
            - Degree | University Name | Graduation Year
            
            CERTIFICATIONS (if applicable)
            - Certification Name | Issuing Organization | Year
            
            ```

            Ensure:
            - The resume is **concise** (one page if possible).
            - Uses **job-relevant keywords** for **ATS optimization**.
            - Is **properly formatted** and **easy to read**.
            
            **Generate the resume below:**  
            """
        )

        chain_resume = prompt_resume | self.llm
        res = chain_resume.invoke({"job_description": str(job)})
        return res.content


if __name__ == "__main__":
    print(os.getenv("GROQ_API_KEY"))


# import streamlit as st
# from langchain_community.document_loaders import WebBaseLoader
# from chains import Chain
# from portfolio import Portfolio
# from utils import clean_text


# def create_streamlit_app(llm, portfolio, clean_text):
#     st.title("📧 Cover Letter, Resume & Cold Email Generator")

#     url_input = st.text_input("Enter a Job Posting URL:", placeholder="https://example.com/job/")
#     option = st.radio("Select Document Type:", ["Cover Letter", "Resume", "Cold Email"])
#     submit_button = st.button("Generate")

#     if submit_button:
#         try:
#             loader = WebBaseLoader([url_input])
#             data = clean_text(loader.load().pop().page_content)
#             portfolio.load_portfolio()
#             jobs = llm.extract_jobs(data)
            
#             for job in jobs:
#                 skills = job.get('skills', [])
#                 links = portfolio.query_links(skills)

#                 if option == "Cover Letter":
#                     output = llm.write_letter(job, links)
#                 elif option == "Resume":
#                     output = llm.write_resume(job)
#                 else:  # Cold Email
#                     output = llm.write_cold_email(job, links)

#                 st.code(output, language='markdown')

#         except Exception as e:
#             st.error(f"An Error Occurred: {e}")


# if __name__ == "__main__":
#     chain = Chain()
#     portfolio = Portfolio()
#     st.set_page_config(layout="wide", page_title="Cover Letter & Resume Generator", page_icon="📧")
#     create_streamlit_app(chain, portfolio, clean_text)

import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
import pandas as pd
import requests
import json
import os
from datetime import datetime

from chains import Chain
from portfolio import Portfolio
from utils import clean_text, find_recruiter_email

# Initialize session state for saved jobs if it doesn't exist
if 'saved_jobs' not in st.session_state:
    st.session_state.saved_jobs = []

def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cover Letter, Resume & Cold Email Generator")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Generate Documents", "Saved Jobs", "Portfolio Management"])
    
    with tab1:
        st.header("Generate Application Materials")
        url_input = st.text_input("Enter a Job Posting URL:", value="https://example.com/job/")
        option = st.radio("Select Document Type:", ["Cover Letter", "Resume", "Cold Email"])
        
        # Option to find recruiter email automatically
        find_email = st.checkbox("Automatically find recruiter email for cold emails")
        
        # Add option to save job
        save_job = st.checkbox("Save this job to your list")
        
        submit_button = st.button("Generate")

        if submit_button:
            try:
                # Show a spinner while processing
                with st.spinner("Processing job data..."):
                    loader = WebBaseLoader([url_input])
                    data = clean_text(loader.load().pop().page_content)
                    portfolio.load_portfolio()
                    jobs = llm.extract_jobs(data)
                    
                    for job in jobs:
                        # If save_job is checked, add to saved jobs
                        if save_job:
                            job_entry = {
                                "url": url_input,
                                "role": job.get('role', 'Unknown Role'),
                                "company": job.get('company', 'Unknown Company'),
                                "date_saved": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            st.session_state.saved_jobs.append(job_entry)
                            st.success(f"Job saved: {job.get('role', 'Unknown Role')}")
                        
                        skills = job.get('skills', [])
                        links = portfolio.query_links(skills)
                        
                        # Get recruiter email if option is selected and it's a cold email
                        recruiter_email = None
                        if find_email and option == "Cold Email":
                            recruiter_email = find_recruiter_email(job.get('company', ''))
                            if recruiter_email:
                                st.info(f"Found potential recruiter email: {recruiter_email}")
                            else:
                                st.warning("Could not find recruiter email automatically.")

                        if option == "Cover Letter":
                            output = llm.write_letter(job, links)
                            st.subheader("📜 Generated Cover Letter")
                        elif option == "Resume":
                            output = llm.write_resume(job)
                            st.subheader("📄 Generated Resume")
                        else:  # Cold Email
                            output = llm.write_cold_email(job, links, recruiter_email)
                            st.subheader("📨 Generated Cold Email")

                        st.code(output, language='markdown')
                        
                        # Add download button for the generated content
                        st.download_button(
                            label=f"Download {option}",
                            data=output,
                            file_name=f"{option.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.md",
                            mime="text/markdown"
                        )

            except Exception as e:
                st.error(f"An Error Occurred: {e}")
    
    with tab2:
        st.header("Saved Jobs")
        if len(st.session_state.saved_jobs) > 0:
            # Create a table of saved jobs
            jobs_df = pd.DataFrame(st.session_state.saved_jobs)
            st.dataframe(jobs_df)
            
            # Option to delete selected jobs
            if st.button("Clear All Saved Jobs"):
                st.session_state.saved_jobs = []
                st.success("All jobs cleared!")
                st.experimental_rerun()
        else:
            st.info("No saved jobs yet. Generate a document and check 'Save this job' to add jobs here.")
    
    with tab3:
        st.header("Portfolio Management")
        
        portfolio_tab1, portfolio_tab2, portfolio_tab3 = st.tabs(["Upload CSV", "Manual Entry", "LinkedIn Import"])
        
        with portfolio_tab1:
            st.subheader("Upload Portfolio CSV")
            st.markdown("Upload a CSV file with your portfolio details. The file should have 'Techstack' and 'Links' columns.")
            
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            if uploaded_file is not None:
                try:
                    portfolio_df = pd.read_csv(uploaded_file)
                    if 'Techstack' in portfolio_df.columns and 'Links' in portfolio_df.columns:
                        # Create resource directory if it doesn't exist
                        os.makedirs("resource", exist_ok=True)
                        # Save the uploaded file
                        portfolio_df.to_csv("resource/my_portfolio.csv", index=False)
                        st.success("Portfolio uploaded successfully!")
                        
                        # Preview the data
                        st.subheader("Portfolio Preview")
                        st.dataframe(portfolio_df)
                    else:
                        st.error("CSV must contain 'Techstack' and 'Links' columns")
                except Exception as e:
                    st.error(f"Error processing CSV: {e}")
        
        with portfolio_tab2:
            st.subheader("Manual Portfolio Entry")
            
            # Get existing portfolio if available
            try:
                existing_portfolio = pd.read_csv("resource/my_portfolio.csv")
            except:
                existing_portfolio = pd.DataFrame(columns=["Techstack", "Links"])
            
            # Show existing entries
            if not existing_portfolio.empty:
                st.subheader("Current Portfolio Entries")
                st.dataframe(existing_portfolio)
            
            # Form for adding new entry
            with st.form("portfolio_entry_form"):
                tech_stack = st.text_input("Technologies (comma separated)", "React, Node.js, MongoDB")
                project_link = st.text_input("Project Link", "https://example.com/my-project")
                
                submit_entry = st.form_submit_button("Add Entry")
                
                if submit_entry:
                    # Create resource directory if it doesn't exist
                    os.makedirs("resource", exist_ok=True)
                    new_entry = pd.DataFrame({"Techstack": [tech_stack], "Links": [project_link]})
                    updated_portfolio = pd.concat([existing_portfolio, new_entry], ignore_index=True)
                    updated_portfolio.to_csv("resource/my_portfolio.csv", index=False)
                    st.success("Entry added successfully!")
                    st.experimental_rerun()
        
        with portfolio_tab3:
            st.subheader("LinkedIn Import")
            st.markdown("Note: This feature requires LinkedIn API access, which may require developer approval.")
            
            linkedin_url = st.text_input("Enter your LinkedIn profile URL")
            linkedin_import_btn = st.button("Import from LinkedIn")
            
            if linkedin_import_btn:
                st.warning("LinkedIn import functionality is currently in development. Please use CSV upload or manual entry for now.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cover Letter & Resume Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
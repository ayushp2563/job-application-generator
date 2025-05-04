
import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

import pandas as pd
import requests
import json
import os
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from chains import Chain
from utils import clean_text, find_recruiter_email
from database import get_db, init_db
import db_operations as db_ops
from auth import verify_password, get_password_hash, create_access_token

# Initialize the database
init_db()

# Initialize session states
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'current_job_id' not in st.session_state:
    st.session_state.current_job_id = None


def login_user(db: Session, email: str, password: str):
    """Log in a user and return user ID if successful"""
    user = db_ops.get_user_by_email(db, email)
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
        
    return user.id


def register_user(db: Session, email: str, password: str):
    """Register a new user and return user ID if successful"""
    existing_user = db_ops.get_user_by_email(db, email)
    
    if existing_user:
        return None
    
    hashed_password = get_password_hash(password)
    user = db_ops.create_user(db, email, hashed_password)
    
    return user.id


def login_page():
    """Display login and registration forms"""
    st.title("Cover Letter & Resume Generator")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.header("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login"):
            if not email or not password:
                st.error("Please fill in all fields")
                return
            
            # Get database session
            session = next(get_db())
            
            user_id = login_user(session, email, password)
            if user_id:
                st.session_state.user_id = user_id
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password")
    
    with tab2:
        st.header("Register")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Register"):
            if not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
                
            if password != confirm_password:
                st.error("Passwords do not match")
                return
                
            # Get database session
            session = next(get_db())
            
            user_id = register_user(session, email, password)
            if user_id:
                st.session_state.user_id = user_id
                st.success("Registration successful! You are now logged in.")
                st.rerun()
            else:
                st.error("Email already registered")


def main_app():
    """Main application interface after login"""
    st.title("📧 Cover Letter, Resume & Cold Email Generator")
    
    # Create tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Generate Documents", "Saved Jobs", "Portfolio Management"])
    
    # Get database session
    db = next(get_db())
    
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
                    # Initialize the LLM chain
                    chain = Chain()
                    
                    loader = WebBaseLoader([url_input])
                    data = clean_text(loader.load().pop().page_content)
                    jobs = chain.extract_jobs(data)
                    
                    for job in jobs:
                        # Save job to database if option is selected
                        job_id = None
                        if save_job:
                            job_data = {
                                "url": url_input,
                                "company": job.get('company', 'Unknown Company'),
                                "role": job.get('role', 'Unknown Role'),
                                "description": job.get('description', ''),
                                "experience": job.get('experience', ''),
                                "skills": job.get('skills', [])
                            }
                            
                            db_job = db_ops.create_job(db, st.session_state.user_id, job_data)
                            job_id = db_job.id
                            st.session_state.current_job_id = job_id
                            st.success(f"Job saved: {job.get('role', 'Unknown Role')}")
                        
                        # Get user's portfolio items that match the job skills
                        skills = job.get('skills', [])
                        portfolio_items = db_ops.query_portfolio_by_skills(db, st.session_state.user_id, skills)
                        
                        # Format portfolio items for the LLM
                        portfolio_data = []
                        for item in portfolio_items:
                            portfolio_data.append({
                                "techstack": item.tech_stack,
                                "links": item.link
                            })
                        
                        # Get recruiter email if option is selected and it's a cold email
                        recruiter_email = None
                        if find_email and option == "Cold Email":
                            recruiter_email = find_recruiter_email(job.get('company', ''))
                            if recruiter_email:
                                st.info(f"Found potential recruiter email: {recruiter_email}")
                            else:
                                st.warning("Could not find recruiter email automatically.")

                        # Generate document based on selected option
                        if option == "Cover Letter":
                            output = chain.write_letter(job, portfolio_data)
                            st.subheader("📜 Generated Cover Letter")
                        elif option == "Resume":
                            output = chain.write_resume(job)
                            st.subheader("📄 Generated Resume")
                        else:  # Cold Email
                            output = chain.write_cold_email(job, portfolio_data, recruiter_email)
                            st.subheader("📨 Generated Cold Email")

                        # Display the generated content
                        st.code(output, language='markdown')
                        
                        # Save the generated document to the database if job was saved
                        if job_id:
                            db_ops.create_generated_document(db, job_id, option.lower().replace(" ", "_"), output)
                        
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
        
        # Retrieve user's saved jobs from database
        jobs = db_ops.get_user_jobs(db, st.session_state.user_id)
        
        if jobs:
            # Create a list of job entries for display
            job_data = []
            for job in jobs:
                job_data.append({
                    "id": job.id,
                    "company": job.company,
                    "role": job.role,
                    "date_saved": job.date_saved.strftime("%Y-%m-%d %H:%M:%S") if job.date_saved else "Unknown"
                })
            
            # Create a dataframe for display
            jobs_df = pd.DataFrame(job_data)
            
            # Display the jobs table
            st.dataframe(jobs_df)
            
            # Create columns for job selection and action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Create a selectbox with job titles
                selected_job_id = st.selectbox(
                    "Select a job to view or delete",
                    options=[job["id"] for job in job_data],
                    format_func=lambda x: next((f"{job['company']} - {job['role']}" for job in job_data if job["id"] == x), "")
                )
            
            with col2:
                # Action buttons
                if st.button("View Documents"):
                    if selected_job_id:
                        documents = db_ops.get_documents_by_job_id(db, selected_job_id)
                        if documents:
                            st.subheader("Generated Documents")
                            for doc in documents:
                                doc_type = doc.document_type.replace("_", " ").title()
                                with st.expander(f"{doc_type} - {doc.created_at.strftime('%Y-%m-%d %H:%M:%S')}"):
                                    st.code(doc.content, language='markdown')
                                    
                                    # Add download button
                                    st.download_button(
                                        label=f"Download {doc_type}",
                                        data=doc.content,
                                        file_name=f"{doc.document_type}_{doc.created_at.strftime('%Y%m%d')}.md",
                                        mime="text/markdown"
                                    )
                        else:
                            st.info("No documents generated for this job.")
                
                if st.button("Delete Job"):
                    if selected_job_id:
                        if db_ops.delete_job(db, selected_job_id):
                            st.success("Job deleted successfully!")
                            st.rerun()

                        else:
                            st.error("Failed to delete job.")
            
            # Option to clear all saved jobs
            if st.button("Clear All Saved Jobs"):
                for job in jobs:
                    db_ops.delete_job(db, job.id)
                st.success("All jobs cleared!")
                st.rerun()
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
                        # Clear existing portfolio items
                        existing_items = db_ops.get_user_portfolio(db, st.session_state.user_id)
                        for item in existing_items:
                            db_ops.delete_portfolio_item(db, item.id)
                        
                        # Add new portfolio items from CSV
                        for _, row in portfolio_df.iterrows():
                            db_ops.create_portfolio_item(
                                db, 
                                st.session_state.user_id,
                                row['Techstack'],
                                row['Links']
                            )
                        
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
            
            # Get existing portfolio items
            portfolio_items = db_ops.get_user_portfolio(db, st.session_state.user_id)
            
            # Show existing entries
            if portfolio_items:
                portfolio_data = []
                for item in portfolio_items:
                    portfolio_data.append({
                        "id": item.id,
                        "Tech Stack": item.tech_stack,
                        "Link": item.link,
                        "Created": item.created_at.strftime("%Y-%m-%d")
                    })
                
                st.subheader("Current Portfolio Entries")
                portfolio_df = pd.DataFrame(portfolio_data)
                st.dataframe(portfolio_df)
                
                # Option to delete an item
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_item_id = st.selectbox(
                        "Select an item to delete",
                        options=[item["id"] for item in portfolio_data],
                        format_func=lambda x: next((f"{item['Tech Stack']} - {item['Link']}" for item in portfolio_data if item["id"] == x), "")
                    )
                
                with col2:
                    if st.button("Delete Selected Item"):
                        if db_ops.delete_portfolio_item(db, selected_item_id):
                            st.success("Portfolio item deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete item.")
            
            # Form for adding new entry
            with st.form("portfolio_entry_form"):
                tech_stack = st.text_input("Technologies (comma separated)", "React, Node.js, MongoDB")
                project_link = st.text_input("Project Link", "https://example.com/my-project")
                
                submit_entry = st.form_submit_button("Add Entry")
                
                if submit_entry:
                    if db_ops.create_portfolio_item(db, st.session_state.user_id, tech_stack, project_link):
                        st.success("Entry added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add entry.")
        
        with portfolio_tab3:
            st.subheader("LinkedIn Import")
            st.markdown("Note: This feature requires LinkedIn API access, which may require developer approval.")
            
            linkedin_url = st.text_input("Enter your LinkedIn profile URL")
            linkedin_import_btn = st.button("Import from LinkedIn")
            
            if linkedin_import_btn:
                st.warning("LinkedIn import functionality is currently in development. Please use CSV upload or manual entry for now.")


def logout():
    """Log out the current user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# Main app function
def app():
    # Display sidebar with logout option if logged in
    if st.session_state.user_id:
        with st.sidebar:
            st.write(f"Welcome, User #{st.session_state.user_id}!")
            if st.button("Logout"):
                logout()
    
    # Show login page or main app based on login status
    if st.session_state.user_id is None:
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cover Letter & Resume Generator", page_icon="📧")
    app()
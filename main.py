import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Job Application Generator")

    url_input = st.text_input("Enter a Job URL:", value="https://example.com/job/")
    option = st.radio("Choose what to generate:", ("Cover Letter", "Resume"))
    submit_button = st.button("Generate")

    if submit_button:
        try:
            loader = WebBaseLoader([url_input])
            data = clean_text(loader.load().pop().page_content)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)

                if option == "Cover Letter":
                    result = llm.write_letter(job, links)
                    st.subheader("📜 Generated Cover Letter")
                else:
                    result = llm.write_resume(job, links)
                    st.subheader("📄 Generated Resume")

                st.code(result, language='markdown')

        except Exception as e:
            st.error(f"An Error Occurred: {e}")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Job Application Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)

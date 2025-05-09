import re
import os
import requests
import streamlit as st
from urllib.parse import urlparse, parse_qs

def clean_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove special characters
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s{2,}', ' ', text)
    # Trim leading and trailing whitespace
    text = text.strip()
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def extract_company_from_workday(url):
    """Extract company name from Workday URL"""
    try:
        # Parse the URL
        parsed_url = urlparse(url)
        
        # Common Workday URL patterns
        workday_patterns = [
            r'(?:https?://)?([^.]+)\.workday\.com',  # company.workday.com
            r'(?:https?://)?wd3\.myworkday\.com/([^/]+)',  # wd3.myworkday.com/company
            r'(?:https?://)?career\d?\.([^.]+)\.com'  # career.company.com
        ]
        
        for pattern in workday_patterns:
            match = re.search(pattern, url)
            if match:
                company_name = match.group(1)
                # Clean up company name
                company_name = company_name.replace('-', ' ').replace('_', ' ')
                return company_name.strip()
                
        return None
    except Exception:
        return None

def find_recruiter_email(company_name, department=None):
    """
    Attempts to find a recruiter email for the given company and department using Hunter.io API
    """
    # Try to get API key from Streamlit secrets first, then fall back to environment variable
    api_key = st.secrets.get("HUNTER_API_KEY", os.getenv("HUNTER_API_KEY"))
    
    if not api_key or not company_name:
        st.warning("Hunter.io API key not found. Please add it to your Streamlit secrets.")
        return None
        
    try:
        # Clean the company name
        company_name = company_name.strip().lower()
        company_name = re.sub(r'\s+(inc|llc|corp|ltd|co)\.?$', '', company_name, flags=re.IGNORECASE)
        domain = company_name.replace(' ', '').replace(',', '').replace('.', '')
        domain = f"{domain}.com"
        
        # Make request to Hunter.io API
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            emails = data.get('data', {}).get('emails', [])
            
            # Define department-specific keywords
            department_keywords = {
                'software': ['software', 'engineering', 'developer', 'tech'],
                'marketing': ['marketing', 'growth', 'brand'],
                'sales': ['sales', 'business development', 'account'],
                'hr': ['hr', 'recruit', 'talent', 'people', 'hiring'],
                'finance': ['finance', 'accounting', 'treasury'],
                'product': ['product', 'pm', 'program manager'],
                'design': ['design', 'ux', 'ui', 'user experience'],
                'data': ['data', 'analytics', 'ml', 'ai'],
                'operations': ['operations', 'ops', 'administrative']
            }
            
            # If department is provided, try to match department-specific recruiter
            if department:
                department = department.lower()
                relevant_keywords = []
                
                # Find relevant keywords for the department
                for dept, keywords in department_keywords.items():
                    if any(kw in department for kw in keywords):
                        relevant_keywords.extend(keywords)
                        break
                
                # If no specific department keywords found, default to HR keywords
                if not relevant_keywords:
                    relevant_keywords = department_keywords['hr']
                
                # First try to find department-specific recruiter
                for email in emails:
                    position = (email.get('position', '') or '').lower()
                    if any(keyword in position for keyword in relevant_keywords):
                        return email.get('value')
                
                # Then try to find any HR/recruiting person
                for email in emails:
                    position = (email.get('position', '') or '').lower()
                    if any(keyword in position for keyword in department_keywords['hr']):
                        return email.get('value')
            
            # If no department-specific match or no department provided, return first HR/recruiting email
            for email in emails:
                position = (email.get('position', '') or '').lower()
                if any(keyword in position for keyword in department_keywords['hr']):
                    return email.get('value')
            
            # If still no match, return the first email
            if emails:
                return emails[0].get('value')
    
    except Exception as e:
        st.error(f"Error finding recruiter email: {e}")
    
    return None
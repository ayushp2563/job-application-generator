# import re

# def clean_text(text):
#     # Remove HTML tags
#     text = re.sub(r'<[^>]*?>', '', text)
#     # Remove URLs
#     text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
#     # Remove special characters
#     text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
#     # Replace multiple spaces with a single space
#     text = re.sub(r'\s{2,}', ' ', text)
#     # Trim leading and trailing whitespace
#     text = text.strip()
#     # Remove extra whitespace
#     text = ' '.join(text.split())
#     return text

import re
import os
import requests

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

def find_recruiter_email(company_name):
    """
    Attempts to find a recruiter email for the given company using Hunter.io API
    
    Note: This requires a Hunter.io API key set as HUNTER_API_KEY environment variable
    If not available, it will return None
    """
    api_key = os.getenv("HUNTER_API_KEY")
    if not api_key or not company_name:
        return None
        
    try:
        # Clean the company name to ensure it's a valid domain
        company_name = company_name.strip().lower()
        # Remove common legal entity indicators
        company_name = re.sub(r'\s+(inc|llc|corp|ltd|co)\.?$', '', company_name, flags=re.IGNORECASE)
        # Remove spaces and special chars for domain format
        domain = company_name.replace(' ', '').replace(',', '').replace('.', '')
        domain = f"{domain}.com"  # Assuming .com domain
        
        # Make request to Hunter.io API
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Look for recruiting/HR emails
            emails = data.get('data', {}).get('emails', [])
            
            # First try to find explicitly recruiting-related emails
            recruiting_keywords = ['recruit', 'hr', 'talent', 'people', 'hiring', 'careers']
            for email in emails:
                position = email.get('position', '').lower()
                if any(keyword in position for keyword in recruiting_keywords):
                    return email.get('value')
            
            # If no recruiting emails found, return the first email (if available)
            if emails:
                return emails[0].get('value')
    
    except Exception as e:
        print(f"Error finding recruiter email: {e}")
    
    return None
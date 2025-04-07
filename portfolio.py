import pandas as pd
import os
import re

class Portfolio:
    def __init__(self, file_path="resource/my_portfolio.csv"):
        self.file_path = file_path
        
        # Create resource directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if portfolio file exists, create a default one if not
        if not os.path.exists(file_path):
            default_data = {
                "Techstack": ["React, Node.js, MongoDB", "Python, Django, MySQL"],
                "Links": ["https://example.com/react-portfolio", "https://example.com/python-portfolio"]
            }
            pd.DataFrame(default_data).to_csv(file_path, index=False)
        
        self.data = pd.read_csv(file_path)

    def load_portfolio(self):
        # Read the latest data in case it was updated
        try:
            self.data = pd.read_csv(self.file_path)
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            # Create a default portfolio if there's an issue
            self.data = pd.DataFrame({
                "Techstack": ["React, Node.js, MongoDB", "Python, Django, MySQL"],
                "Links": ["https://example.com/react-portfolio", "https://example.com/python-portfolio"]
            })

    def query_links(self, skills):
        """
        Find relevant portfolio entries based on skills
        Using a simple keyword matching approach instead of vector similarity
        """
        if not isinstance(skills, list):
            if isinstance(skills, str):
                skills = [skills]
            else:
                skills = ["general"]
                
        # Ensure skills is not empty
        if not skills:
            skills = ["general"]
            
        # Create a list to store matching entries
        matches = []
        
        # For each skill in the query
        for skill in skills:
            skill = str(skill).lower()
            
            # For each entry in the portfolio
            for _, row in self.data.iterrows():
                tech_stack = str(row["Techstack"]).lower()
                
                # If the skill appears in the tech stack and this entry isn't already matched
                if skill in tech_stack:
                    entry = {"links": row["Links"], "techstack": row["Techstack"]}
                    if entry not in matches:
                        matches.append(entry)
        
        # If no matches found, return the first few entries as defaults
        if not matches and len(self.data) > 0:
            for i in range(min(3, len(self.data))):
                row = self.data.iloc[i]
                matches.append({"links": row["Links"], "techstack": row["Techstack"]})
                
        return matches
        
    def add_portfolio_entry(self, techstack, link):
        """Add a new entry to the portfolio CSV"""
        new_entry = pd.DataFrame({"Techstack": [techstack], "Links": [link]})
        self.data = pd.concat([self.data, new_entry], ignore_index=True)
        self.data.to_csv(self.file_path, index=False)
        
    def get_portfolio_data(self):
        """Return the current portfolio data"""
        return self.data
        
    def clear_portfolio(self):
        """Clear all portfolio entries"""
        self.data = pd.DataFrame(columns=["Techstack", "Links"])
        self.data.to_csv(self.file_path, index=False)
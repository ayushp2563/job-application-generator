# 📧 Cover Letter & Resume Generator

This project is an **AI-powered tool** that generates **tailored cover letters and ATS-friendly resumes** based on job descriptions. It leverages **LangChain**, **Streamlit**, and **Groq's LLaMA-3 model** to scrape job postings, extract key details, and create **customized application materials**.

---

## 🚀 Features

✅ **Cover Letter Generation** – Generates job-specific cover letters that highlight relevant skills and experiences.  
✅ **Resume Generation** – Creates a **formatted**, **ATS-optimized** resume tailored to the job description.  
✅ **Job Posting Extraction** – Scrapes job details (role, experience, skills) from provided job URLs.  
✅ **Streamlit UI** – Simple and interactive web-based interface for easy usage.  
✅ **AI-Powered** – Uses **LangChain** with **Groq's LLaMA-3** model for intelligent text generation.  

---

## 🛠️ Tech Stack

- **Python** 🐍  
- **Streamlit** 🎨 (for the UI)  
- **LangChain** 🧠 (for AI-driven text generation)  
- **Groq's LLaMA-3** 🤖 (for generating responses)  
- **dotenv** 🔑 (for environment variable management)  

---

## 📦 Installation

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/cover-letter-resume-generator.git
cd cover-letter-resume-generator
```

**2️⃣ Set Up Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows
```

**3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```
**4️⃣ Set Up API Keys**
```bash
GROQ_API_KEY=your_groq_api_key_here
```
**🎮 Usage**
```bash
streamlit run main.py
```
**📂 Project Structure**
```bash
📂 cover-letter-resume-generator
│── 📄 app.py                  # Streamlit app entry point
│── 📄 chains.py               # Handles AI model interactions
│── 📄 portfolio.py            # Portfolio reference handling
│── 📄 utils.py                # Utility functions
│── 📄 requirements.txt        # Required Python packages
│── 📄 README.md               # Project documentation
│── 📄 .env.example            # Example env file for API keys
```
**🤝 Contributing**
```bash
Want to improve this project? Feel free to fork it and submit a pull request! 🚀
```

**📜 License**
```bash
This project is licensed under the MIT License.
```







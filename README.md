# RESUMATCH – AI-Powered ATS Resume Analyzer

## Overview

**RESUMATCH** is an AI-powered Applicant Tracking System (ATS) Resume Analyzer designed to help job seekers optimize their resumes for specific job descriptions. The platform evaluates resume compatibility, identifies missing skills and keywords, and provides actionable recommendations to improve ATS performance and increase interview opportunities.

The application combines Natural Language Processing (NLP), semantic similarity analysis, and Large Language Models (LLMs) to deliver intelligent resume assessments and personalized feedback.

---

## Key Features

### Resume Analysis

* Upload resumes in PDF, DOC, or DOCX format.
* Automatic extraction of resume content and relevant information.
* Support for multiple resume formats.

### ATS Match Scoring

* Calculates an overall ATS compatibility score.
* Compares resume content against a provided job description.
* Highlights strengths and areas requiring improvement.

### Skill & Keyword Evaluation

* Detects technical and soft skills present in the resume.
* Identifies missing keywords from the target job description.
* Validates skill relevance using semantic similarity techniques.

### AI-Powered Recommendations

* Generates personalized improvement suggestions using LLMs.
* Recommends content enhancements and keyword optimizations.
* Provides guidance for increasing ATS compatibility.

### Detailed Score Breakdown

The ATS score is divided into multiple categories:

* Resume Formatting
* Keyword Matching
* Content Quality
* Skill Validation
* ATS Compatibility

### User Authentication

* Secure Email/Password Authentication.
* Google OAuth Login Integration.
* Personalized dashboard experience.

### Analysis History

* Saves previous resume evaluations.
* Allows users to revisit and compare past analyses.

### PDF Report Generation

* Export detailed ATS analysis reports.
* Download professional evaluation summaries.

---

## Technology Stack

### Frontend

* Streamlit

### Backend

* FastAPI
* Python

### Natural Language Processing

* spaCy (`en_core_web_md`)
* Sentence Transformers (`all-MiniLM-L6-v2`)

### Artificial Intelligence

* Groq API
* Llama 3

### Database & Authentication

* Supabase
* Google OAuth

### Report Generation

* Jinja2
* WeasyPrint

---

## System Architecture

```text
User Resume + Job Description
            │
            ▼
      Streamlit Frontend
            │
            ▼
       FastAPI Backend
            │
 ┌──────────┼──────────┐
 ▼          ▼          ▼
Resume   NLP Engine   AI Feedback
Parser   (spaCy +     (Llama 3)
          SBERT)
            │
            ▼
      ATS Score Engine
            │
            ▼
      Results Dashboard
            │
            ▼
      PDF Report Export
```

---

## Project Structure

```text
RESUMATCH/
│
├── backend/                 # FastAPI backend services
├── frontend/                # Streamlit frontend application
├── ml model/                # Trained and exported ML artifacts
├── jupyter notebooks/       # Research and experimentation notebooks
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variable template
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/ayushagarwal619/RESUMATCH.git
cd RESUMATCH
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Download the spaCy language model:

```bash
python -m spacy download en_core_web_md
```

---

## Environment Configuration

Create a `.env` file and configure the following variables:

```env
SUPABASE_URL=
SUPABASE_KEY=
SUPABASE_ANON_KEY=

GROQ_API_KEY=
```

For Streamlit secrets:

```bash
frontend/.streamlit/secrets.toml
```

Add your Supabase credentials accordingly.

---

## Running the Backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URL:

```text
http://localhost:8000
```

---

## Running the Frontend

```bash
streamlit run frontend/streamlit_app.py
```

Frontend URL:

```text
http://localhost:8501
```

---

## How It Works

1. User uploads a resume.
2. User enters a target job description.
3. Resume content is extracted and processed.
4. NLP models identify skills, keywords, and experience.
5. Semantic similarity is calculated between the resume and job description.
6. ATS scoring engine evaluates overall compatibility.
7. LLM generates personalized improvement recommendations.
8. Results are displayed through an interactive dashboard.
9. Users can export reports and save analyses for future reference.

---

## Learning Outcomes

Through this project, I gained practical experience in:

* Full-Stack Application Development
* FastAPI Backend Development
* Streamlit Application Design
* Natural Language Processing (NLP)
* Semantic Search & Similarity Models
* Large Language Model Integration
* Authentication & Database Management
* API Development & Integration
* Resume Parsing Techniques
* AI-Powered Product Development

---

## Future Improvements

* Multi-language resume support
* Resume ranking against multiple job descriptions
* Cover letter generation
* Real-time interview preparation recommendations
* Advanced analytics dashboard
* Industry-specific ATS scoring models

---

## Author

**Ayush Agarwal**

B.Tech CSE Student | Full Stack & AI Developer

GitHub: https://github.com/ayushagarwal619

---

## License

This project is developed for educational, learning, and portfolio purposes.

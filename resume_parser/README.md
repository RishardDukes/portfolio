# Resume Parser & Job Matcher

Extract information from resumes and match them against job descriptions.

## Features
- [ ] Parse resume files (PDF, DOCX, TXT)
- [ ] Extract key information:
  - Contact info
  - Work experience
  - Education
  - Skills
  - Certifications
- [ ] AI-powered skill extraction
- [ ] Match resumes against job descriptions
- [ ] Calculate compatibility score
- [ ] Web interface for upload and matching
- [ ] Database of job descriptions

## Project Structure
```
resume_parser/
├── app.py                 # Flask web app
├── resume_extractor.py    # Parse resume files
├── skill_matcher.py       # Match skills to jobs
├── ai_extractor.py        # AI-powered data extraction
├── job_matcher.py         # Calculate compatibility
├── requirements.txt
├── sample_data/
│   └── job_descriptions.json
└── templates/
    ├── index.html
    └── results.html
```

## Key Concepts
- PDF/DOCX text extraction
- NLP for skill extraction
- Similarity algorithms
- Vector embeddings for semantic matching
- OpenAI for intelligent parsing

## Getting Started
1. Parse resume files
2. Extract structured data
3. Build job database
4. Implement matching algorithm
5. Create web interface

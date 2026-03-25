# Resume Parser & Job Matcher

[Back to Portfolio](../README.md)

Extract information from resumes and match the results against job descriptions in a way that can support recruiting workflows, screening tools, and structured candidate evaluation.

## Overview

This project explores how resume content can move from raw, inconsistent documents into structured data that is easier to search, compare, and score. It combines parsing, AI-assisted extraction, and matching logic in a web-based workflow.

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

## Why It Matters

- Turns unstructured resume content into usable structured data
- Creates a foundation for candidate scoring and job matching workflows
- Shows practical overlap between AI extraction, document handling, and product-oriented web development

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

## Related Projects

- [Tax Return AI Calculator](../tax_ai_calculator/README.md)
- [Workout Tracker + Hercules AI](../workout_tracker/README.md)

## Getting Started
1. Parse resume files
2. Extract structured data
3. Build job database
4. Implement matching algorithm
5. Create web interface

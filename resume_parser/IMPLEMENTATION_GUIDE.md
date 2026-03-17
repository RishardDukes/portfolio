# Resume Parser - Step-by-Step Implementation Guide

## Overview
We'll build this in 5 manageable steps:
1. **Parse text from resume files** (PDF, DOCX, TXT)
2. **Extract structured data** from raw text
3. **Implement job matching** logic
4. **Build the Flask web app**
5. **Connect the frontend**

---

## Step 1: Extract Text from Resume Files

### 1a. Extract from TXT (EASIEST - START HERE)
This one is already done! Text files are simple:
```python
def _extract_txt(self, file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
```

### 1b. Extract from PDF
Add this code to `resume_extractor.py`:
```python
def _extract_pdf(self, file_path: str) -> str:
    """Extract text from PDF using PyPDF2"""
    import PyPDF2
    
    text = ""
    with open(file_path, 'rb') as f:
        pdf_reader = PyPDF2.PdfReader(f)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    
    return text
```

### 1c. Extract from DOCX
Add this code to `resume_extractor.py`:
```python
def _extract_docx(self, file_path: str) -> str:
    """Extract text from DOCX using python-docx"""
    from docx import Document
    
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    
    return text
```

---

## Step 2: Parse Raw Text into Structured Data

### 2a. Create sample test file first
Create `test_resume.txt`:
```
John Smith
john.smith@email.com
(555) 123-4567
New York, NY

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years in Python and web development.

EXPERIENCE
Senior Developer - Tech Company (2020-2024)
- Led team of 5 developers
- Increased performance by 40%

Junior Developer - StartUp (2019-2020)
- Built REST APIs using Flask
- Implemented database schemas

EDUCATION
Bachelor of Science in Computer Science
University of California (2019)

SKILLS
Python, Flask, JavaScript, React, SQL, PostgreSQL, Git, Docker
```

### 2b. Implement the parsing function
Add to `resume_extractor.py`:
```python
import re

def _parse_text(self, text: str) -> Dict:
    """Parse raw text into structured resume data"""
    resume = {
        'name': self._extract_name(text),
        'email': self._extract_email(text),
        'phone': self._extract_phone(text),
        'location': self._extract_location(text),
        'summary': self._extract_summary(text),
        'experience': self._extract_experience(text),
        'education': self._extract_education(text),
        'skills': self._extract_skills(text),
    }
    return resume

def _extract_name(self, text: str) -> str:
    """Extract name (usually first line with capitalized words)"""
    lines = text.split('\n')
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if len(line) > 0 and len(line.split()) >= 2:
            if line.isupper() or (line[0].isupper() and ' ' in line):
                return line
    return None

def _extract_email(self, text: str) -> str:
    """Extract email using regex"""
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return emails[0] if emails else None

def _extract_phone(self, text: str) -> str:
    """Extract phone number"""
    phones = re.findall(r'\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
    return phones[0] if phones else None

def _extract_location(self, text: str) -> str:
    """Extract location (look for city, state pattern)"""
    pattern = r'(\w+),\s*([A-Z]{2})'  # City, ST format
    matches = re.findall(pattern, text)
    if matches:
        city, state = matches[0]
        return f"{city}, {state}"
    return None

def _extract_summary(self, text: str) -> str:
    """Extract professional summary section"""
    pattern = r'(?:PROFESSIONAL\s*SUMMARY|SUMMARY)(.*?)(?:EXPERIENCE|EDUCATION|SKILLS|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()[:200]  # First 200 chars
    return None

def _extract_experience(self, text: str) -> list:
    """Extract work experience"""
    experiences = []
    
    # Look for job title - company pattern
    pattern = r'([\w\s]+)\s*-\s*([\w\s]+)\s*\((\d{4})-(\d{4})\)'
    matches = re.findall(pattern, text)
    
    for title, company, start, end in matches:
        experiences.append({
            'title': title.strip(),
            'company': company.strip(),
            'start_year': int(start),
            'end_year': int(end)
        })
    
    return experiences

def _extract_education(self, text: str) -> list:
    """Extract education information"""
    educations = []
    
    # Look for degree patterns
    patterns = [
        r"(Bachelor|Master|PhD|Associate|Diploma)\s+(?:of\s+)?(\w+)",
        r"(B\.S\.|M\.S\.|B\.A\.|M\.A\.)\s+(?:in\s+)?(.+?)(?:\n|$)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for degree, field in matches:
            educations.append({
                'degree': degree.strip(),
                'field': field.strip()
            })
    
    return educations

def _extract_skills(self, text: str) -> list:
    """Extract skills section"""
    # Find SKILLS section
    pattern = r'(?:SKILLS|TECHNICAL\s+SKILLS)(.*?)(?:\n\n|EXPERIENCE|EDUCATION|$)'
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    
    if match:
        skills_text = match.group(1)
        # Split by comma, semicolon, or new line
        skills = re.split(r'[,\n;]', skills_text)
        skills = [s.strip() for s in skills if s.strip()]
        return skills
    
    return []
```

---

## Step 3: Test Step 2 First!

Before moving on, test your parsing:

```python
# Add this to the bottom of resume_extractor.py
if __name__ == "__main__":
    extractor = ResumeExtractor()
    
    # Test with sample resume
    resume_data = extractor.parse_resume("test_resume.txt")
    
    print("Name:", resume_data['name'])
    print("Email:", resume_data['email'])
    print("Phone:", resume_data['phone'])
    print("Skills:", resume_data['skills'])
    print("Experience:", resume_data['experience'])
```

Run it:
```powershell
python resume_extractor.py
```

**You should see parsed data!**

---

## Step 4: Implement Job Matching (Simplified)

Add to `job_matcher.py`:

```python
def calculate_compatibility(self, resume: Dict, job_description: str) -> Dict:
    """
    Simple compatibility score based on skill matching
    """
    resume_skills = set([s.lower() for s in resume['skills']])
    
    # Extract job skills from description
    job_skills_text = job_description.lower()
    common_skills = {
        'python', 'javascript', 'java', 'c++', 'sql',
        'react', 'flask', 'django', 'node', 'docker',
        'git', 'aws', 'azure', 'kubernetes', 'machine learning'
    }
    
    required_skills = common_skills & resume_skills
    
    # Calculate score
    if len(common_skills) > 0:
        match_percentage = (len(required_skills) / len(common_skills)) * 100
    else:
        match_percentage = 0
    
    return {
        'overall_score': int(match_percentage),
        'matching_skills': list(required_skills),
        'missing_skills': list(common_skills - resume_skills)
    }
```

---

## Your Walkthrough Tasks

### Phase 1 (Do First):
- [ ] Implement `_extract_pdf()` 
- [ ] Implement `_extract_docx()`
- [ ] Implement all the `_extract_*()` functions in Step 2
- [ ] Test with `test_resume.txt`

### Phase 2 (After Phase 1 works):
- [ ] Implement basic `calculate_compatibility()`
- [ ] Connect to Flask app's `/api/upload-resume` endpoint
- [ ] Test file upload

### Phase 3 (UI):
- [ ] Wire up the JavaScript in `templates/index.html`
- [ ] Test the full flow

---

## Common Issues & Fixes

**"ModuleNotFoundError: No module named 'PyPDF2'"**
→ Run: `pip install PyPDF2 python-docx`

**Resume data is empty**
→ Check your regex patterns match your resume format

**Skills not extracting**
→ Make sure your resume has a "SKILLS" section header

**Email not found**
→ Your resume might use different format (try: `user@example . com` won't work)

---

**Which phase are you ready to start with?** I recommend Phase 1 first!

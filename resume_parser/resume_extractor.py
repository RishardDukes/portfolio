"""
Resume Extractor Module
Parse resume files and extract structured information
"""

import os
from pathlib import Path
from typing import Dict
import re

class ResumeExtractor:
    """Extract information from resume files"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        Parse resume and extract information
        Returns: dict with structured resume data
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            text = self._extract_pdf(file_path)
        elif file_ext == '.docx':
            text = self._extract_docx(file_path)
        elif file_ext == '.txt':
            text = self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
        
        # TODO: Parse raw text into structured data
        structured_data = self._parse_text(text)
        
        return structured_data
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF"""
        import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        return text
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx"""
        from docx import Document
        
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text
    
    def _extract_txt(self, file_path: str) -> str:
        """Extract text from TXT"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

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
                if line[0].isupper():
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
    
    def extract_skills(self, resume_data: Dict) -> list:
        """Extract and normalize skills"""
        # TODO: Parse skills section
        # TODO: Normalize skill names
        # TODO: Return list of skills
        pass
    
    def extract_experience_years(self, resume_data: Dict) -> float:
        """Calculate total years of experience"""
        # TODO: Parse dates from experience
        # TODO: Calculate total years
        pass


if __name__ == "__main__":
    extractor = ResumeExtractor()
    
    # Test with sample resume
    resume_data = extractor.parse_resume("test_resume.txt")
    
    print("=" * 50)
    print("RESUME PARSING TEST RESULTS")
    print("=" * 50)
    print(f"Name: {resume_data['name']}")
    print(f"Email: {resume_data['email']}")
    print(f"Phone: {resume_data['phone']}")
    print(f"Location: {resume_data['location']}")
    print(f"Summary: {resume_data['summary']}")
    print(f"\nSkills: {resume_data['skills']}")
    print(f"\nExperience: {resume_data['experience']}")
    print(f"\nEducation: {resume_data['education']}")
    print("=" * 50)

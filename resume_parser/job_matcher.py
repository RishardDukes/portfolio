"""
Job Matcher Module
Match resumes against job descriptions
"""

from typing import Dict, List

class JobMatcher:
    """Match resumes to jobs based on skills and experience"""
    
    def __init__(self):
        # Common tech skills to match against
        self.common_skills = {
            'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin',
            'react', 'angular', 'vue', 'flask', 'django', 'spring', 'express', 'node',
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'docker', 'kubernetes', 'git', 'aws', 'azure', 'gcp', 'jenkins',
            'machine learning', 'tensorflow', 'pytorch', 'scikit-learn',
            'html', 'css', 'rest api', 'graphql', 'microservices',
            'agile', 'scrum', 'ci/cd'
        }
    
    def calculate_compatibility(self, resume: Dict, job_description: str) -> Dict:
        """
        Calculate compatibility score between resume and job
        Returns: dict with score and breakdown
        """
        
        # Get skills from resume
        resume_skills = set([s.lower() for s in resume.get('skills', [])])
        
        # Extract skills mentioned in job description
        job_text_lower = job_description.lower()
        found_job_skills = set()
        
        for skill in self.common_skills:
            if skill in job_text_lower:
                found_job_skills.add(skill)
        
        # Calculate matches
        matching_skills = resume_skills & found_job_skills
        missing_skills = found_job_skills - resume_skills
        
        # Calculate score based on what we found
        if len(found_job_skills) > 0:
            # If we found job requirements, score based on matches
            match_percentage = (len(matching_skills) / len(found_job_skills)) * 100
        elif len(resume_skills) > 0:
            # If we didn't find specific skills in job posting, 
            # give good score (can't analyze the job well)
            match_percentage = 75
        else:
            # No skills in either
            match_percentage = 0
        
        # Generate AI summary
        ai_summary = self._generate_summary(resume, matching_skills, missing_skills, match_percentage)
        
        return {
            'overall_score': int(match_percentage),
            'matching_skills': sorted(list(matching_skills)),
            'missing_skills': sorted(list(missing_skills)),
            'resume_has': len(resume_skills),
            'job_requires': len(found_job_skills),
            'ai_summary': ai_summary
        }
    
    def _generate_summary(self, resume: Dict, matching_skills: set, missing_skills: set, score: float) -> str:
        """Generate an AI-style summary of the match with detailed analysis"""
        name = resume.get('name', 'Candidate')
        
        # Overall assessment
        if score >= 80:
            assessment = "🟢 Excellent Match!"
            description = f"{name} is a strong fit for this role with solid qualifications."
        elif score >= 60:
            assessment = "🟡 Good Match"
            description = f"{name} has most required skills and would likely succeed in this position."
        elif score >= 40:
            assessment = "🟠 Moderate Match"
            description = f"{name} has some relevant experience but will need to develop specific skills."
        else:
            assessment = "🔴 Limited Match"
            description = f"{name} would benefit significantly from upskilling in key required areas."
        
        summary = f"{assessment}\n{description}\n\n"
        
        # STRENGTHS/GOODS
        summary += "═══ STRENGTHS ═══\n"
        if matching_skills:
            matching_list = sorted(list(matching_skills))
            summary += f"✅ You have expertise in: {', '.join(matching_list[:5])}"
            if len(matching_list) > 5:
                summary += f" and {len(matching_list) - 5} more"
            summary += "\n"
            summary += f"   This shows {score}% alignment with the job requirements.\n\n"
        else:
            summary += "⚠️  Limited overlap with required skills. Review below.\n\n"
        
        # EXPERIENCE
        years_exp = len(resume.get('experience', []))
        if years_exp > 0:
            summary += f"💼 Experience: {years_exp} documented position(s)\n"
            if years_exp >= 3:
                summary += "   Strong professional background\n"
            elif years_exp >= 1:
                summary += "   Emerging professional experience\n"
            summary += "\n"
        
        # WEAKNESSES/BADS
        summary += "═══ AREAS FOR IMPROVEMENT ═══\n"
        if missing_skills:
            missing_list = sorted(list(missing_skills))
            summary += f"❌ Missing skills: {', '.join(missing_list[:5])}"
            if len(missing_list) > 5:
                summary += f" and {len(missing_list) - 5} more"
            summary += "\n"
            summary += f"   These gaps account for {100 - score}% of the role's requirements.\n\n"
        else:
            summary += "✨ No missing required skills! You're well-aligned.\n\n"
        
        # SUGGESTIONS
        summary += "═══ RECOMMENDATIONS ═══\n"
        if missing_skills:
            missing_list = sorted(list(missing_skills))
            top_missing = missing_list[:3]
            summary += f"🎯 Priority Skills to Learn:\n"
            for i, skill in enumerate(top_missing, 1):
                summary += f"   {i}. {skill.capitalize()}\n"
            summary += f"\n"
            
            if score < 60:
                summary += "⏱️ Timeline: Estimate 3-6 months to become competitive\n\n"
            else:
                summary += "⏱️ Timeline: 1-3 months of targeted learning recommended\n\n"
        else:
            summary += "🚀 You're ready! Your skills match perfectly. Apply with confidence!\n\n"
        
        # FINAL VERDICT
        summary += "═══ FINAL VERDICT ═══\n"
        if score >= 80:
            summary += f"🎯 You have {score}% of required qualifications. Highly recommended for this role!"
        elif score >= 60:
            summary += f"🎯 You have {score}% of required qualifications. Good fit with minor skill gaps."
        elif score >= 40:
            summary += f"🎯 You have {score}% of required qualifications. Doable but focus on learning key skills first."
        else:
            summary += f"🎯 You have {score}% of required qualifications. Consider upskilling before applying."
        
        return summary
    
    def match_skills(self, resume_skills: List[str], job_skills: List[str]) -> Dict:
        """
        Match resume skills against job requirements
        Returns: matching and missing skills
        """
        
        # TODO: Normalize skill names
        # TODO: Use fuzzy matching for similar skills
        # TODO: Calculate match percentage
        
        matching = []
        missing = []
        
        # TODO: Find exact and similar matches
        
        return {
            'matching': matching,
            'missing': missing,
            'match_percentage': 0
        }
    
    def semantic_similarity(self, resume_text: str, job_text: str) -> float:
        """
        Calculate semantic similarity using TF-IDF
        Returns: similarity score 0-1
        """
        
        # TODO: Vectorize both texts
        # TODO: Calculate cosine similarity
        # TODO: Return score
        
        return 0.0
    
    def rank_candidates(self, resumes: List[Dict], job_description: Dict) -> List[Dict]:
        """
        Rank multiple resumes for a job
        Returns: sorted list by compatibility score
        """
        
        # TODO: Calculate score for each resume
        # TODO: Sort by score (descending)
        # TODO: Return ranked list
        
        return []


if __name__ == "__main__":
    matcher = JobMatcher()
    
    # Example usage:
    # score = matcher.calculate_compatibility(resume, job)
    # print(f"Compatibility: {score['overall_score']}%")

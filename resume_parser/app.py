"""
Flask Web Application
Resume Parser & Job Matcher Web UI
"""

from flask import Flask, render_template, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
from resume_extractor import ResumeExtractor
from job_matcher import JobMatcher

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize modules
extractor = ResumeExtractor()
matcher = JobMatcher()

# Store current resume in memory
current_resume = None

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    """Upload and parse resume"""
    global current_resume
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Parse resume
            resume = extractor.parse_resume(file_path)
            current_resume = resume
            
            return jsonify({
                'success': True,
                'resume': resume,
                'file_name': filename
            })
        
        finally:
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/match-job', methods=['POST'])
def match_job():
    """Match resume against job description"""
    global current_resume
    
    try:
        if current_resume is None:
            return jsonify({'error': 'No resume uploaded yet'}), 400
        
        data = request.get_json()
        job_description = data.get('job_description', '')
        
        if not job_description:
            return jsonify({'error': 'No job description provided'}), 400
        
        # Calculate compatibility
        result = matcher.calculate_compatibility(current_resume, job_description)
        
        return jsonify({
            'success': True,
            'compatibility_score': result['overall_score'],
            'matching_skills': result['matching_skills'],
            'missing_skills': result['missing_skills'],
            'ai_summary': result.get('ai_summary', '')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/resume', methods=['GET'])
def get_current_resume():
    """Get the current loaded resume"""
    if current_resume is None:
        return jsonify({'error': 'No resume uploaded'}), 400
    
    return jsonify({
        'success': True,
        'resume': current_resume
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

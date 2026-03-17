"""
Main Application Module
Flask/FastAPI web application for Tax Return AI Calculator
"""

from flask import Flask, render_template, request, jsonify
import os
import json
from datetime import datetime
from config import UPLOAD_FOLDER, SECRET_KEY, FLASK_DEBUG
from document_processor import DocumentProcessor
from ai_extractor import AIDocumentExtractor
from tax_calculator import TaxCalculator

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

# Initialize components
processor = DocumentProcessor()
calculator = TaxCalculator()

try:
    ai_extractor = AIDocumentExtractor()
except ValueError:
    ai_extractor = None
    print("Warning: OpenAI API key not configured. AI extraction disabled.")


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Handle document upload and extraction"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file temporarily
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        
        # Extract text from document
        document_text = processor.process_document(file_path)
        
        # Use AI to extract financial data
        if ai_extractor:
            extracted_data = ai_extractor.extract_financial_data(document_text)
        else:
            # Fallback: return raw text
            extracted_data = {'raw_text': document_text[:500]}
        
        # Clean up temporary file
        os.remove(file_path)
        
        return jsonify({
            'success': True,
            'extracted_data': extracted_data,
            'file_name': file.filename
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/calculate', methods=['POST'])
def calculate_tax():
    """Calculate tax based on provided financial data"""
    try:
        data = request.get_json()
        
        gross_income = float(data.get('gross_income', 0))
        deductions = float(data.get('deductions', 0))
        tax_withheld = float(data.get('tax_withheld', 0))
        credits = float(data.get('credits', 0))
        
        # Calculate refund
        result = calculator.calculate_refund(gross_income, tax_withheld, deductions, credits)
        
        return jsonify({
            'success': True,
            'calculation': result,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/status', methods=['GET'])
def status():
    """Check API status"""
    return jsonify({
        'status': 'running',
        'ai_enabled': ai_extractor is not None,
        'tax_year': 2024
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("Starting Tax Return AI Calculator...")
    print(f"AI Extraction: {'Enabled' if ai_extractor else 'Disabled'}")
    app.run(debug=FLASK_DEBUG, host='127.0.0.1', port=5000)

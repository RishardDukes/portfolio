# Tax Return AI Calculator

[Back to Portfolio](../README.md)

An intelligent system that analyzes financial documents and calculates tax returns using AI.

## Overview

This project focuses on a practical document-to-decision workflow: upload financial records, extract relevant tax information, and return a usable estimate through a web interface. It combines OCR, AI-assisted parsing, and tax calculation logic in a way that feels closer to a product than a script.

## Features
- 📄 Document parsing (PDFs, images, text files)
- 🤖 AI-powered income and expense extraction using OpenAI
- 💰 Automated tax calculation with 2024 tax brackets
- 🌐 Modern web interface with drag-and-drop uploads
- 📊 Instant refund or tax owed calculations

## Why It Matters

- Connects AI extraction to a concrete financial use case
- Demonstrates OCR, parsing, and decision logic in one workflow
- Shows how AI can support structured analysis rather than just text generation

## Quick Start

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- OpenAI API key (get one at https://platform.openai.com/account/api-keys)

### Installation

1. **Clone or download the project**
   ```bash
   cd tax_ai_calculator
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   OPENAI_MODEL=gpt-4
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the web interface**
   - Open your browser to `http://localhost:5000`
   - Upload tax documents or enter financial information manually
   - Click "Calculate Tax Return" to see results

## Project Structure
```
tax_ai_calculator/
├── app.py                 # Main Flask web application
├── tax_calculator.py      # Tax calculation engine
├── document_processor.py  # PDF/image/text parsing
├── ai_extractor.py        # OpenAI-powered data extraction
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore patterns
├── README.md              # This file
└── templates/
    └── index.html         # Web UI (HTML + CSS + JavaScript)
```

## Usage

### Via Web Interface
1. Drag and drop your tax documents (PDF, PNG, JPG, TXT)
2. Or manually enter:
   - Gross income
   - Deductions (standard or itemized)
   - Total tax withheld
   - Tax credits
3. Click "Calculate Tax Return"
4. View your refund or amount owed

### Via API (Python)
```python
from tax_calculator import TaxCalculator

calc = TaxCalculator()
result = calc.calculate_refund(
    gross_income=75000,
    total_withheld=10000,
    deductions=13850,
    credits=500
)
print(result)
# Output: {'tax_owed': 8950.0, 'total_withheld': 10000, 'refund': 1050.0}
```

## Configuration

Edit `.env` to customize:
```
OPENAI_API_KEY=your_key          # Required: OpenAI API key
OPENAI_MODEL=gpt-4               # GPT model to use
TAX_YEAR=2024                     # Tax year
STATE=CA                          # State code (future use)
FLASK_ENV=development             # development or production
FLASK_DEBUG=True                  # Enable debug mode
```

## Tax Calculations

The calculator uses **2024 federal tax brackets** for single filers:
- 10% on income up to $11,000
- 12% from $11,001 to $44,725
- 22% from $44,726 to $95,375
- 24% from $95,376 to $182,100
- 32% from $182,101 to $231,250
- 35% from $231,251 to $578,125
- 37% on income over $578,125

Standard deduction (2024): **$13,850** (single filer)

## Document Processing

Supported file formats:
- ✅ `.pdf` - PDF files (via PyPDF2)
- ✅ `.txt` - Plain text
- ✅ `.png`, `.jpg`, `.jpeg` - Images with OCR (requires Tesseract)

**Note:** For image OCR, install Tesseract:
- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Mac: `brew install tesseract`
- Linux: `apt-get install tesseract-ocr`

## AI Data Extraction

The AI extractor analyzes documents and automatically extracts:
- Gross income
- Income type (W-2, 1099, etc.)
- Tax withholdings
- Deductions
- Tax credits
- Business expenses

## Troubleshooting

**"OpenAI API key not found"**
- Ensure `.env` file exists in the project directory
- Verify `OPENAI_API_KEY` is set with a valid key

**"Module not found" errors**
- Run `pip install -r requirements.txt` again
- Make sure virtual environment is activated

**PDF extraction not working**
- Install PyPDF2: `pip install PyPDF2`

**Image OCR not working**
- Install Tesseract (see Document Processing section)

**Port 5000 already in use**
- Change port in `app.py` last line: `app.run(port=5001)`

## Security Notes
- 🔐 Never commit `.env` file to version control
- 🔐 API keys should never be shared or public
- 🔐 Use environment variables for sensitive data
- 🔐 `.gitignore` prevents accidental commits of `.env`

## Future Enhancements
- [ ] State tax calculations
- [ ] Multiple filing statuses (Married, Head of Household, etc.)
- [ ] Historical year calculations
- [ ] PDF export of results
- [ ] Database storage of calculations
- [ ] Multi-form processing (1040, Schedule C, etc.)
- [ ] Advanced deductions advisor

## License
Educational project for learning Python, Flask, and AI integration.

## Support
For issues or questions, check the troubleshooting section or review the code comments.

## Related Projects

- [AI Resume Parser](../resume_parser/README.md)
- [Workout Tracker + Hercules AI](../workout_tracker/README.md)


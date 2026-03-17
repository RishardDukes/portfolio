"""
AI Document Extractor
Uses OpenAI API to extract financial data from documents
"""

import os
from typing import Dict, List, Any


class AIDocumentExtractor:
    """Extracts financial data from documents using AI"""
    
    def __init__(self, api_key=None):
        """
        Initialize with OpenAI API key
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Import here to avoid dependency if not using
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            print("Warning: openai not installed. Install with: pip install openai")
            self.client = None
    
    def extract_financial_data(self, document_text: str) -> Dict[str, Any]:
        """
        Extract financial information from document text using AI
        Returns: Dict with income, expenses, deductions, etc.
        """
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")
        
        prompt = f"""
        Analyze the following financial document and extract the following information:
        - Gross income
        - Income type (W-2, 1099, etc.)
        - Tax withholdings
        - Deductions (itemized or standard recommendation)
        - Tax credits
        - Business expenses (if applicable)
        
        Return the data in a structured format (key: value pairs).
        
        Document text:
        {document_text}
        
        Extract and return:
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            # Parse response into dictionary
            extracted_data = self._parse_ai_response(response.choices[0].message.content)
            return extracted_data
        
        except Exception as e:
            print(f"Error extracting data with AI: {e}")
            return {}
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse AI response into structured data"""
        data = {}
        
        # Simple parsing - could be enhanced with regex or JSON
        lines = response_text.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                # Try to convert to numeric values
                try:
                    if '.' in value:
                        data[key] = float(value.replace('$', '').replace(',', ''))
                    else:
                        data[key] = int(value.replace('$', '').replace(',', ''))
                except ValueError:
                    data[key] = value
        
        return data


if __name__ == "__main__":
    # Example usage (requires API key)
    sample_text = """
    W-2 Form Summary
    Gross Wages: $65,000
    Federal Withholding: $9,000
    FICA Withholding: $4,972.50
    """
    
    try:
        extractor = AIDocumentExtractor()
        result = extractor.extract_financial_data(sample_text)
        print("Extracted Data:", result)
    except ValueError as e:
        print(f"Setup note: {e}")

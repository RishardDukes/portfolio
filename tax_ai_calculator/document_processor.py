"""
Document Processor Module
Handles parsing of PDFs, images, and other document formats
"""

import os
from typing import Optional


class DocumentProcessor:
    """Processes various document formats to extract text"""
    
    def __init__(self):
        self.supported_formats = ['.pdf', '.png', '.jpg', '.jpeg', '.txt']
    
    def process_document(self, file_path: str) -> str:
        """
        Process document and return extracted text
        Supports: PDF, images (with OCR), plain text
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.txt':
            return self._read_text_file(file_path)
        elif file_ext == '.pdf':
            return self._extract_pdf_text(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg']:
            return self._extract_image_text(file_path)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
    
    def _read_text_file(self, file_path: str) -> str:
        """Read plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading text file: {e}")
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            return text
        except ImportError:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        except Exception as e:
            raise IOError(f"Error extracting PDF text: {e}")
    
    def _extract_image_text(self, file_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except ImportError:
            raise ImportError("pytesseract or Pillow not installed. Install with: pip install pytesseract pillow")
        except Exception as e:
            raise IOError(f"Error extracting image text: {e}")
    
    def batch_process_documents(self, directory: str) -> dict:
        """Process all supported documents in a directory"""
        results = {}
        
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Not a directory: {directory}")
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                file_ext = os.path.splitext(filename)[1].lower()
                if file_ext in self.supported_formats:
                    try:
                        results[filename] = self.process_document(file_path)
                    except Exception as e:
                        results[filename] = f"Error: {str(e)}"
        
        return results


if __name__ == "__main__":
    processor = DocumentProcessor()
    
    # Example: process a text file with sample W-2 data
    sample_content = """
    W-2 Form
    Employee Name: John Doe
    Gross Wages: $75,000
    Federal Tax Withheld: $10,500
    """
    
    # Would use actual files in practice
    print("Document processor ready for:")
    print("- PDF files (.pdf)")
    print("- Images (.png, .jpg, .jpeg) - requires OCR")
    print("- Text files (.txt)")

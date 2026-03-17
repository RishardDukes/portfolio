"""
Configuration Module
Handles API keys, settings, and environment variables
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# Tax Calculation Settings
TAX_YEAR = int(os.getenv("TAX_YEAR", "2024"))
STATE = os.getenv("STATE", "CA")  # Default state for state tax calculations

# Web Server Configuration
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-in-production")

# File Upload Configuration
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt'}

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tax_calculations.db")

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

print(f"Configuration loaded for tax year {TAX_YEAR}")

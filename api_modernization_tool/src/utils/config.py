"""Configuration and environment utilities"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # AWS
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    USE_BEDROCK = os.getenv("USE_BEDROCK", "false").lower() == "true"
    
    # App
    APP_NAME = "API Modernization Tool"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Paths
    RAG_INDEX_PATH = "rag_indices"
    UPLOAD_FOLDER = "uploaded_files"
    
    @staticmethod
    def init_folders():
        """Initialize required folders"""
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.RAG_INDEX_PATH, exist_ok=True)

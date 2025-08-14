#!/usr/bin/env python3
"""
Production Configuration for ABC Housing Finance Assistant
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Production configuration class."""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

    # Pinecone Configuration
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east1-aws")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "pdf-documents")
    PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "housing-finance")

    # App Configuration
    APP_NAME = "ABC Housing Finance Assistant"
    APP_VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Chat Configuration
    MAX_CONTEXT_CHUNKS = int(os.getenv("MAX_CONTEXT_CHUNKS", "5"))
    CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.8"))

    # File Storage
    CHAT_STORAGE_DIR = os.getenv("CHAT_STORAGE_DIR", "chats")

    # Security
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        required_vars = ["OPENAI_API_KEY", "PINECONE_API_KEY"]

        missing_vars = [var for var in required_vars if not getattr(cls, var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return True


# Production configuration instance
config = Config()

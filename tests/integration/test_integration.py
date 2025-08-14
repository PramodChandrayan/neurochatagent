"""
Integration tests for the complete system workflow
"""

import os
import shutil
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from finance_chatbot import FinanceChatbot
from pdf_to_embeddings import PDFToEmbeddingsConverter


class TestSystemIntegration:
    """Integration tests for the complete system"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client for integration tests"""
        with patch("finance_chatbot.openai") as mock:
            mock.OpenAI.return_value = Mock()
            yield mock

    @pytest.fixture
    def mock_pinecone(self):
        """Mock Pinecone client for integration tests"""
        with patch("finance_chatbot.pinecone") as mock:
            mock.init.return_value = None
            mock.Index.return_value = Mock()
            yield mock

    def test_end_to_end_workflow(self, temp_dir, mock_openai, mock_pinecone):
        """Test complete end-to-end workflow"""
        # Mock OpenAI responses
        mock_openai.OpenAI.return_value.embeddings.create.return_value.data = [
            Mock(embedding=[0.1, 0.2, 0.3])
        ]
        mock_openai.OpenAI.return_value.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="AI response"))
        ]

        # Mock Pinecone responses
        mock_pinecone.Index.return_value.query.return_value.matches = [
            Mock(id="doc1", score=0.95, metadata={"text": "test content"})
        ]

        # Test PDF processing
        pdf_processor = PDFToEmbeddingsConverter(
            openai_api_key="test_key",
            pinecone_api_key="test_key",
        )

        # Test chatbot
        chatbot = FinanceChatbot(
            openai_api_key="test_key",
            pinecone_api_key="test_key",
        )

        # Test chat functionality
        result = chatbot.chat("test question")

        assert result["response"] == "AI response"
        assert result["context_chunks"] is not None
        assert result["context_sources"] is not None

    def test_error_recovery_workflow(self, temp_dir, mock_openai, mock_pinecone):
        """Test system recovery from errors"""
        # Mock OpenAI to fail first, then succeed
        mock_openai.OpenAI.return_value.embeddings.create.side_effect = [
            Exception("API error"),  # First call fails
            Mock(data=[Mock(embedding=[0.1, 0.2, 0.3])]),  # Second call succeeds
        ]

        chatbot = FinanceChatbot(
            openai_api_key="test_key",
            pinecone_api_key="test_key",
        )

        # First call should fail
        with pytest.raises(Exception):
            chatbot.generate_embeddings("test text")

        # Second call should succeed
        result = chatbot.generate_embeddings("test text")
        assert result == [0.1, 0.2, 0.3]

    def test_environment_configuration(self, temp_dir):
        """Test environment configuration loading"""
        # Test config loading
        from config import Config

        # Mock environment variables
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test_openai_key",
                "PINECONE_API_KEY": "test_pinecone_key",
                "PINECONE_ENVIRONMENT": "test_env",
                "PINECONE_INDEX_NAME": "test_index",
            },
        ):
            config = Config()
            assert config.openai.api_key == "test_openai_key"
            assert config.pinecone.api_key == "test_pinecone_key"

    def test_streamlit_integration(self, temp_dir):
        """Test Streamlit app integration"""
        # Test that Streamlit app can be imported
        try:
            import streamlit_app

            assert True  # Import successful
        except ImportError as e:
            pytest.fail(f"Failed to import streamlit_app: {e}")

    def test_docker_integration(self, temp_dir):
        """Test Docker configuration"""
        # Test Dockerfile exists and is valid
        dockerfile_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Dockerfile"
        )
        assert os.path.exists(dockerfile_path), "Dockerfile not found"

        # Test Dockerfile content
        with open(dockerfile_path, "r") as f:
            content = f.read()
            assert "FROM python:3.11-slim" in content
            assert "EXPOSE 8080" in content
            assert "streamlit run streamlit_app.py" in content

    def test_requirements_integration(self, temp_dir):
        """Test requirements.txt integration"""
        requirements_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "requirements.txt",
        )
        assert os.path.exists(requirements_path), "requirements.txt not found"

        # Test key dependencies
        with open(requirements_path, "r") as f:
            content = f.read()
            assert "streamlit" in content
            assert "openai" in content
            assert "pinecone" in content
            assert "python-dotenv" in content

    def test_configuration_validation(self, temp_dir):
        """Test configuration validation"""
        from config import Config

        # Test with missing required fields
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                Config().validate()

    def test_chat_session_persistence(self, temp_dir):
        """Test chat session persistence functionality"""
        # Test chat session functions
        from streamlit_app import (
            list_chat_sessions,
            load_chat_session,
            save_chat_session,
        )

        # Mock session data
        session_id = "test_session_123"
        messages = [{"role": "user", "content": "test question"}]
        title = "Test Session"

        # Test save and load
        save_chat_session(session_id, messages, title)
        loaded_session = load_chat_session(session_id)

        assert loaded_session["messages"] == messages
        assert loaded_session["title"] == title

    def test_health_check_endpoint(self, temp_dir):
        """Test health check functionality"""
        # Test that health check endpoint exists in Dockerfile
        dockerfile_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Dockerfile"
        )

        with open(dockerfile_path, "r") as f:
            content = f.read()
            assert "HEALTHCHECK" in content
            assert "curl -f http://localhost:8080/_stcore/health" in content

    def test_security_configuration(self, temp_dir):
        """Test security configuration"""
        # Test that no hardcoded secrets exist
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Check Python files for potential secrets
        python_files = []
        for root, dirs, files in os.walk(project_root):
            for file in files:
                if file.endswith(".py"):
                    python_files.append(os.path.join(root, file))

        # Check for common secret patterns
        secret_patterns = ["sk-", "pk_", "Bearer ", "Authorization:"]

        for file_path in python_files:
            with open(file_path, "r") as f:
                content = f.read()
                for pattern in secret_patterns:
                    assert (
                        pattern not in content
                    ), f"Potential secret found in {file_path}"

    def test_performance_metrics(self, temp_dir, mock_openai, mock_pinecone):
        """Test performance metrics and monitoring"""
        # Mock timing for performance testing
        import time

        chatbot = FinanceChatbot(
            openai_api_key="test_key",
            pinecone_api_key="test_key",
        )

        # Mock OpenAI response
        mock_openai.OpenAI.return_value.chat.completions.create.return_value.choices = [
            Mock(message=Mock(content="Performance test response"))
        ]

        # Test response time
        start_time = time.time()
        result = chatbot.chat("performance test question")
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 5.0  # Should respond within 5 seconds
        assert result["response"] == "Performance test response"


if __name__ == "__main__":
    pytest.main([__file__])

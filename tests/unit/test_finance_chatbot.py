"""
Unit tests for finance_chatbot.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from finance_chatbot import FinanceChatbot


class TestFinanceChatbot:
    """Test cases for FinanceChatbot class"""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client"""
        with patch("finance_chatbot.openai") as mock:
            mock.OpenAI.return_value = Mock()
            yield mock

    @pytest.fixture
    def mock_pinecone(self):
        """Mock Pinecone client"""
        with patch("finance_chatbot.pinecone") as mock:
            mock.init.return_value = None
            mock.Index.return_value = Mock()
            yield mock

    @pytest.fixture
    def chatbot(self, mock_openai, mock_pinecone):
        """Create chatbot instance with mocked dependencies"""
        return FinanceChatbot(
            openai_api_key="test_key",
            pinecone_api_key="test_key",
            pinecone_environment="test_env",
            pinecone_index_name="test_index",
        )

    def test_chatbot_initialization(self, chatbot):
        """Test chatbot initialization"""
        assert chatbot.openai_api_key == "test_key"
        assert chatbot.pinecone_index_name == "test_index"
        assert chatbot.openai_client is not None

    def test_generate_embeddings(self, chatbot):
        """Test embedding generation"""
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]

        chatbot.openai_client.embeddings.create.return_value = mock_response

        result = chatbot.generate_embeddings("test text")

        assert result == [0.1, 0.2, 0.3]
        chatbot.openai_client.embeddings.create.assert_called_once()

    def test_search_pinecone(self, chatbot):
        """Test Pinecone search functionality"""
        mock_query_response = Mock()
        mock_query_response.matches = [
            Mock(id="doc1", score=0.95, metadata={"text": "test content 1"}),
            Mock(id="doc2", score=0.85, metadata={"text": "test content 2"}),
        ]

        chatbot.pinecone_index.query.return_value = mock_query_response

        result = chatbot.search_pinecone([0.1, 0.2, 0.3], top_k=2)

        assert len(result) == 2
        assert result[0]["id"] == "doc1"
        assert result[0]["score"] == 0.95
        assert result[0]["text"] == "test content 1"

    def test_generate_response_with_context(self, chatbot):
        """Test response generation with context"""
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="AI response"))]

        chatbot.openai_client.chat.completions.create.return_value = mock_chat_response

        context = [{"text": "context 1"}, {"text": "context 2"}]
        result = chatbot.generate_response("test question", context)

        assert result == "AI response"
        chatbot.openai_client.chat.completions.create.assert_called_once()

    def test_generate_fallback_response(self, chatbot):
        """Test fallback response generation"""
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="Fallback response"))]

        chatbot.openai_client.chat.completions.create.return_value = mock_chat_response

        result = chatbot.generate_fallback_response("test question")

        assert result == "Fallback response"
        chatbot.openai_client.chat.completions.create.assert_called_once()

    def test_chat_with_context(self, chatbot):
        """Test chat method with context found"""
        # Mock search to return context
        chatbot.search_pinecone = Mock(
            return_value=[
                {"text": "context 1", "score": 0.9},
                {"text": "context 2", "score": 0.8},
            ]
        )

        # Mock response generation
        chatbot.generate_response = Mock(return_value="AI response with context")

        result = chatbot.chat("test question")

        assert result["response"] == "AI response with context"
        assert result["context"] is not None
        assert result["source"] is not None

    def test_chat_without_context(self, chatbot):
        """Test chat method without context"""
        # Mock search to return no context
        chatbot.search_pinecone = Mock(return_value=[])

        # Mock fallback response
        chatbot.generate_fallback_response = Mock(return_value="Fallback response")

        result = chatbot.chat("test question")

        assert result["response"] == "Fallback response"
        assert result["context"] is None
        assert result["source"] is None

    def test_error_handling(self, chatbot):
        """Test error handling in chat method"""
        # Mock search to raise exception
        chatbot.search_pinecone = Mock(side_effect=Exception("Search failed"))

        # Mock fallback response
        chatbot.generate_fallback_response = Mock(return_value="Error fallback")

        result = chatbot.chat("test question")

        assert result["response"] == "Error fallback"
        assert "error" in result

    def test_embedding_error_handling(self, chatbot):
        """Test error handling in embedding generation"""
        chatbot.openai_client.embeddings.create.side_effect = Exception("API error")

        with pytest.raises(Exception):
            chatbot.generate_embeddings("test text")

    def test_pinecone_search_error_handling(self, chatbot):
        """Test error handling in Pinecone search"""
        chatbot.pinecone_index.query.side_effect = Exception("Pinecone error")

        with pytest.raises(Exception):
            chatbot.search_pinecone([0.1, 0.2, 0.3])

    def test_response_generation_error_handling(self, chatbot):
        """Test error handling in response generation"""
        chatbot.openai_client.chat.completions.create.side_effect = Exception(
            "OpenAI error"
        )

        with pytest.raises(Exception):
            chatbot.generate_response("test question", [])

    def test_invalid_input_handling(self, chatbot):
        """Test handling of invalid inputs"""
        # Test empty question
        result = chatbot.chat("")
        assert "error" in result or result["response"] is not None

        # Test None question
        result = chatbot.chat(None)
        assert "error" in result or result["response"] is not None

    def test_context_filtering(self, chatbot):
        """Test context filtering based on relevance scores"""
        # Mock search with low relevance scores
        chatbot.search_pinecone = Mock(
            return_value=[
                {"text": "context 1", "score": 0.3},  # Low score
                {"text": "context 2", "score": 0.2},  # Very low score
            ]
        )

        chatbot.generate_fallback_response = Mock(
            return_value="Fallback due to low scores"
        )

        result = chatbot.chat("test question")

        # Should use fallback due to low relevance scores
        assert result["response"] == "Fallback due to low scores"

    def test_metadata_extraction(self, chatbot):
        """Test metadata extraction from search results"""
        mock_query_response = Mock()
        mock_query_response.matches = [
            Mock(
                id="doc1",
                score=0.95,
                metadata={"text": "test content", "filename": "test.pdf", "page": 1},
            )
        ]

        chatbot.pinecone_index.query.return_value = mock_query_response
        chatbot.generate_response = Mock(return_value="AI response")

        result = chatbot.chat("test question")

        assert result["source"]["filename"] == "test.pdf"
        assert result["source"]["page"] == 1


if __name__ == "__main__":
    pytest.main([__file__])

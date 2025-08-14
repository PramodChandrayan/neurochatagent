"""
Unit tests for finance_chatbot.py
"""

import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

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
        )

    def test_chatbot_initialization(self, chatbot):
        """Test chatbot initialization"""
        assert chatbot.openai_api_key == "test_key"
        assert chatbot.index_name == "pdf-documents"
        assert chatbot.client is not None

    def test_search_relevant_context(self, chatbot):
        """Test context search functionality"""
        # Mock the embeddings.create method
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3])]
        chatbot.client.embeddings.create.return_value = mock_response

        # Mock the Pinecone index
        mock_index = Mock()
        mock_query_response = Mock()
        mock_query_response.matches = [
            Mock(
                score=0.9,
                metadata={"text": "test content", "chunk_index": 0, "source": "pdf"},
            )
        ]
        mock_index.query.return_value = mock_query_response

        # Mock the Pinecone Index directly on the chatbot instance
        chatbot.pc.Index = Mock(return_value=mock_index)
        result = chatbot.search_relevant_context("test query")

        assert len(result) == 1
        assert result[0]["text"] == "test content"
        assert result[0]["score"] == 0.9

    def test_generate_response(self, chatbot):
        """Test response generation with context"""
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="AI response"))]

        chatbot.client.chat.completions.create.return_value = mock_chat_response

        context = [{"text": "context 1", "score": 0.9}, {"text": "context 2", "score": 0.8}]
        result = chatbot.generate_response("test question", context)

        assert result == "AI response"
        chatbot.client.chat.completions.create.assert_called_once()

    def test_generate_fallback_response(self, chatbot):
        """Test fallback response generation"""
        mock_chat_response = Mock()
        mock_chat_response.choices = [Mock(message=Mock(content="Fallback response"))]

        chatbot.client.chat.completions.create.return_value = mock_chat_response

        result = chatbot.generate_fallback_response("test question")

        assert result == "Fallback response"
        chatbot.client.chat.completions.create.assert_called_once()

    def test_chat_with_context(self, chatbot):
        """Test chat method with context found"""
        # Mock search to return context
        chatbot.search_relevant_context = Mock(
            return_value=[
                {"text": "context 1", "score": 0.9, "source": "doc1"},
                {"text": "context 2", "score": 0.8, "source": "doc2"},
            ]
        )

        # Mock response generation
        chatbot.generate_response = Mock(return_value="AI response with context")

        result = chatbot.chat("test question")

        assert result["response"] == "AI response with context"
        assert result["context_chunks"] is not None
        assert result["context_sources"] is not None

    def test_chat_without_context(self, chatbot):
        """Test chat method without context"""
        # Mock search to return no context
        chatbot.search_relevant_context = Mock(return_value=[])

        # Mock fallback response
        chatbot.generate_fallback_response = Mock(return_value="Fallback response")

        result = chatbot.chat("test question")

        assert result["response"] == "Fallback response"
        assert result["context_chunks"] == 0
        assert result["context_sources"] == []

    def test_error_handling(self, chatbot):
        """Test error handling in chat method"""
        # Mock search to raise exception
        chatbot.search_relevant_context = Mock(side_effect=Exception("Search failed"))

        result = chatbot.chat("test question")

        # Should return error response, not raise exception
        assert "error" in result
        assert "Search failed" in result["response"]

    def test_embedding_error_handling(self, chatbot):
        """Test error handling in embedding generation"""
        chatbot.client.embeddings.create.side_effect = Exception("API error")

        # Should return empty list, not raise exception
        result = chatbot.search_relevant_context("test text")
        assert result == []

    def test_pinecone_search_error_handling(self, chatbot):
        """Test error handling in Pinecone search"""
        # Mock the Pinecone Index to raise an exception
        mock_index = Mock()
        mock_index.query.side_effect = Exception("Pinecone error")
        chatbot.pc.Index = Mock(return_value=mock_index)

        # Should return empty list, not raise exception
        result = chatbot.search_relevant_context("test query")
        assert result == []

    def test_response_generation_error_handling(self, chatbot):
        """Test error handling in response generation"""
        chatbot.client.chat.completions.create.side_effect = Exception(
            "OpenAI error"
        )

        # Should return error message, not raise exception
        result = chatbot.generate_response("test question", [])
        assert "error" in result.lower()

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
        chatbot.search_relevant_context = Mock(
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
        # Mock search to return context with metadata
        chatbot.search_relevant_context = Mock(
            return_value=[
                {
                    "text": "test content",
                    "score": 0.95,
                    "chunk_index": 0,
                    "source": "test.pdf"
                }
            ]
        )
        chatbot.generate_response = Mock(return_value="AI response")

        result = chatbot.chat("test question")

        assert result["context_sources"] == ["test.pdf"]


if __name__ == "__main__":
    pytest.main([__file__])

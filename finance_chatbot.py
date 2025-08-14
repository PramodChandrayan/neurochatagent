#!/usr/bin/env python3
"""
Finance Assistant Chatbot

This chatbot uses OpenAI's chat completion API and Pinecone vector database
to answer questions about finance documents. It retrieves relevant context
from the vector index and generates accurate, contextual responses.
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import openai
import pinecone
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FinanceChatbot:
    """Chatbot that answers finance questions using vector search and OpenAI."""

    def __init__(self, openai_api_key: str = None, pinecone_api_key: str = None):
        """
        Initialize the chatbot with API keys.

        Args:
            openai_api_key: OpenAI API key for chat completion
            pinecone_api_key: Pinecone API key for vector search
        """
        # Load environment variables
        load_dotenv()

        # Set API keys
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.pinecone_api_key = pinecone_api_key or os.getenv("PINECONE_API_KEY")

        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required.")
        if not self.pinecone_api_key:
            raise ValueError("Pinecone API key is required.")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)

        # Initialize Pinecone
        self.pc = pinecone.Pinecone(api_key=self.pinecone_api_key)

        # Chatbot configuration
        self.index_name = "pdf-documents"
        self.namespace = "housing-finance"
        self.max_context_chunks = 5
        self.chunk_threshold = 0.7  # Similarity threshold for relevant chunks

        # System prompt for the chatbot
        self.system_prompt = """You are a knowledgeable finance assistant specializing in housing finance and home loans. 
You have access to detailed information about ABC Housing Finance Limited and their products.

Your role is to:
1. Answer questions about housing finance products, loan types, and services
2. Provide accurate information based on the available documents
3. Explain complex financial concepts in simple terms
4. Help users understand loan options and requirements
5. Be helpful, professional, and informative

Always base your answers on the provided context from the documents. If you don't have enough information to answer a question accurately, say so rather than making assumptions.

Current focus areas: Home loans, construction loans, plot loans, renovation loans, balance transfers, and housing finance regulations."""

    def search_relevant_context(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search Pinecone for relevant context based on the user's query.

        Args:
            query: User's question
            top_k: Number of top results to return

        Returns:
            List of relevant context chunks with metadata
        """
        try:
            # Generate embedding for the query
            query_embedding = (
                self.client.embeddings.create(
                    input=query, model="text-embedding-ada-002"
                )
                .data[0]
                .embedding
            )

            # Search Pinecone index
            index = self.pc.Index(self.index_name)
            search_results = index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.namespace,
                include_metadata=True,
            )

            # Extract relevant context
            relevant_chunks = []
            for match in search_results.matches:
                if match.score >= self.chunk_threshold:
                    relevant_chunks.append(
                        {
                            "text": match.metadata.get("text", ""),
                            "score": match.score,
                            "chunk_index": match.metadata.get("chunk_index", 0),
                            "source": match.metadata.get("source", "pdf_processing"),
                        }
                    )

            logger.info(
                f"Found {len(relevant_chunks)} relevant chunks for query: {query[:50]}..."
            )
            return relevant_chunks

        except Exception as e:
            logger.error(f"Error searching Pinecone: {str(e)}")
            return []

    def format_context_for_prompt(self, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Format context chunks into a prompt-friendly string.

        Args:
            context_chunks: List of relevant context chunks

        Returns:
            Formatted context string
        """
        if not context_chunks:
            return "No relevant context found."

        context_parts = []
        for i, chunk in enumerate(context_chunks, 1):
            context_parts.append(
                f"Context {i} (Relevance: {chunk['score']:.3f}):\n{chunk['text']}\n"
            )

        return "\n".join(context_parts)

    def generate_response(
        self, user_question: str, context_chunks: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a response using OpenAI's chat completion API.

        Args:
            user_question: User's question
            context_chunks: Relevant context chunks

        Returns:
            Generated response
        """
        try:
            # Format the context
            context_text = self.format_context_for_prompt(context_chunks)

            # Create the user message with context
            user_message = f"""Based on the following context, please answer this question: {user_question}

Context:
{context_text}

Please provide a comprehensive and accurate answer based on the context provided. If the context doesn't contain enough information to fully answer the question, acknowledge this and provide what information you can."""

            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"I apologize, but I encountered an error while generating a response: {str(e)}"

    def chat(self, user_question: str) -> Dict[str, Any]:
        """
        Main chat method that processes a user question and returns a response.

        Args:
            user_question: User's question

        Returns:
            Dictionary containing response and metadata
        """
        try:
            logger.info(f"Processing question: {user_question[:100]}...")

            # Search for relevant context
            context_chunks = self.search_relevant_context(
                user_question, self.max_context_chunks
            )

            # Determine if we should use RAG or fallback to general knowledge
            use_rag = len(context_chunks) > 0 and any(
                chunk["score"] > 0.8 for chunk in context_chunks
            )

            if use_rag:
                # Generate response using RAG
                response = self.generate_response(user_question, context_chunks)
                response_source = "document_context"
            else:
                # Fallback to general financial knowledge
                response = self.generate_fallback_response(user_question)
                response_source = "general_knowledge"

            # Prepare result
            result = {
                "question": user_question,
                "response": response,
                "context_chunks": len(context_chunks) if use_rag else 0,
                "context_sources": (
                    [chunk["source"] for chunk in context_chunks] if use_rag else []
                ),
                "timestamp": datetime.now().isoformat(),
                "relevant_chunks": context_chunks[:2] if use_rag else [],
                "response_source": response_source,
                "confidence": "high" if use_rag else "medium",
            }

            logger.info(
                f"Generated response using {response_source} with {len(context_chunks)} context chunks"
            )
            return result

        except Exception as e:
            logger.error(f"Error in chat method: {str(e)}")
            return {
                "question": user_question,
                "response": f"I apologize, but I encountered an error: {str(e)}",
                "context_chunks": 0,
                "context_sources": [],
                "timestamp": datetime.now().isoformat(),
                "relevant_chunks": [],
                "error": str(e),
                "response_source": "error",
                "confidence": "low",
            }

    def generate_fallback_response(self, user_question: str) -> str:
        """
        Generate a response using general financial knowledge when RAG context is insufficient.

        Args:
            user_question: User's question

        Returns:
            Generated response using general knowledge
        """
        try:
            # Enhanced system prompt for fallback scenarios
            fallback_prompt = """You are a knowledgeable finance assistant with expertise in housing finance, home loans, and general financial concepts. 

When the user asks questions that aren't covered in your specific documents, you should:

1. Provide helpful, accurate financial information based on general knowledge
2. Explain concepts clearly and professionally
3. Offer general guidance while being transparent about limitations
4. Suggest consulting with financial professionals for specific advice
5. Focus on educational content and best practices

Current question: {question}

Please provide a helpful response based on your general financial knowledge. Be clear about what you know and what might require professional consultation."""

            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": fallback_prompt.format(question=user_question),
                    },
                    {"role": "user", "content": user_question},
                ],
                max_tokens=800,
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.error(f"Error generating fallback response: {str(e)}")
            return f"I apologize, but I'm having trouble generating a response right now. Please try rephrasing your question or contact a financial professional for assistance."

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get chat history (placeholder for future implementation)."""
        return []

    def clear_chat_history(self):
        """Clear chat history (placeholder for future implementation)."""
        pass


def interactive_chat():
    """Interactive chat interface for testing the chatbot."""
    try:
        print("🏦 Welcome to the Finance Assistant Chatbot!")
        print(
            "I can help you with questions about housing finance, home loans, and ABC Housing Finance Limited."
        )
        print("Type 'quit' or 'exit' to end the conversation.\n")

        # Initialize chatbot
        chatbot = FinanceChatbot()
        print("✅ Chatbot initialized successfully!")
        print("🔍 Connected to Pinecone index: pdf-documents")
        print("🤖 Using OpenAI GPT-4 for responses\n")

        chat_session = []

        while True:
            try:
                # Get user input
                user_input = input("\n💬 You: ").strip()

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("\n👋 Thank you for using the Finance Assistant Chatbot!")
                    break

                if not user_input:
                    print("Please enter a question.")
                    continue

                # Process the question
                print("🤔 Thinking...")
                result = chatbot.chat(user_input)

                # Display response
                print(f"\n🤖 Assistant: {result['response']}")

                # Show context info
                if result["context_chunks"] > 0:
                    print(
                        f"\n📚 Used {result['context_chunks']} relevant document chunks"
                    )
                    if result["relevant_chunks"]:
                        print("📖 Top relevant context:")
                        for i, chunk in enumerate(result["relevant_chunks"], 1):
                            print(
                                f"   {i}. {chunk['text'][:100]}... (Score: {chunk['score']:.3f})"
                            )
                else:
                    print("\n⚠️  No relevant context found in documents")

                # Store in session
                chat_session.append(result)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")

        # Save chat session
        if chat_session:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_session_{timestamp}.json"
            with open(filename, "w") as f:
                json.dump(chat_session, f, indent=2)
            print(f"\n💾 Chat session saved to: {filename}")

    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {str(e)}")
        print("Please check your API keys and Pinecone connection.")


def test_chatbot():
    """Test the chatbot with sample questions."""
    try:
        print("🧪 Testing Finance Chatbot with Sample Questions\n")

        chatbot = FinanceChatbot()

        test_questions = [
            "What home loan products does ABC Housing Finance offer?",
            "What are the interest rates for home loans?",
            "How does the construction loan work?",
            "What is a plot loan and how does it work?",
            "Can I transfer my existing home loan to ABC Housing Finance?",
        ]

        for i, question in enumerate(test_questions, 1):
            print(f"\n{'='*60}")
            print(f"Test {i}: {question}")
            print(f"{'='*60}")

            result = chatbot.chat(question)

            print(f"🤖 Response: {result['response']}")
            print(f"📚 Context chunks used: {result['context_chunks']}")

            if result["context_chunks"] > 0:
                print("📖 Relevant context:")
                for chunk in result["relevant_chunks"][:2]:
                    print(f"   - {chunk['text'][:80]}... (Score: {chunk['score']:.3f})")

            print()

        print("✅ Chatbot testing completed!")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_chatbot()
    else:
        interactive_chat()

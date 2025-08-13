#!/usr/bin/env python3
"""
PDF to Pinecone Embeddings Converter

This script converts PDF documents to vectorized embeddings that can be used
with Pinecone vector database for semantic search and retrieval.
"""

import os
import logging
import re
from pathlib import Path
from typing import List, Dict, Any
import json

# PDF processing
import PyPDF2

# Embeddings and vector operations
import openai
import pinecone
import numpy as np
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleTextSplitter:
    """Simple text splitter that splits text into chunks with overlap."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with specified size and overlap."""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this isn't the last chunk, try to break at a sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters of the chunk
                search_start = max(start, end - 100)
                sentence_end = text.rfind('.', search_start, end)
                if sentence_end > start and sentence_end > end - 200:
                    end = sentence_end + 1
                else:
                    # Look for paragraph breaks
                    paragraph_end = text.rfind('\n\n', search_start, end)
                    if paragraph_end > start and paragraph_end > end - 200:
                        end = paragraph_end + 2
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position, accounting for overlap
            start = max(start + 1, end - self.chunk_overlap)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks

class PDFToEmbeddingsConverter:
    """Converts PDF documents to vectorized embeddings for Pinecone."""
    
    def __init__(self, openai_api_key: str = None, pinecone_api_key: str = None):
        """
        Initialize the converter with API keys.
        
        Args:
            openai_api_key: OpenAI API key for generating embeddings
            pinecone_api_key: Pinecone API key for vector database operations
        """
        # Load environment variables
        load_dotenv()
        
        # Set API keys
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = pinecone_api_key or os.getenv('PINECONE_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Initialize Pinecone if API key is provided
        if self.pinecone_api_key:
            self.pc = pinecone.Pinecone(api_key=self.pinecone_api_key)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content as string
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                logger.info(f"Successfully extracted text from {pdf_path} ({len(pdf_reader.pages)} pages)")
                return text.strip()
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """
        Split text into chunks for embedding generation.
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
            
        Returns:
            List of text chunks
        """
        try:
            text_splitter = SimpleTextSplitter(chunk_size, chunk_overlap)
            chunks = text_splitter.split_text(text)
            logger.info(f"Text chunked into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise
    
    def generate_embeddings(self, text_chunks: List[str], model: str = "text-embedding-ada-002") -> List[List[float]]:
        """
        Generate embeddings for text chunks using OpenAI's embedding model.
        
        Args:
            text_chunks: List of text chunks to embed
            model: OpenAI embedding model to use
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            for i, chunk in enumerate(text_chunks):
                response = self.client.embeddings.create(
                    input=chunk,
                    model=model
                )
                embedding = response.data[0].embedding
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Generated embeddings for {i + 1}/{len(text_chunks)} chunks")
            
            logger.info(f"Successfully generated embeddings for {len(text_chunks)} chunks")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def save_embeddings_to_file(self, embeddings: List[List[float]], text_chunks: List[str], 
                               output_file: str = "embeddings.json") -> None:
        """
        Save embeddings and text chunks to a JSON file.
        
        Args:
            embeddings: List of embedding vectors
            text_chunks: List of text chunks
            output_file: Output file path
        """
        try:
            data = {
                "embeddings": embeddings,
                "text_chunks": text_chunks,
                "metadata": {
                    "total_chunks": len(text_chunks),
                    "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                    "model_used": "text-embedding-ada-002"
                }
            }
            
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Embeddings saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error saving embeddings: {str(e)}")
            raise
    
    def upload_to_pinecone(self, embeddings: List[List[float]], text_chunks: List[str], 
                          index_name: str, namespace: str = "default") -> None:
        """
        Upload embeddings to Pinecone vector database.
        
        Args:
            embeddings: List of embedding vectors
            text_chunks: List of text chunks
            index_name: Name of the Pinecone index
            namespace: Namespace within the index
        """
        if not self.pinecone_api_key:
            logger.warning("Pinecone API key not provided. Skipping upload to Pinecone.")
            return
        
        try:
            # Check if index exists, create if not
            if index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {index_name}")
                self.pc.create_index(
                    name=index_name,
                    dimension=len(embeddings[0]),
                    metric="cosine",
                    spec=pinecone.ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    )
                )
            
            # Get index
            index = self.pc.Index(index_name)
            
            # Prepare vectors for upload
            vectors = []
            for i, (embedding, chunk) in enumerate(zip(embeddings, text_chunks)):
                vector_data = {
                    "id": f"chunk_{i}",
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "chunk_index": i,
                        "source": "pdf_processing"
                    }
                }
                vectors.append(vector_data)
            
            # Upload in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                index.upsert(vectors=batch, namespace=namespace)
                logger.info(f"Uploaded batch {i//batch_size + 1}/{(len(vectors) + batch_size - 1)//batch_size}")
            
            logger.info(f"Successfully uploaded {len(vectors)} vectors to Pinecone index '{index_name}'")
            
        except Exception as e:
            logger.error(f"Error uploading to Pinecone: {str(e)}")
            raise
    
    def process_pdf(self, pdf_path: str, chunk_size: int = 1000, chunk_overlap: int = 200,
                   save_to_file: bool = True, upload_to_pinecone: bool = False,
                   index_name: str = "pdf-embeddings", namespace: str = "default") -> Dict[str, Any]:
        """
        Complete pipeline to process PDF and generate embeddings.
        
        Args:
            pdf_path: Path to the PDF file
            chunk_size: Maximum size of each text chunk
            chunk_overlap: Overlap between consecutive chunks
            save_to_file: Whether to save embeddings to file
            upload_to_pinecone: Whether to upload to Pinecone
            index_name: Pinecone index name
            namespace: Pinecone namespace
            
        Returns:
            Dictionary containing processing results
        """
        try:
            logger.info(f"Starting PDF processing for: {pdf_path}")
            
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            # Chunk the text
            chunks = self.chunk_text(text, chunk_size, chunk_overlap)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            # Save to file if requested
            if save_to_file:
                output_file = f"{Path(pdf_path).stem}_embeddings.json"
                self.save_embeddings_to_file(embeddings, chunks, output_file)
            
            # Upload to Pinecone if requested
            if upload_to_pinecone:
                self.upload_to_pinecone(embeddings, chunks, index_name, namespace)
            
            results = {
                "pdf_path": pdf_path,
                "total_pages": len(PyPDF2.PdfReader(open(pdf_path, 'rb')).pages),
                "total_chunks": len(chunks),
                "embedding_dimension": len(embeddings[0]) if embeddings else 0,
                "chunks": chunks,
                "embeddings": embeddings
            }
            
            logger.info(f"PDF processing completed successfully for: {pdf_path}")
            return results
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise


def main():
    """Main function to demonstrate usage."""
    try:
        # Initialize converter
        converter = PDFToEmbeddingsConverter()
        
        # Process the PDF in the current directory
        pdf_files = list(Path('.').glob('*.pdf'))
        
        if not pdf_files:
            logger.warning("No PDF files found in current directory")
            return
        
        for pdf_file in pdf_files:
            logger.info(f"Processing: {pdf_file}")
            
            # Process PDF and generate embeddings
            results = converter.process_pdf(
                str(pdf_file),
                chunk_size=1000,
                chunk_overlap=200,
                save_to_file=True,
                upload_to_pinecone=True,  # Upload to Pinecone
                index_name="pdf-documents",
                namespace="housing-finance"
            )
            
            logger.info(f"Successfully processed {pdf_file}")
            logger.info(f"Generated {results['total_chunks']} chunks with {results['embedding_dimension']}-dimensional embeddings")
    
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise


if __name__ == "__main__":
    main()

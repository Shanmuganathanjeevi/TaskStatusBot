"""
QA Engine: Question Answering with Groq
========================================

This module handles:
1. Retrieving relevant chunks (from DocumentProcessor)
2. Creating a prompt
3. Sending to Groq API
4. Returning the answer

Think of it like:
- You ask a question
- We find the 3 most relevant parts of the document
- We ask a smart AI (Groq) to answer using only those parts
- We return the answer to you
"""

import os
from groq import Groq
from document_processor import DocumentProcessor


class QAEngine:
    """
    Question Answering Engine using Groq API.
    
    Attributes:
    - processor: DocumentProcessor instance (for retrieval)
    - client: Groq API client
    - model: Which model to use (mixtral-8x7b-32768)
    """
    
    def __init__(self, processor: DocumentProcessor):
        """
        Initialize the QA Engine.
        
        Args:
            processor: DocumentProcessor instance
        
        What happens:
        1. Store the processor (for chunk retrieval)
        2. Initialize Groq client (connects to Groq servers)
        3. Load API key from environment
        """
        self.processor = processor
        
        # Remember: we stored this in .env file            
        # Try to load from .env first, then environment variable
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass  # dotenv not available or .env file issue - use env var
        
        # Get API key from environment variable
        api_key = os.getenv('GROQ_API_KEY')
        
        # Validate that API key exists
        if not api_key:
            raise ValueError(
                "❌ Error: GROQ_API_KEY not found!\n"
                "Please set it in your .env file or as an environment variable."
            )
        
        # Initialize Groq client
        # This client handles all communication with Groq servers
        self.client = Groq(api_key=api_key)
        
        # Which model to use
        # mixtral-8x7b-32768 is:
        # - Fast (optimized by Groq)
        # - Free (up to 500 calls/month)
        # - Powerful (8x7B means 56 billion parameters)
        self.model = "llama-3.1-8b-instant"
    
    def create_prompt(self, question: str, context_chunks: list) -> str:
        """
        Create a well-structured prompt for Groq.
        
        Args:
            question: User's question
            context_chunks: Relevant document chunks
        
        Returns:
            A formatted prompt string
        
        Why this matters:
        - Groq is a language model, it works on prompts
        - A good prompt = good answer
        - We structure it to be clear and actionable
        
        Prompt structure:
        1. System message: "You are a helpful assistant..."
        2. Context: "Here's the relevant document:"
        3. Question: "Answer this question based only on the context"
        
        This is called "prompt engineering"
        """
        # Join chunks into one context block
        context = "\n---\n".join(context_chunks)
        
        # Create the prompt
        # We use a clear structure to guide the LLM
        prompt = f"""You are a helpful assistant that answers questions about documents.

DOCUMENT CONTEXT:
---
{context}
---

QUESTION:
{question}

INSTRUCTIONS:
1. Answer based ONLY on the document context above.
2. If the answer is not in the context, say "I cannot find this information in the document."
3. Be concise and clear."""
        
        return prompt
    
    def answer(self, question: str) -> str:
        """
        Answer a question about tasks.
        
        Args:
            question: User's question
        
        Returns:
            Answer string (no sources, just the answer)
        """
        try:
            # Retrieve relevant chunks
            chunks = self.processor.search(question, top_k=3)
            
            if not chunks:
                return "I don't have information about that in the task database."
            
            # Create prompt
            prompt = self.create_prompt(question, chunks)
            
            # Call Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
            )
            
            # Extract and return answer only
            answer_text = response.choices[0].message.content
            return answer_text
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return f"Error getting answer: {str(e)}"
    
    def answer_with_context(self, question: str) -> dict:
        """
        Answer a question and show which chunks were used.
        
        Args:
            question: User's question
        
        Returns:
            Dictionary with 'answer' and 'sources' (chunks used)
        
        Why have this function?
        - Transparency: users can see which parts were used
        - Debugging: helps us understand why the AI answered something
        - Trust: showing sources makes answers more credible
        
        This is useful for GitHub demos - shows your thinking!
        """
        # Retrieve chunks
        chunks = self.processor.search(question, top_k=3)
        
        if not chunks:
            return {
                "answer": "No relevant information found in the document.",
                "sources": []
            }
        
        # Create prompt and get answer
        prompt = self.create_prompt(question, chunks)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=512,
                temperature=0.7,
            )
            
            answer_text = response.choices[0].message.content
            
            # Return answer with sources
            return {
                "answer": answer_text,
                "sources": chunks,
                "sources_count": len(chunks)
            }
        
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }


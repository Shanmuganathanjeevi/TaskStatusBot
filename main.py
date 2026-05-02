"""
TasksStatusBot: Smart Document Q&A System
=====================================

This is the main file you run to interact with TasksStatusBot.

What it does:
1. Loads your document
2. Processes it (chunks + embeddings)
3. Answers your questions using Groq AI

How to run:
    python main.py
"""

import os
import sys
from pathlib import Path
from document_processor import DocumentProcessor
from qa_engine import QAEngine


def print_header():
    """Print a nice welcome message"""
    print("\n" + "="*60)
    print("  TasksStatusBot: Smart Document Q&A System")
    print("="*60 + "\n")


def get_document_path():
    """
    Ask the user which document to use.
    
    Why this function:
    - Makes the CLI user-friendly
    - Validates the file exists
    """
    print("Step 1: Load Your Document")
    print("-" * 40)
    
    # Ask user for file path
    file_path = input("Enter document path (e.g., document.txt): ").strip()
    
    # Check if file exists
    if not Path(file_path).exists():
        print(f"❌ Error: File '{file_path}' not found!")
        sys.exit(1)
    
    print(f"✅ Loaded: {file_path}\n")
    return file_path


def initialize_system(document_path):
    """
    Initialize the TasksStatusBot system.
    
    This function:
    1. Reads your document
    2. Breaks it into chunks (pieces)
    3. Converts chunks to embeddings (numbers)
    4. Stores them in ChromaDB (a database)
    
    This happens once per document.
    """
    print("Step 2: Processing Document")
    print("-" * 40)
    print("Breaking document into chunks...")
    print("Converting to embeddings...")
    print("Storing in database...")
    
    # Create processor
    # DocumentProcessor handles all the heavy lifting
    processor = DocumentProcessor()
    
    # Process the document
    # This reads the file, chunks it, embeds it, and stores it
    processor.process_and_store(document_path)
    
    print("✅ Document processed successfully!\n")
    
    return processor


def run_qa_loop(processor):
    """
    The main Q&A loop.
    
    After the document is processed, you can ask questions.
    This function handles the back-and-forth conversation.
    
    What happens each time you ask:
    1. Your question is converted to an embedding
    2. We find the 3 most relevant chunks
    3. We send those chunks + your question to Groq
    4. Groq gives us an answer
    5. We show you the answer
    """
    print("Step 3: Ask Questions")
    print("-" * 40)
    print("You can now ask questions about your document!")
    print("Type 'quit' to exit.\n")
    
    # Create QA engine
    # This handles the retrieval and Groq API calls
    qa_engine = QAEngine(processor)
    
    # Keep asking questions until user quits
    while True:
        # Get question from user
        question = input("\n❓ Ask a question: ").strip()
        
        # Check if user wants to quit
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        # Validate question
        if not question:
            print("⚠️  Please enter a valid question.")
            continue
        
        # Answer the question
        print("\n🤔 Thinking...")
        answer = qa_engine.answer(question)
        # answer = qa_engine.answer_with_context(question)
        
        # Show the answer
        print(f"\n💡 Answer:\n{answer}")


def main():
    """
    Main entry point.
    
    This orchestrates the entire flow:
    1. Welcome message
    2. Get document path
    3. Initialize system
    4. Run Q&A loop
    """
    try:
        print_header()
        
        # Step 1: Get document
        document_path = get_document_path()
        
        # Step 2: Process document
        processor = initialize_system(document_path)
        
        # Step 3: Run Q&A loop
        run_qa_loop(processor)
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("\n\n⚠️  Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        # Handle any errors
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

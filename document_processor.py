"""
Document Processor: Chunking + Embeddings
==========================================

This module handles:
1. Reading your document
2. Splitting into chunks (small pieces)
3. Converting chunks to embeddings (numbers)
4. Storing in ChromaDB

Think of it like:
- Reading a book
- Breaking it into pages
- Creating an index for quick lookup
"""

from sentence_transformers import SentenceTransformer
import chromadb
from typing import List
from pypdf import PdfReader


class DocumentProcessor:
    """
    Processes documents and stores them in a searchable format.
    
    Attributes:
    - model: Embedding model (converts text to numbers)
    - client: ChromaDB client (database for storing embeddings)
    - collection: Where we store chunks and embeddings
    """
    
    def __init__(self):
        """
        Initialize the processor.
        
        What happens here:
        1. Load embedding model (this is fast, cached locally)
        2. Initialize ChromaDB (creates local database)
        3. Create a collection (like a table in a database)
        """
        print("Loading embedding model... (this is fast)")
        
        # Load the embedding model
        # SentenceTransformers converts text to 384-dimensional vectors
        # Why this model? It's small (~27MB), fast, and free
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB
        # This is a vector database - stores text and embeddings together
        self.client = chromadb.Client()
        
        # Create a collection (like a table)
        # We'll store all our chunks here
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity for search
        )
        
        print("✅ Processor initialized\n")
    
    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split document into overlapping chunks.
        
        Args:
            text: The document text
            chunk_size: Size of each chunk (in characters)
            overlap: How much chunks overlap
        
        Returns:
            List of chunks
        
        Why chunking?
        - LLMs have token limits (can't process huge documents)
        - We want to send only relevant chunks to Groq
        - Overlap helps preserve context at boundaries
        
        Example:
        Text: "The cat sat on the mat. The mat was red."
        Chunks (with overlap):
        - "The cat sat on the mat. The" (chunk 1)
        - "mat. The mat was red." (chunk 2, overlaps with chunk 1)
        """
        chunks = []
        start = 0
        
        # Keep splitting until we reach the end
        while start < len(text):
            # Calculate end position
            end = start + chunk_size
            
            # Extract chunk
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start position
            # We move by (chunk_size - overlap) to create overlap
            start += chunk_size - overlap
        
        return chunks
    
    def process_and_store(self, document_path: str) -> None:
        """
        Read, chunk, embed, and store a document.
        
        Args:
            document_path: Path to your document (e.g., "data.txt")
        
        What happens step-by-step:
        1. Read the file
        2. Clean the text
        3. Split into chunks
        4. Convert chunks to embeddings
        5. Store in ChromaDB
        """
        # Step 1: Read the document
        print(f"Reading document: {document_path}")
        with open(document_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        print(f"Document size: {len(text)} characters")
        
        # Step 2: Clean text
        # Remove extra whitespace and newlines
        text = ' '.join(text.split())
        
        # Step 3: Chunk the document
        print("Chunking document...")
        chunks = self.chunk_document(text, chunk_size=500, overlap=50)
        print(f"Created {len(chunks)} chunks")
        
        # Step 4: Convert chunks to embeddings
        # This is where we convert text to numbers
        print("Creating embeddings...")
        embeddings = self.model.encode(chunks, show_progress_bar=True)
        
        # Step 5: Store in ChromaDB
        print("Storing in database...")
        
        # ChromaDB needs:
        # - ids: unique identifiers for each chunk
        # - documents: the actual text
        # - embeddings: the vector representations
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist()  # Convert numpy array to list
        )
        
        print(f"✅ Stored {len(chunks)} chunks in database\n")
    
    def search(self, query: str, top_k: int = 3) -> List[str]:
        """
        Search for relevant chunks.
        
        Args:
            query: Your question or search term
            top_k: How many chunks to return (default: 3)
        
        Returns:
            List of relevant chunks
        
        How it works:
        1. Convert your question to an embedding
        2. Find chunks with most similar embeddings
        3. Return the top K
        
        Example:
        Query: "What is the main topic?"
        Returns: Top 3 chunks most relevant to this question
        """
        # Convert query to embedding
        # Same model as chunks, so embeddings are comparable
        query_embedding = self.model.encode(query, show_progress_bar=True)
        
        # Search ChromaDB
        # Cosine similarity finds most similar chunks
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k
        )
        
        # ChromaDB returns results in a specific format
        # We extract the documents (the actual text chunks)
        if results and results['documents'] and len(results['documents']) > 0:
            return results['documents'][0]  # Return the list of chunks
        
        return []  # Return empty list if no results
        
    def read_pdf(self, path: str) -> str:
        reader = PdfReader(path)
        return "\n".join(page.extract_text() for page in reader.pages)

    def process_multiple_files(self, folder_path: str = 'tasks') -> None:
        """
        Read CSV + TXT files from folder and process together.
        CSV = primary, TXT = additional context
        """
        import os
        
        csv_file = None
        txt_file = None
        all_content = ""
        
        # Find CSV and TXT files
        for filename in os.listdir(folder_path):
            filepath = os.path.join(folder_path, filename)
            
            if filename.endswith('.csv'):
                csv_file = filepath
            elif filename.endswith('.txt'):
                txt_file = filepath
        
        # Read CSV (primary)
        if csv_file:
            print(f"Reading CSV: {csv_file}")
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                all_content += "=== TASK DATABASE (CSV) ===\n"
                all_content += f.read()
                all_content += "\n\n"
        
        # Read TXT (additional context) if exists
        if txt_file:
            print(f"Reading TXT: {txt_file}")
            with open(txt_file, 'r', encoding='utf-8-sig') as f:
                all_content += "=== DETAILED TASK NOTES (TXT) ===\n"
                all_content += f.read()
        
        if not all_content:
            raise ValueError("No CSV or TXT files found in tasks folder")
        
        # Process combined content
        print("Processing combined task data...")
        text = ' '.join(all_content.split())
        chunks = self.chunk_document(text, chunk_size=500, overlap=50)
        embeddings = self.model.encode(chunks)
        
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        self.collection.add(
            ids=ids,
            documents=chunks,
            embeddings=embeddings.tolist()
        )
        
        print(f"✅ Processed {len(chunks)} chunks from task files\n")
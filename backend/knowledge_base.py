import chromadb
from chromadb.utils import embedding_functions
import os

# Initialize the local ChromaDB client (saves data to a local folder)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use a lightweight, fast local embedding model
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

def setup_vector_db():
    """Reads the coding standards and loads them into ChromaDB."""
    # Get or create a collection
    collection = chroma_client.get_or_create_collection(
        name="coding_rules", 
        embedding_function=sentence_transformer_ef
    )
    
    # Read our knowledge base document
    file_path = os.path.join(os.path.dirname(__file__), "../data/coding_standards.txt")
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
            
        # Split the document by "RULE" to create distinct searchable chunks
        chunks = content.split("RULE")
        documents = []
        ids = []
        
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                documents.append("RULE " + chunk.strip())
                ids.append(f"rule_{i}")
                
        # Upsert (insert or update) the documents into the database
        collection.upsert(
            documents=documents,
            ids=ids
        )
        print("✅ Knowledge Base Loaded Successfully!")
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {file_path}")

def get_refactoring_context(code_snippet, n_results=2):
    """Searches the database for rules relevant to the bad code."""
    collection = chroma_client.get_collection(
        name="coding_rules", 
        embedding_function=sentence_transformer_ef
    )
    
    # Query the database
    results = collection.query(
        query_texts=[code_snippet],
        n_results=n_results
    )
    
    # Combine the top matching rules into a single string
    if results['documents'] and results['documents'][0]:
        return "\n".join(results['documents'][0])
    return "No specific rules found."
import chromadb
from chromadb.utils import embedding_functions
import os

chroma_client = chromadb.PersistentClient(path="./chroma_db")

sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

COLLECTION_NAME = "coding_rules"


def _ensure_collection():
    """Ensure vector DB collection exists and is populated."""
    try:
        return chroma_client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=sentence_transformer_ef
        )
    except:
        return setup_vector_db()


def setup_vector_db():
    collection = chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef
    )

    file_path = os.path.join(
        os.path.dirname(__file__),
        "../data/coding_standards.txt"
    )

    if not os.path.exists(file_path):
        return collection

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = [chunk.strip() for chunk in content.split("RULE") if chunk.strip()]
    documents = ["RULE " + chunk for chunk in chunks]
    ids = [f"rule_{i}" for i in range(len(documents))]

    if documents:
        collection.upsert(documents=documents, ids=ids)

    return collection


def get_refactoring_context(code_snippet: str, n_results: int = 2) -> str:
    collection = _ensure_collection()

    results = collection.query(
        query_texts=[code_snippet],
        n_results=n_results
    )

    if results.get("documents") and results["documents"][0]:
        return "\n".join(results["documents"][0])

    return "Follow SOLID principles and optimize time/space complexity."

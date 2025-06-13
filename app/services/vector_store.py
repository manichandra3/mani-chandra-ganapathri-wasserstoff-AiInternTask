from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
import google.generativeai as genai
from ..core.config import settings

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

# Initialize ChromaDB client
chroma_client = chromadb.Client(Settings(
    persist_directory="data/chroma",
    anonymized_telemetry=False
))

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="documents"
)

def get_embedding(text: str) -> List[float]:
    """Get embedding for text using Gemini."""
    result = genai.embed_content(
        model="embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return result["embedding"]

def approximate_tokens(text: str) -> int:
    """Approximate token count using character-based estimation.
    This is a rough approximation: 1 token ≈ 4 characters for English text."""
    return len(text) // 4

def split_text_into_chunks(text: str, max_tokens: int = 500) -> List[str]:
    """Split text into chunks of maximum token size."""
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    # Split by paragraphs first
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        para_tokens = approximate_tokens(para)
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def store_document_chunks(doc_id: str, page_num: int, chunks: List[str]) -> None:
    """Store document chunks in the vector database."""
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        collection.add(
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{
                "doc_id": doc_id,
                "page": page_num,
                "chunk_num": i
            }],
            ids=[f"{doc_id}_page{page_num}_chunk{i}"]
        )

def search_similar_chunks(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """Search for similar chunks using semantic search."""
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )
    
    return [
        {
            "text": doc,
            "metadata": meta,
            "distance": dist
        }
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        )
    ] 
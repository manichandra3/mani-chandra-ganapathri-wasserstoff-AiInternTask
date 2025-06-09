from typing import List, Dict, Any
import google.generativeai as genai
from ..core.config import settings
from .vector_store import search_similar_chunks
from ..db.database import SessionLocal
from ..db.models import Document, Page, Paragraph

# Initialize Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

def get_all_document_content() -> List[Dict[str, Any]]:
    """Get all document content from the database."""
    db = SessionLocal()
    try:
        documents = db.query(Document).all()
        all_content = []
        
        for doc in documents:
            for page in doc.pages:
                page_content = {
                    "doc_id": str(doc.id),
                    "page": page.page_number,
                    "content": page.content,
                    "paragraphs": [
                        {
                            "paragraph_number": p.paragraph_number,
                            "content": p.content
                        }
                        for p in page.paragraphs
                    ]
                }
                all_content.append(page_content)
        
        return all_content
    finally:
        db.close()

def format_context(chunks: List[Dict[str, Any]], all_content: List[Dict[str, Any]]) -> str:
    """Format retrieved chunks and all document content into a context string with citations."""
    if not chunks and not all_content:
        return "No documents available."
        
    context = "Here are the relevant document chunks and their full context:\n\n"
    
    # First add the retrieved chunks
    if chunks:
        context += "Most relevant chunks:\n"
        for chunk in chunks:
            metadata = chunk["metadata"]
            context += f"[Doc ID: {metadata['doc_id']}, Page: {metadata['page']}, Chunk: {metadata['chunk_num']}]\n"
            context += f"{chunk['text']}\n\n"
    
    # Then add all document content
    context += "\nFull document content:\n"
    for doc in all_content:
        context += f"\n[Doc ID: {doc['doc_id']}, Page: {doc['page']}]\n"
        context += f"Content: {doc['content']}\n"
        context += "Paragraphs:\n"
        for para in doc['paragraphs']:
            context += f"[Paragraph {para['paragraph_number']}]: {para['content']}\n"
        context += "\n"
    
    return context

def generate_qa_prompt(question: str, context: str) -> str:
    """Generate a prompt for the LLM to answer the question with citations."""
    return f"""You are a helpful AI assistant. Answer the following question based on the provided context.
Include specific citations from the context in your answer.

Context:
{context}

Question: {question}

Please format your answer as follows:
1. First, provide a direct answer to the question
2. Then, list the citations you used in the format: [Doc ID: X, Page: Y, Paragraph: Z]

If the context doesn't contain enough information to answer the question, please say so.

Answer:"""

def format_answer_for_table(answer: str, chunks: List[Dict[str, Any]], all_content: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Format the LLM's answer into a table-like structure."""
    # Split answer into main answer and citations
    parts = answer.split("Citations:")
    main_answer = parts[0].strip()
    citations = parts[1].strip() if len(parts) > 1 else ""
    
    # Create table rows
    table_rows = []
    
    # Add main answer row
    table_rows.append({
        "doc_id": "Answer",
        "content": main_answer,
        "page": "",
        "paragraph": ""
    })
    
    # Add citation rows
    if citations:
        # First add the retrieved chunks
        for chunk in chunks:
            metadata = chunk["metadata"]
            table_rows.append({
                "doc_id": metadata["doc_id"],
                "content": chunk["text"],
                "page": str(metadata["page"]),
                "paragraph": str(metadata["chunk_num"])
            })
        
        # Then add any additional cited content from the full documents
        for doc in all_content:
            for para in doc["paragraphs"]:
                if f"[Doc ID: {doc['doc_id']}, Page: {doc['page']}, Paragraph: {para['paragraph_number']}]" in citations:
                    table_rows.append({
                        "doc_id": doc["doc_id"],
                        "content": para["content"],
                        "page": str(doc["page"]),
                        "paragraph": str(para["paragraph_number"])
                    })
    
    return table_rows

async def answer_question(question: str, k: int = 5) -> List[Dict[str, str]]:
    """
    Answer a question using retrieved chunks and LLM.
    
    Args:
        question: The question to answer
        k: Number of chunks to retrieve (default: 5)
    
    Returns:
        List of dictionaries containing the answer and citations in table format
    """
    # Get all document content
    all_content = get_all_document_content()
    
    if not all_content:
        return [{
            "doc_id": "Answer",
            "content": "No documents have been processed yet. Please upload some documents first.",
            "page": "",
            "paragraph": ""
        }]
    
    # Retrieve relevant chunks
    chunks = search_similar_chunks(question, k)
    
    # Format context with citations
    context = format_context(chunks, all_content)
    
    # Generate prompt
    prompt = generate_qa_prompt(question, context)
    
    # Get answer from LLM
    response = model.generate_content(prompt)
    answer = response.text
    
    # Format answer into table structure
    return format_answer_for_table(answer, chunks, all_content) 
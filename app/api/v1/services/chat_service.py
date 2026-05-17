import requests
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from ....core.config import settings
from typing import List, Optional

# Safe/Lazy initialization for network/heavy assets
pc = None
index = None
embedder = None

try:
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)
    print("Pinecone client and index initialized successfully.")
except Exception as e:
    print(f"Warning: Pinecone initialization failed (server may be offline or API unreachable): {e}")

try:
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("SentenceTransformer loaded successfully.")
except Exception as e:
    print(f"Warning: SentenceTransformer model failed to load: {e}")

def query_rag_chatbot(user_message: str, history: Optional[List[dict]] = None) -> str:
    """Query the RAG chatbot using Pinecone and Ollama.

    Args:
        user_message: The user's query string.
    Returns:
        The chatbot's answer as a string.
    """
    # 1. Embed the user query if assets are available
    context_text = ""
    
    if embedder is not None and index is not None:
        try:
            query_embedding = embedder.encode(user_message).tolist()

            # 2. Search Pinecone vector DB
            search_results = index.query(
                vector=query_embedding,
                top_k=3,
                include_metadata=True
            )

            # 3. Build context from Pinecone matches
            if search_results and "matches" in search_results:
                for match in search_results["matches"]:
                    if "metadata" in match and "text" in match["metadata"]:
                        context_text += match["metadata"]["text"] + "\n"
        except Exception as e:
            print(f"Warning: Pinecone search query failed: {e}")
            context_text = "No vector database context available."
    else:
        print("Warning: Pinecone client not initialized. Skipping RAG search.")
        context_text = "No vector database context available."

    # 4. Prepare messages for Ollama
    messages = [
        {
            "role": "system", 
            "content": """You are a helpful HR Chatbot for Auto Tricks Private Limited. 
            Use the context provided to answer the user's questions. 
            
            Format your response for readability:
            1. Use **bold** for emphasis.
            2. Use headings (###) for sections.
            3. Use bullet points or numbered lists for steps or items.
            4. Keep paragraphs short and use line breaks between them.
            
            Always ensure the information is clear and professional."""
        }
    ]
    
    # Add history if available
    if history:
        messages.extend(history)
        # The last message in history is the current user message (added by frontend)
        # We enrich it with context to ensure RAG works correctly
        if messages[-1]["role"] == "user":
            messages[-1]["content"] = f"Context HR Policies:\n{context_text}\n\nUser Question: {user_message}"
    else:
        # If no history, add the current prompt as the first user message
        messages.append({"role": "user", "content": f"Context HR Policies:\n{context_text}\n\nUser Question: {user_message}"})

    payload = {
        "model": "llama3.2:1b",
        "messages": messages,
        "stream": False
    }

    try:
        response = requests.post(settings.OLLAMA_URL, json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()
        return result.get("message", {}).get("content", "Sorry, I could not generate a response.")
    except Exception as e:
        print(f"Error querying Ollama: {e}")
        return "The HR chatbot is currently undergoing offline maintenance. Please try again later, or contact HR directly!"


import uuid
import chromadb
from sentence_transformers import SentenceTransformer


embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path="data/chroma_db")

collection = chroma_client.get_or_create_collection(
    name="enterprise_documents"
)


def generate_embeddings(chunks: list[str]):
    embeddings = embedding_model.encode(chunks).tolist()
    return embeddings


def store_chunks_in_vector_db(chunks: list[str], filename: str):
    if not chunks:
        return {
            "status": "failed",
            "message": "No chunks available to store"
        }

    embeddings = generate_embeddings(chunks)

    ids = [
        f"{filename}_chunk_{i}_{uuid.uuid4()}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "filename": filename,
            "chunk_index": i
        }
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return {
        "status": "success",
        "filename": filename,
        "chunks_stored": len(chunks),
        "collection_name": "enterprise_documents",
        "message": "Chunks embedded and stored in ChromaDB successfully"
    }


def search_similar_chunks(query: str, top_k: int = 3):
    query_embedding = embedding_model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return results

def retrieve_relevant_chunks(query: str, top_k: int = 3):
    
    if not query or not query.strip():
        return {
            "status": "failed",
            "message": "Query cannot be empty"
        }

    query_embedding = embedding_model.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    retrieved_chunks = []

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i, document in enumerate(documents):
        retrieved_chunks.append({
            "rank": i + 1,
            "content": document,
            "filename": metadatas[i].get("filename", "unknown"),
            "chunk_index": metadatas[i].get("chunk_index", "unknown"),
            "distance": round(distances[i], 4),
            "relevance_score": round(1 / (1 + distances[i]), 4)
        })

    return {
        "status": "success",
        "query": query,
        "top_k": top_k,
        "retrieved_chunks": retrieved_chunks,
        "message": "Relevant chunks retrieved successfully"
    }
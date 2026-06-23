from app.services.vector_store_service import retrieve_relevant_chunks


def build_rag_prompt(question: str, context_chunks: list):
    context_text = "\n\n".join(
        [
            f"Source: {chunk['filename']} | Chunk Index: {chunk['chunk_index']}\n{chunk['content']}"
            for chunk in context_chunks
        ]
    )

    prompt = f"""
You are a document question-answering assistant.

Use only the context provided below to answer the user's question.
Do not use outside knowledge.
If the answer is not present in the context, say:
"I could not find the answer in the provided documents."

Context:
{context_text}

Question:
{question}

Answer:
"""

    return prompt


def mock_llm_answer(question: str, context_chunks: list):
    if not context_chunks:
        return "I could not find the answer in the provided documents."

    combined_context = " ".join([chunk["content"] for chunk in context_chunks])

    return (
        "Grounded response based on retrieved document context:\n\n"
        f"{combined_context[:700]}"
    )


def generate_rag_response(question: str, top_k: int = 3):
    if not question or not question.strip():
        return {
            "status": "failed",
            "message": "Question cannot be empty"
        }

    retrieval_result = retrieve_relevant_chunks(question, top_k)

    if retrieval_result["status"] != "success":
        return retrieval_result

    retrieved_chunks = retrieval_result["retrieved_chunks"]

    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("relevance_score", 0) >= 0.45
    ]

    if not relevant_chunks:
        return {
            "status": "success",
            "question": question,
            "answer": "I could not find the answer in the provided documents.",
             "retrieved_chunks": [],
             "rejected_chunks": retrieved_chunks,
            "message": "No relevant document context found for this question"
        }

    prompt = build_rag_prompt(question, relevant_chunks)
    answer = mock_llm_answer(question, relevant_chunks)

    return {
        "status": "success",
        "question": question,
        "answer": answer,
        "retrieved_chunks": relevant_chunks,
        "prompt_preview": prompt[:1000],
        "message": "RAG response generated using retrieved document context"
    }
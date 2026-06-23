from app.services.vector_store_service import retrieve_relevant_chunks
from app.services.rag_service import build_rag_prompt, mock_llm_answer
from app.services.safety_service import validate_user_question, verify_output


class PlannerAgent:
    def plan(self, question: str):
        return {
            "agent": "Planner Agent",
            "task": "Decide the steps required to answer the user question",
            "steps": [
                "Validate the user question",
                "Retrieve relevant chunks from ChromaDB",
                "Analyze retrieved document context",
                "Verify whether the answer can be grounded",
                "Generate final response"
            ],
            "question": question
        }


class RetrieverAgent:
    def retrieve(self, question: str, top_k: int = 3):
        retrieval_result = retrieve_relevant_chunks(question, top_k)

        return {
            "agent": "Retriever Agent",
            "task": "Fetch relevant content from the vector knowledge base",
            "retrieval_result": retrieval_result
        }


class ReasoningAgent:
    def reason(self, question: str, retrieved_chunks: list):
        if not retrieved_chunks:
            return {
                "agent": "Reasoning Agent",
                "task": "Analyze retrieved context",
                "reasoning": "No relevant context was found for the user question.",
                "can_answer": False
            }

        combined_context = " ".join(
            [chunk["content"] for chunk in retrieved_chunks]
        )

        return {
            "agent": "Reasoning Agent",
            "task": "Analyze retrieved context",
            "reasoning": "Relevant document context was found and can be used to generate a grounded response.",
            "can_answer": True,
            "context_summary": combined_context[:500]
        }


class ResponseAgent:
    def respond(self, question: str, retrieved_chunks: list):
        if not retrieved_chunks:
            return {
                "agent": "Response Agent",
                "task": "Generate final response",
                "answer": "I could not find the answer in the provided documents."
            }

        prompt = build_rag_prompt(question, retrieved_chunks)
        answer = mock_llm_answer(question, retrieved_chunks)

        return {
            "agent": "Response Agent",
            "task": "Generate final response",
            "answer": answer,
            "prompt_preview": prompt[:1000]
        }


class OutputVerificationAgent:
    def verify(self, answer: str, retrieved_chunks: list):
        verification_result = verify_output(answer, retrieved_chunks)

        return {
            "agent": "Output Verification Agent",
            "task": "Verify whether the response is supported by retrieved document context",
            "verification_result": verification_result
        }


def run_agent_workflow(question: str, top_k: int = 3):
    validation_result = validate_user_question(question)
    if validation_result["status"] == "failed":
        return validation_result

    planner = PlannerAgent()
    retriever = RetrieverAgent()
    reasoning = ReasoningAgent()
    responder = ResponseAgent()
    verifier = OutputVerificationAgent()

    plan_result = planner.plan(question)

    retrieve_result = retriever.retrieve(question, top_k)

    if retrieve_result["retrieval_result"]["status"] != "success":
        return retrieve_result

    retrieved_chunks = retrieve_result["retrieval_result"].get(
        "retrieved_chunks", []
    )

    relevant_chunks = [
        chunk for chunk in retrieved_chunks
        if chunk.get("relevance_score", 0) >= 0.45
    ]

    reasoning_result = reasoning.reason(question, relevant_chunks)

    response_result = responder.respond(question, relevant_chunks)

    verification_result = verifier.verify(
        response_result["answer"],
        relevant_chunks
    )

    return {
        "status": "success",
        "question": question,
        "agent_workflow": [
            plan_result,
            retrieve_result,
            reasoning_result,
            response_result,
            verification_result
        ],
        "final_answer": response_result["answer"],
        "output_verification": verification_result,
        "message": "Agent-based reasoning workflow completed with safety verification"
    }
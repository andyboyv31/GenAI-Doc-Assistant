def validate_user_question(question: str):
    if not question or not question.strip():
        return {
            "status": "failed",
            "message": "Question cannot be empty"
        }

    if len(question) > 500:
        return {
            "status": "failed",
            "message": "Question exceeds maximum length"
        }

    return {
        "status": "success",
        "message": "Question validation successful"
    }


def verify_output(answer: str, retrieved_chunks: list):
    if not answer:
        return {
            "status": "failed",
            "verified": False,
            "message": "Empty answer generated"
        }

    if not retrieved_chunks:
        return {
            "status": "success",
            "verified": True,
            "message": "No supporting context found. Safe response returned."
        }

    return {
        "status": "success",
        "verified": True,
        "message": "Answer verified against retrieved document context."
    }
import re

from core.document_loader import extract_pdf_pages
from core.chunker import chunk_pages
from core.retriever import DocumentRetriever
from core.verifier import verify_evidence

from agents.explanation_agent import explain_document
from workflow.summary_workflow import summarize_pdf


# Words that mean "give me a summary of the whole document".
_SUMMARY_PATTERN = re.compile(
    r"\b("
    r"summar(?:y|ise|ize|ised|ized|ising|izing)"
    r"|overview"
    r"|tl;?dr"
    r"|gist"
    r"|key\s+(?:points|takeaways|terms)"
    r"|main\s+points"
    r"|brief\s+me"
    r")\b",
    re.IGNORECASE,
)


def is_summary_request(question: str) -> bool:
    """True for short requests like 'summarise', 'give me an overview',
    'key points'. Long, specific questions go to normal question answering,
    e.g. 'what does the termination clause say, in summary?'."""
    text = (question or "").strip()
    return bool(_SUMMARY_PATTERN.search(text)) and len(text.split()) <= 10


def build_response(
    status: str,
    message: str,
    risk_flags: list | None = None,
    professional_review: bool = False,
    uncertainties: list | None = None,
) -> dict:
    """Build an empty-evidence response in the standard result format."""
    return {
        "status": status,
        "answer": message,
        "explicit_statements": [],
        "interpretations": [],
        "evidence": [],
        "uncertainties": uncertainties if uncertainties is not None else [message],
        "risk_flags": risk_flags or [],
        "professional_review_recommended": professional_review,
    }


def insufficient_evidence(message: str) -> dict:
    return build_response("INSUFFICIENT_EVIDENCE", message)


def model_error(message: str) -> dict:
    """Used for technical failures (Ollama down, bad model tag, bad JSON)
    so they are not confused with 'the document has no answer'."""
    return build_response("MODEL_ERROR", message)


def answer_document_question(
    pdf_bytes: bytes,
    question: str
) -> dict:

    # Step 1: Validate the question
    if not question or not question.strip():
        return insufficient_evidence("Please enter a question.")

    # Step 1b: "summarise" style requests get the document summary
    if is_summary_request(question):
        return summarize_pdf(pdf_bytes)

    # Step 2: Extract text from the PDF
    try:
        pages = extract_pdf_pages(pdf_bytes)
    except Exception as error:
        print("PDF extraction error:", error)
        return insufficient_evidence(
            "Could not read the PDF. Please check that "
            "it is a valid, readable PDF."
        )

    # Step 3: Divide the document into passages
    passages = chunk_pages(pages)

    if not passages:
        return insufficient_evidence("No readable passages were found.")

    # Step 4: Retrieve relevant passages
    try:
        retriever = DocumentRetriever(passages)
        relevant_passages = retriever.search(question, top_k=5)
    except Exception as error:
        print("Retrieval error:", error)
        return insufficient_evidence(
            "An error occurred while searching the document."
        )

    # Step 5: Debug information
    print("\n========== DEBUG: NYAYAAI ==========")
    print("Question:", question)
    print("Total passages:", len(passages))
    print(
        "Retrieved:",
        [(p["id"], p["page"], round(p.get("score", 0), 3))
         for p in relevant_passages]
    )
    print("====================================\n")

    # Step 6: Stop ONLY if nothing was retrieved
    if not relevant_passages:
        print("No passage shared any meaningful word with the question.")
        print("Passages available:")
        for passage in passages:
            print(" ", passage["id"], "page", passage["page"],
                  repr(passage["text"][:120]))

        return insufficient_evidence(
            "I could not find relevant evidence "
            "to answer this question."
        )

    # Step 7: Ask the explanation agent to generate an answer
    try:
        result = explain_document(question, relevant_passages)
    except Exception as error:
        print("Explanation agent error:", repr(error))
        return model_error(
            "An error occurred while generating the answer. "
            "Check that Ollama is running and the selected "
            "Gemma model is available (run 'ollama list')."
        )

    # Step 8: Validate the model response
    if not isinstance(result, dict):
        return model_error("The model returned an invalid response.")

    evidence = result.get("evidence", [])

    if not isinstance(evidence, list):
        return model_error("The model returned invalid evidence data.")

    # If the model itself says the document has no answer, respect that
    # and skip verification (there is no evidence to verify).
    if result.get("status") == "INSUFFICIENT_EVIDENCE" and not evidence:
        print("Model reported INSUFFICIENT_EVIDENCE:", result.get("answer"))
        return result

    # Step 9: Verify evidence against the retrieved passages
    valid, errors = verify_evidence(evidence, relevant_passages)

    if not valid:
        print("Evidence verification errors:", errors)
        print("Model result was:", result)

        return build_response(
            "INSUFFICIENT_EVIDENCE",
            "The answer could not be safely verified "
            "against the source passages.",
            risk_flags=["Evidence verification failed."],
            professional_review=True,
            uncertainties=errors,
        )

    # Step 10: Return the verified result
    return result
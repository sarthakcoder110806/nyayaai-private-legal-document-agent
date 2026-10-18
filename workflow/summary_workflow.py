from core.document_loader import extract_pdf_pages
from core.chunker import chunk_pages

from agents.summary_agent import summarize_passages


def summarize_pdf(pdf_bytes: bytes) -> dict:
    """Read a PDF and return a summary with verified key points.

    The result always has a "status". On success it is SUMMARY_READY.
    On failure it is ERROR or MODEL_ERROR, with a "message" to show the user.
    """

    # Step 1: extract text
    try:
        pages = extract_pdf_pages(pdf_bytes)
    except Exception as error:
        print("PDF extraction error:", error)
        return {
            "status": "ERROR",
            "message": (
                "Could not read the PDF. Please check that it is a "
                "valid, text-based PDF (not a scanned image)."
            ),
        }

    # Step 2: split into passages
    passages = chunk_pages(pages)

    if not passages:
        return {
            "status": "ERROR",
            "message": "No readable passages were found in the PDF.",
        }

    print(
        "\n===== SUMMARY: "
        f"{len(pages)} page(s), {len(passages)} passage(s) ====="
    )

    # Step 3: summarise with Gemma
    try:
        return summarize_passages(passages)
    except Exception as error:
        print("Summary agent error:", repr(error))
        return {
            "status": "MODEL_ERROR",
            "message": (
                "An error occurred while summarising. Check that Ollama "
                "is running and the selected Gemma model is available "
                "(run 'ollama list')."
            ),
        }
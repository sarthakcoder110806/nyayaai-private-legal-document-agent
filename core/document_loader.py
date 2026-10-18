import pymupdf



def extract_pdf_pages(pdf_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF while preserving page numbers.

    The PDF is read from memory rather than saved permanently
    by this function.
    """

    pages = []

    with pymupdf.open(
        stream=pdf_bytes,
        filetype="pdf"
    ) as document:

        if document.page_count == 0:
            raise ValueError(
                "The PDF contains no pages."
            )

        for index, page in enumerate(document):

            text = page.get_text("text").strip()

            pages.append({
                "page": index + 1,
                "text": text
            })

    if not any(page["text"] for page in pages):
        raise ValueError(
            "No extractable text was found. "
            "The PDF may be scanned or image-based."
        )

    return pages
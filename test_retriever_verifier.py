from pathlib import Path

from core.document_loader import extract_pdf_pages
from core.retriever import DocumentRetriever
from core.verifier import verify_evidence


# Locate the PDF
BASE_DIR = Path(__file__).resolve().parent
pdf_files = list(BASE_DIR.rglob("sample_agreement.pdf"))

if not pdf_files:
    raise FileNotFoundError("sample_agreement.pdf was not found.")

pdf_path = pdf_files[0]

# Extract PDF text
pages = extract_pdf_pages(pdf_path.read_bytes())

# Create passages with IDs, page numbers, and text
passages = []

for page in pages:
    paragraphs = [
        paragraph.strip()
        for paragraph in page["text"].splitlines()
        if paragraph.strip()
    ]

    for index, paragraph in enumerate(paragraphs):
        passages.append({
            "id": f"P{len(passages) + 1}",
            "page": page["page"],
            "text": paragraph,
        })

# Initialize BM25
retriever = DocumentRetriever(pages)

print("PDF loaded successfully.")
print("Total passages:", len(passages))

# Ask a question
question = "When must the rent be paid?"

print("\nQuestion:", question)

results = retriever.search(question, top_k=5)

print("\nRetrieved passages:")

for result in results:
    print(result)

# Match retrieved text to the canonical passages
retrieved_texts = {
    result["text"]
    for result in results
}

retrieved_passages = [
    passage
    for passage in passages
    if passage["text"] in retrieved_texts
]

# Build a valid evidence item using the retrieved source
if retrieved_passages:
    passage = retrieved_passages[0]

    evidence_items = [{
        "id": passage["id"],
        "page": passage["page"],
        "quote": passage["text"],
    }]

    is_valid, errors = verify_evidence(
        evidence_items,
        passages,
    )

    print("\nEvidence verification result:", is_valid)
    print("Verification errors:", errors)

else:
    print("\nNo passages were retrieved.")
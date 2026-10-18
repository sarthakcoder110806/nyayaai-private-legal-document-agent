from pathlib import Path

from core.document_loader import extract_pdf_pages
from core.retriever import DocumentRetriever


# Locate the project directory
BASE_DIR = Path(__file__).resolve().parent

# Find the PDF anywhere inside the project
pdf_files = list(BASE_DIR.rglob("sample_agreement.pdf"))

if not pdf_files:
    raise FileNotFoundError(
        f"sample_agreement.pdf was not found inside {BASE_DIR}"
    )

# Use the first matching PDF
pdf_path = pdf_files[0]

print(f"PDF found: {pdf_path}")

# Extract the PDF text
pages = extract_pdf_pages(pdf_path.read_bytes())

print(f"PDF extraction successful: {len(pages)} page(s)")

# Initialize the retriever
retriever = DocumentRetriever(pages)

print("\nNyayaAI retrieval system is ready!")
print("Ask questions about your agreement. Type 'exit' to quit.")

while True:
    question = input("\nYour question: ").strip()

    if question.lower() == "exit":
        print("Exiting NyayaAI.")
        break

    if not question:
        print("Please enter a question.")
        continue

    results = retriever.search(question, top_k=3)

    if not results:
        print("No matching information found in the document.")
        continue

    print("\nRelevant information:")

    for result in results:
        print(f"Page: {result['page']}")
        print(f"Text: {result['text']}")
        print(f"Score: {result['score']:.4f}")
        print("-" * 40)
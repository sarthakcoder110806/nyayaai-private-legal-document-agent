from core.document_loader import extract_pdf_pages
from core.chunker import chunk_pages
from core.retriever import DocumentRetriever

with open("sample_data/sample_agreement.pdf", "rb") as f:
    pages = extract_pdf_pages(f.read())

passages = chunk_pages(pages)
print("Passages:", len(passages))

hits = DocumentRetriever(passages).search("when must the rent be paid?", top_k=5)
for h in hits:
    print(h["id"], round(h["score"], 3), h["text"][:100])
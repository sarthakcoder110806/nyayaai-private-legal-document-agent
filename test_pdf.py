from pathlib import Path
from core.document_loader import extract_pdf_pages

# Get the directory where test_pdf.py is located
BASE_DIR = Path(__file__).resolve().parent

# Build the PDF path relative to the project directory
pdf_path = BASE_DIR / "sample_data" / "sample_agreement.pdf"

# Check whether the file exists
if not pdf_path.is_file():
    raise FileNotFoundError(
        f"PDF not found at: {pdf_path}\n"
        "Please check the PDF's actual location."
    )

# Read and extract the PDF
pdf_bytes = pdf_path.read_bytes()
pages = extract_pdf_pages(pdf_bytes)

print("PDF extraction successful!")
print(f"PDF location: {pdf_path}")
print(f"Total pages: {len(pages)}")

for page in pages:
    print(f"\n--- PAGE {page['page']} ---")
    print(page["text"])
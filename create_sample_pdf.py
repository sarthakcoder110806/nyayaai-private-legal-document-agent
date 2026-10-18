from pathlib import Path
import pymupdf


# Define file paths
source_path = Path(
    "sample_data/sample_rental_agreement.txt"
)

output_path = Path(
    "sample_data/sample_agreement.pdf"
)


# Check whether the text file exists
if not source_path.exists():
    raise FileNotFoundError(
        f"Text file not found: {source_path.resolve()}\n"
        "Create sample_data/sample_rental_agreement.txt first."
    )


# Read the agreement
text = source_path.read_text(
    encoding="utf-8"
)


# Create the PDF
document = pymupdf.open()

page = document.new_page()

page.insert_textbox(
    pymupdf.Rect(50, 50, 545, 780),
    text,
    fontsize=11,
    fontname="helv"
)


# Save the PDF
document.save(output_path)

document.close()

print("Sample PDF created successfully!")
print("PDF location:", output_path.resolve())
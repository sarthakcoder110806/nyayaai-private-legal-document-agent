from core.answer_checker import check_answer_against_evidence


passages = [
    {
        "id": "P1",
        "page": 1,
        "text": (
            "The tenant shall pay monthly rent of INR 12,000. "
            "Rent must be paid on or before the 5th day of each month."
        ),
    }
]

# Genuine evidence quote
evidence_items = [
    {
        "id": "P1",
        "page": 1,
        "quote": "The tenant shall pay monthly rent of INR 12,000.",
    }
]

tests = [
    (
        "Correct answer",
        "The tenant shall pay monthly rent of INR 12,000.",
    ),
    (
        "Different amount",
        "The tenant shall pay monthly rent of INR 50,000.",
    ),
    (
        "Unsupported bank account",
        "The landlord's bank account number is 123456.",
    ),
]

for name, answer in tests:
    result = check_answer_against_evidence(
        answer,
        evidence_items,
        passages,
    )

    print(f"\nTest: {name}")
    print("Answer:", answer)
    print("Status:", result["status"])
    print("Message:", result["message"])
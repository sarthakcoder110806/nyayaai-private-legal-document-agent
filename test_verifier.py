from core.verifier import verify_quote, verify_evidence


# Test source passage
passages = [
    {
        "id": "P1",
        "page": 1,
        "text": (
            "The tenant shall pay monthly rent of INR 12,000. "
            "Rent must be paid on or before the 5th day of each month."
        ),
    },
    {
        "id": "P2",
        "page": 1,
        "text": (
            "The tenant shall pay a security deposit of INR 24,000."
        ),
    },
]


def run_test(name, evidence_items, expected):
    result, errors = verify_evidence(evidence_items, passages)

    passed = result == expected

    print(f"\nTest: {name}")
    print(f"Expected: {expected}")
    print(f"Actual:   {result}")
    print(f"Errors:   {errors}")
    print("RESULT:", "PASS" if passed else "FAIL")


# TEST 1: Genuine quote and correct page
run_test(
    "Valid evidence",
    [
        {
            "id": "P1",
            "page": 1,
            "quote": "The tenant shall pay monthly rent of INR 12,000.",
        }
    ],
    True,
)


# TEST 2: Unknown passage ID
run_test(
    "Invalid passage ID",
    [
        {
            "id": "P99",
            "page": 1,
            "quote": "The tenant shall pay monthly rent of INR 12,000.",
        }
    ],
    False,
)


# TEST 3: Incorrect page number
run_test(
    "Incorrect page number",
    [
        {
            "id": "P1",
            "page": 5,
            "quote": "The tenant shall pay monthly rent of INR 12,000.",
        }
    ],
    False,
)


# TEST 4: Fabricated quote
run_test(
    "Quote not present in source",
    [
        {
            "id": "P1",
            "page": 1,
            "quote": "The monthly rent is INR 50,000.",
        }
    ],
    False,
)


# TEST 5: No evidence
run_test(
    "Empty evidence",
    [],
    False,
)


# TEST 6: Valid evidence from another passage
run_test(
    "Valid security deposit evidence",
    [
        {
            "id": "P2",
            "page": 1,
            "quote": "The tenant shall pay a security deposit of INR 24,000.",
        }
    ],
    True,
)


# TEST 7: Whitespace differences
run_test(
    "Whitespace normalization",
    [
        {
            "id": "P1",
            "page": 1,
            "quote": "The tenant shall pay monthly rent of INR 12,000.",
        }
    ],
    True,
)


# TEST 8: Empty quote
run_test(
    "Empty quote",
    [
        {
            "id": "P1",
            "page": 1,
            "quote": "",
        }
    ],
    False,
)


# Test verify_quote directly
print("\nDirect quote verification:")

source_text = "Rent must be paid on or before the 5th day of each month."

print(
    "Genuine quote:",
    verify_quote(
        "Rent must be paid on or before the 5th day of each month.",
        source_text,
    ),
)

print(
    "Fabricated quote:",
    verify_quote(
        "Rent must be paid on the 20th day of each month.",
        source_text,
    ),
)
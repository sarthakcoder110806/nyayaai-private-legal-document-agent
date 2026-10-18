import re


def normalize(text: str) -> str:
    """Normalize text for simple comparisons."""
    text = str(text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def check_answer_against_evidence(
    answer: str,
    evidence_items: list[dict],
    passages: list[dict],
) -> dict:
    """
    Perform basic consistency checks on answers.

    This is a preliminary rule-based check, not a complete
    semantic or legal verification system.
    """

    if not answer or not answer.strip():
        return {
            "status": "UNSUPPORTED",
            "message": "No answer was generated.",
        }

    # compare IDs as strings so small type differences do not break matching
    passage_map = {
        str(passage["id"]): passage
        for passage in passages
    }

    if not evidence_items:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "message": "No evidence was provided.",
        }

    verified_texts = []

    for item in evidence_items:
        passage = passage_map.get(str(item.get("id")))

        if passage is None:
            continue

        page = item.get("page")
        if page is not None and str(page) != str(passage["page"]):
            continue

        quote = item.get("quote", "")

        if not quote or not str(quote).strip():
            continue

        if normalize(quote) not in normalize(passage["text"]):
            continue

        verified_texts.append(passage["text"])

    if not verified_texts:
        return {
            "status": "INVALID_EVIDENCE",
            "message": "No supplied evidence could be verified.",
        }

    evidence_text = normalize(" ".join(verified_texts))
    normalized_answer = normalize(answer)

    # Conservative check: does the answer contain a long phrase
    # that also appears in the verified evidence?
    words = normalized_answer.split()

    for size in range(min(8, len(words)), 2, -1):
        for start in range(len(words) - size + 1):
            phrase = " ".join(words[start:start + size])

            if phrase in evidence_text:
                return {
                    "status": "POSSIBLY_SUPPORTED",
                    "message": (
                        "Part of the answer matches verified evidence. "
                        "This does not prove that every claim is correct."
                    ),
                }

    return {
        "status": "NEEDS_REVIEW",
        "message": (
            "The answer could not be matched confidently using "
            "simple phrase comparison. Review it against the evidence."
        ),
    }
import re
import unicodedata


def normalise_text(text: str) -> str:
    """Normalise text so harmless differences do not fail verification.

    Handles case, smart quotes, dashes, punctuation, line-break hyphens
    and repeated whitespace.
    """
    text = unicodedata.normalize("NFKC", str(text))
    text = text.casefold()

    text = (
        text.replace("\u2019", "'").replace("\u2018", "'")
        .replace("\u201c", '"').replace("\u201d", '"')
        .replace("\u2013", "-").replace("\u2014", "-")
    )

    # rejoin words hyphenated across line breaks
    text = re.sub(r"-\s*\n\s*", "", text)

    # drop punctuation, keep letters and numbers
    text = re.sub(r"[^\w\s]", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def verify_quote(quote: str, source_text: str) -> bool:
    """True if the quote appears inside the source text."""
    if not quote or not str(quote).strip():
        return False

    normalised_quote = normalise_text(quote)

    return bool(normalised_quote) and (
        normalised_quote in normalise_text(source_text)
    )


def verify_evidence(
    evidence_items: list[dict],
    passages: list[dict]
) -> tuple[bool, list[str]]:
    """Check every evidence item against the retrieved passages."""

    errors = []

    # compare IDs as strings so "P001" vs "P001" or 1 vs "1" both work
    passages_by_id = {str(p["id"]): p for p in passages}

    if not evidence_items:
        errors.append("No evidence was provided.")

    for item in evidence_items:
        if not isinstance(item, dict):
            errors.append(f"Evidence item is not an object: {item!r}")
            continue

        passage_id = str(item.get("id"))
        quote = item.get("quote", "")
        page = item.get("page")

        passage = passages_by_id.get(passage_id)

        if passage is None:
            errors.append(f"Unknown passage ID: {passage_id}")
            continue

        # lenient page check: compare as strings, skip if the model omitted it
        if page is not None and str(page) != str(passage["page"]):
            errors.append(f"Incorrect page for {passage_id}")
            continue

        if not verify_quote(quote, passage["text"]):
            errors.append(f"Quote does not match {passage_id}: {quote!r}")

    return len(errors) == 0, errors
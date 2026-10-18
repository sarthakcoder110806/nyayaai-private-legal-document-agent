def chunk_pages(
    pages: list[dict],
    max_words: int = 60
) -> list[dict]:
    """Split each page into passages of roughly max_words words.

    Passages are built from whole lines so clauses are not cut in half,
    and the last line of each passage is repeated at the start of the
    next one (overlap) so context is not lost at the boundaries.
    """

    passages = []
    passage_number = 1

    def add_passage(lines: list[str], page_number: int) -> None:
        nonlocal passage_number
        passages.append({
            "id": f"P{passage_number:03d}",
            "page": page_number,
            "text": " ".join(lines),
        })
        passage_number += 1

    for page in pages:
        lines = [
            line.strip()
            for line in page["text"].splitlines()
            if line.strip()
        ]

        if not lines:
            continue

        current: list[str] = []
        current_words = 0
        has_new_lines = False

        for line in lines:
            current.append(line)
            current_words += len(line.split())
            has_new_lines = True

            if current_words >= max_words:
                add_passage(current, page["page"])

                # overlap: carry the last line into the next passage
                current = [current[-1]]
                current_words = len(current[0].split())
                has_new_lines = False

        if current and has_new_lines:
            add_passage(current, page["page"])

    return passages
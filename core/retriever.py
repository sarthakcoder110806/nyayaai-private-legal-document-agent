import re
from rank_bm25 import BM25Okapi

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "am",
    "of", "to", "in", "on", "at", "for", "by", "and", "or", "when",
    "what", "who", "how", "which", "does", "do", "did", "must", "this",
    "that", "it", "any", "can", "i", "my", "me", "there", "with",
}


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens with stopwords removed."""
    tokens = re.findall(r"\b\w+\b", text.lower())
    return [t for t in tokens if t not in STOPWORDS]


class DocumentRetriever:
    def __init__(self, passages: list[dict]):
        self.chunks = [
            {"id": p["id"], "page": p["page"], "text": p["text"]}
            for p in passages
            if p.get("text", "").strip()
        ]

        if not self.chunks:
            raise ValueError("No text chunks were created from the PDF.")

        self.tokenized = [tokenize(c["text"]) for c in self.chunks]
        self.bm25 = BM25Okapi(self.tokenized)

    def search(self, question: str, top_k: int = 3) -> list[dict]:
        """Return the most relevant passages.

        BM25 is used only for RANKING. A passage is kept if it shares at
        least one meaningful word with the question. We do not filter on
        the BM25 score, because it can be zero or negative when the
        document has very few passages.
        """
        query_tokens = tokenize(question)

        if not query_tokens:
            return []

        query_set = set(query_tokens)
        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            range(len(scores)),
            key=lambda i: (len(query_set & set(self.tokenized[i])), scores[i]),
            reverse=True,
        )

        results = []

        for i in ranked:
            if not (query_set & set(self.tokenized[i])):
                continue

            chunk = self.chunks[i]
            results.append({
                "id": chunk["id"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": float(scores[i]),
            })

            if len(results) >= top_k:
                break

        return results
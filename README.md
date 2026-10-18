# ⚖️ NyayaAI — Private Legal Document Explainer

NyayaAI helps you understand legal documents such as rental agreements, contracts and notices. Upload a text-based PDF and get a plain-language summary, then ask questions about it. Every answer is backed by an exact quote and page number taken from your document.

Everything runs **locally on your computer** using a Gemma model through [Ollama](https://ollama.com). Your documents are not sent to any online service.

> **Disclaimer:** NyayaAI explains what a document says. It is **not legal advice**. Consult a qualified legal professional for legal decisions.

---

## ✨ Features

- **Plain-language summaries** with document type, key points, important details, risk flags and uncertainties
- **Question answering** grounded only in the uploaded document
- **Verified quotes:** every quote is checked against the source passage and page, and unverifiable points are dropped
- **Chat history per document:** re-uploading the same PDF brings back its summary and conversation
- **Download summaries** as Markdown
- **Local-only storage** in a SQLite database and a `data/` folder, with one-click deletion
- **Legal-themed interface** (navy and gold) with inline SVG graphics and no external requests

---

## 🧱 How it works

1. **Extract:** PyMuPDF reads the PDF text page by page.
2. **Chunk:** each page is split into overlapping passages of about 60 words.
3. **Retrieve:** BM25 ranks the passages that best match your question.
4. **Explain:** the local Gemma model answers in structured JSON, citing passage IDs and quotes.
5. **Verify:** every quote is checked against the retrieved text. If verification fails, the answer is rejected rather than shown as fact.

---

## 📁 Project structure

```
nyayaai-private-legal-document/
├── app.py                  # Streamlit interface
├── ui_theme.py             # Theme, CSS and inline SVG graphics
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml         # Theme colours and upload limit
├── agents/
│   ├── explanation_agent.py
│   └── summary_agent.py
├── core/
│   ├── chunker.py
│   ├── document_loader.py
│   ├── history_store.py    # SQLite + local PDF storage
│   ├── llm.py              # Ollama / Gemma wrapper
│   ├── retriever.py        # BM25 retrieval
│   └── verifier.py         # Quote verification
├── workflow/
│   ├── agent_workflow.py
│   └── summary_workflow.py
└── data/                   # Created automatically on first run
```

---

## 🚀 Getting started

### Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- A Gemma model pulled in Ollama (for example `ollama pull gemma3:4b`)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd nyayaai-private-legal-document

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Choose your model

Run `ollama list` and note the exact model name. The default in `core/llm.py` is `gemma4:e2b`. You can override it without editing code:

```bash
# Windows (cmd)
set NYAYAAI_MODEL=gemma3:4b

# Windows (PowerShell)
$env:NYAYAAI_MODEL="gemma3:4b"

# macOS / Linux
export NYAYAAI_MODEL=gemma3:4b
```

### Check the setup

```bash
python -c "from workflow.summary_workflow import summarize_pdf; print('OK')"
```

### Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

---

## 🖥️ Usage

1. Click **New chat** and upload a text-based PDF.
2. Wait while the summary is generated locally. This can take a minute.
3. Read the summary and key points, or download them as `.md`.
4. Ask questions in the chat box, or use the starter questions.
5. Re-open past documents from the sidebar at any time.

---

## 🔒 Privacy

- Processing happens on your machine through Ollama.
- PDFs, summaries and chats are saved only in the local `data/` folder (`data/nyayaai.db` and `data/pdfs/`).
- `data/` is listed in `.gitignore` so your documents are never committed.
- Use **Privacy & data** in the sidebar to delete one document or all history.
- The interface uses no web fonts or remote images, so the browser makes no third-party requests.

Verify the privacy behaviour yourself before using highly sensitive documents.

---

## ⚠️ Limitations

- Only **text-based PDFs** are supported. Scanned or image-only PDFs need OCR first.
- Very long documents are summarised in sections, with a cap to keep local models fast.
- Answer quality depends on the local model you choose. Larger models are generally more accurate.
- The tool does not judge whether a clause is legally valid or enforceable.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `MODEL_ERROR` in the app | Make sure Ollama is running and `MODEL_NAME` (or `NYAYAAI_MODEL`) matches `ollama list` exactly |
| "No extractable text" | The PDF is scanned or image-based; run OCR on it first |
| Answers say evidence could not be verified | Try a more specific question or a larger model |
| Theme looks unstyled | Hard-refresh the browser (Ctrl+Shift+R) and confirm `ui_theme.py` is next to `app.py` |
| Import errors | Activate the virtual environment and run `pip install -r requirements.txt` |

---

## 🧰 Tech stack

[Streamlit](https://streamlit.io) · [Ollama](https://ollama.com) with Gemma · [PyMuPDF](https://pymupdf.readthedocs.io) · [rank-bm25](https://github.com/dorianbrown/rank_bm25) · SQLite

---

## 📄 License

Add your preferred license here (for example MIT).

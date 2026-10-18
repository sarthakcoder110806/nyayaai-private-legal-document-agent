import traceback

import streamlit as st

from workflow.agent_workflow import answer_document_question


st.set_page_config(
    page_title="NyayaAI",
    page_icon="📄",
    layout="wide"
)

# ---------- session state ----------
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

if "result" not in st.session_state:
    st.session_state["result"] = None

if "error" not in st.session_state:
    st.session_state["error"] = None


def clear_session() -> None:
    """Reset the result, the question and the file uploader."""
    st.session_state["result"] = None
    st.session_state["error"] = None
    st.session_state["question"] = ""
    # changing the key creates a fresh, empty file uploader
    st.session_state["uploader_key"] += 1


def render_list(items: list, empty_text: str) -> None:
    """Show a list as bullet points instead of raw [] brackets."""
    if not items:
        st.caption(empty_text)
        return

    for item in items:
        st.markdown(f"- {item}")


def render_status(status: str) -> None:
    """Show the status with a colour that matches its meaning."""
    label = f"Status: {status}"

    if status == "SUPPORTED":
        st.success(label)
    elif status in ("PARTIALLY_SUPPORTED", "AMBIGUOUS"):
        st.warning(label)
    elif status == "MODEL_ERROR":
        st.error(label)
    else:
        st.info(label)


# ---------- page header ----------
st.title("NyayaAI")

st.subheader("Understand your documents. Protect your privacy.")

st.write("Upload a document and ask questions about its contents.")

st.info(
    "Privacy: This application is designed to "
    "process document text locally using Gemma "
    "through Ollama. Do not upload sensitive "
    "documents until you have verified the "
    "application's privacy behavior."
)

st.warning(
    "NyayaAI provides document explanations, "
    "not legal advice. Consult a qualified "
    "professional for legal decisions."
)


# ---------- inputs ----------
uploaded_file = st.file_uploader(
    "Upload a text-based PDF",
    type=["pdf"],
    key=f"uploader_{st.session_state['uploader_key']}"
)

question = st.text_input(
    "Ask a question about the document",
    placeholder="What is the termination notice period?",
    key="question"
)

col_analyze, col_clear, _ = st.columns([1, 1, 6])

with col_analyze:
    analyze_clicked = st.button("Analyze document")

with col_clear:
    st.button("Clear session", on_click=clear_session)


# ---------- run the analysis ----------
if analyze_clicked:

    st.session_state["result"] = None
    st.session_state["error"] = None

    if uploaded_file is None:
        st.session_state["error"] = "Please upload a PDF first."

    elif not question.strip():
        st.session_state["error"] = "Please enter a question."

    else:
        with st.spinner("Analyzing the document locally..."):
            try:
                result = answer_document_question(
                    uploaded_file.getvalue(),
                    question
                )
                st.session_state["result"] = result

            except Exception as error:
                # full details go to the terminal for debugging
                traceback.print_exc()
                st.session_state["error"] = (
                    "The analysis failed. Check that Ollama is running "
                    "and the selected Gemma model is installed "
                    f"(run `ollama list`).\n\nDetails: {error}"
                )


# ---------- show errors ----------
if st.session_state["error"]:
    st.error(st.session_state["error"])


# ---------- show the result ----------
result = st.session_state["result"]

if result:

    st.subheader("Answer")
    st.write(result.get("answer", "No answer was generated."))
    render_status(result.get("status", "UNKNOWN"))

    st.subheader("Explicit statements")
    render_list(
        result.get("explicit_statements", []),
        "None."
    )

    st.subheader("Interpretations")
    render_list(
        result.get("interpretations", []),
        "None."
    )

    st.subheader("Evidence")
    evidence = result.get("evidence", [])

    if evidence:
        for item in evidence:
            st.markdown(
                f"**Page {item.get('page')} — {item.get('id')}**"
            )
            st.markdown(f"> {item.get('quote', '')}")
    else:
        st.caption("No verified evidence is available.")

    st.subheader("Uncertainties")
    render_list(
        result.get("uncertainties", []),
        "None."
    )

    st.subheader("Risk flags")
    render_list(
        result.get("risk_flags", []),
        "None."
    )

    if result.get("professional_review_recommended", False):
        st.warning(
            "Consider consulting a qualified legal professional."
        )
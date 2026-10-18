import hashlib
import traceback
from datetime import date, datetime, timedelta

import streamlit as st

from core.history_store import (
    add_message,
    delete_all,
    delete_document,
    get_document,
    get_pdf_bytes,
    init_db,
    list_documents,
    load_messages,
    save_document,
    save_summary,
    touch_document,
)
from ui_theme import (
    inject_theme,
    render_doc_header,
    render_features,
    render_hero,
    render_status_badge,
    sidebar_brand,
)
from workflow.agent_workflow import (
    answer_document_question,
    is_summary_request,
)
from workflow.summary_workflow import summarize_pdf


st.set_page_config(
    page_title="NyayaAI",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSISTANT_AVATAR = "⚖️"

STARTER_QUESTIONS = [
    "Summarise this document",
    "What are the key dates and deadlines?",
    "What are the payment terms?",
    "How can this agreement be terminated?",
]


# ============================================================ safe wrappers
def safe_summarize(pdf_bytes: bytes) -> dict:
    try:
        return summarize_pdf(pdf_bytes)
    except Exception as error:
        traceback.print_exc()
        return {
            "status": "MODEL_ERROR",
            "message": (
                "The summary failed. Check that Ollama is running and "
                "the Gemma model is installed (run `ollama list`). "
                f"Details: {error}"
            ),
        }


def safe_answer(pdf_bytes: bytes, question: str) -> dict:
    try:
        return answer_document_question(pdf_bytes, question)
    except Exception as error:
        traceback.print_exc()
        return {
            "status": "MODEL_ERROR",
            "message": (
                "The analysis failed. Check that Ollama is running and "
                "the Gemma model is installed (run `ollama list`). "
                f"Details: {error}"
            ),
        }


# ================================================================ rendering
def render_list(items: list, empty_text: str = "None.") -> None:
    if not items:
        st.caption(empty_text)
        return

    for item in items:
        st.markdown(f"- {item}")


def render_status(status: str) -> None:
    render_status_badge(status)


def render_summary(data: dict, heading: str = "####") -> None:
    if data.get("document_type"):
        st.caption(f"Document type: {data['document_type']}")

    st.markdown(f"{heading} Summary")
    st.write(data.get("summary", ""))

    st.markdown(f"{heading} Key points")
    key_points = data.get("key_points", [])

    if key_points:
        for number, item in enumerate(key_points, start=1):
            st.markdown(
                f"**{number}.** {item.get('point', '')}  \n"
                f"*Page {item.get('page')} · {item.get('id')}*"
            )
            st.caption(f"Verified quote: \u201c{item.get('quote', '')}\u201d")
    else:
        st.caption("No key points could be verified against the document.")

    if data.get("important_details"):
        st.markdown(f"{heading} Important details")
        render_list(data["important_details"])

    if data.get("risk_flags"):
        st.markdown(f"{heading} Risk flags")
        render_list(data["risk_flags"])

    if data.get("uncertainties"):
        st.markdown(f"{heading} Uncertainties")
        render_list(data["uncertainties"])

    if data.get("professional_review_recommended"):
        st.warning("Consider consulting a qualified legal professional.")


def render_answer(result: dict) -> None:
    st.write(result.get("answer", "No answer was generated."))
    render_status(result.get("status", "UNKNOWN"))

    evidence = result.get("evidence", [])
    if evidence:
        st.markdown("**Evidence**")
        for item in evidence:
            st.markdown(f"*Page {item.get('page')} · {item.get('id')}*")
            st.markdown(f"> {item.get('quote', '')}")

    with st.expander("More details"):
        st.markdown("**Explicit statements**")
        render_list(result.get("explicit_statements", []))

        st.markdown("**Interpretations**")
        render_list(result.get("interpretations", []))

        st.markdown("**Uncertainties**")
        render_list(result.get("uncertainties", []))

        st.markdown("**Risk flags**")
        render_list(result.get("risk_flags", []))

    if result.get("professional_review_recommended", False):
        st.warning("Consider consulting a qualified legal professional.")


def render_assistant(data: dict) -> None:
    status = data.get("status")

    if status == "SUMMARY_READY":
        render_summary(data)
    elif "answer" not in data and "message" in data:
        render_status(status or "ERROR")
        st.write(data["message"])
    else:
        render_answer(data)


def summary_to_markdown(name: str, summary: dict) -> str:
    lines = [f"# Summary: {name}", ""]

    if summary.get("document_type"):
        lines += [f"*Document type: {summary['document_type']}*", ""]

    lines += [summary.get("summary", ""), "", "## Key points"]

    for number, item in enumerate(summary.get("key_points", []), start=1):
        lines.append(
            f"{number}. {item.get('point', '')} (page {item.get('page')})"
        )

    for title, key in (
        ("Important details", "important_details"),
        ("Risk flags", "risk_flags"),
        ("Uncertainties", "uncertainties"),
    ):
        if summary.get(key):
            lines += ["", f"## {title}"]
            lines += [f"- {entry}" for entry in summary[key]]

    lines += [
        "",
        "_Generated by NyayaAI. This is an explanation, not legal advice._",
    ]

    return "\n".join(lines)


# ============================================================ state helpers
def group_label(timestamp: float) -> str:
    day = datetime.fromtimestamp(timestamp).date()
    today = date.today()

    if day == today:
        return "Today"
    if day == today - timedelta(days=1):
        return "Yesterday"
    if (today - day).days <= 7:
        return "Previous 7 days"
    return "Older"


def short_name(name: str, limit: int = 26) -> str:
    return name if len(name) <= limit else name[: limit - 1] + "\u2026"


def start_new_chat() -> None:
    st.session_state["active_doc_id"] = None
    st.session_state["uploader_key"] += 1


def open_document(doc_id: str) -> None:
    touch_document(doc_id)
    st.session_state["active_doc_id"] = doc_id


def delete_active_document() -> None:
    delete_document(st.session_state["active_doc_id"])
    st.session_state["active_doc_id"] = None
    st.session_state["uploader_key"] += 1
    st.session_state["confirm_delete"] = False


def delete_everything() -> None:
    delete_all()
    st.session_state["active_doc_id"] = None
    st.session_state["uploader_key"] += 1
    st.session_state["confirm_delete"] = False


# ============================================================== app startup
init_db()
inject_theme()

st.session_state.setdefault("active_doc_id", None)
st.session_state.setdefault("uploader_key", 0)
st.session_state.setdefault("confirm_delete", False)

active_id = st.session_state["active_doc_id"]


# ================================================================== sidebar
with st.sidebar:
    sidebar_brand()

    st.button(
        "＋  New chat",
        on_click=start_new_chat,
        use_container_width=True,
        type="primary" if active_id is None else "secondary",
    )

    documents = list_documents()

    if not documents:
        st.caption("Your previous chats will appear here.")

    last_group = None

    for document in documents:
        group = group_label(document["updated_at"])

        if group != last_group:
            st.markdown(
                f"<div class='side-group'>{group}</div>",
                unsafe_allow_html=True,
            )
            last_group = group

        st.button(
            f"📄  {short_name(document['name'])}",
            key=f"open_{document['id']}",
            on_click=open_document,
            args=(document["id"],),
            use_container_width=True,
            type="primary" if document["id"] == active_id else "secondary",
            help=document["name"],
        )

    st.divider()

    with st.expander("🔒 Privacy & data"):
        st.caption(
            "Documents are processed on this computer with Gemma through "
            "Ollama. PDFs, summaries and chats are saved in the local "
            "`data` folder, so your history is still here next time. "
            "Do not upload sensitive documents until you have verified "
            "the application's privacy behavior."
        )

        st.checkbox("I want to delete data", key="confirm_delete")

        if active_id is not None:
            st.button(
                "🗑  Delete this document & chat",
                on_click=delete_active_document,
                disabled=not st.session_state["confirm_delete"],
                use_container_width=True,
            )

        st.button(
            "🗑  Delete ALL history",
            on_click=delete_everything,
            disabled=not st.session_state["confirm_delete"],
            use_container_width=True,
        )

    st.caption(
        "NyayaAI explains documents. It is not legal advice. "
        "Consult a qualified professional for legal decisions."
    )


# ================================================================== landing
if active_id is None:

    render_hero()

    uploaded_file = st.file_uploader(
        "Upload a text-based PDF to get a summary and ask questions",
        type=["pdf"],
        key=f"uploader_{st.session_state['uploader_key']}",
    )

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.getvalue()
        doc_id = hashlib.sha256(pdf_bytes).hexdigest()

        if get_document(doc_id) is None:
            save_document(doc_id, uploaded_file.name, pdf_bytes)

            with st.spinner(
                "Reading the document and writing a summary locally. "
                "This can take a minute..."
            ):
                summary = safe_summarize(pdf_bytes)

            save_summary(doc_id, summary)
        else:
            # same PDF as before: its summary and chat history come back
            touch_document(doc_id)

        st.session_state["active_doc_id"] = doc_id
        st.session_state["uploader_key"] += 1
        st.rerun()

    render_features()

    st.caption(
        "Tip: upload the same PDF again at any time to bring back its "
        "summary and chat history, or pick it from the sidebar."
    )

    st.stop()


# =============================================================== chat screen
document = get_document(active_id)

if document is None:
    st.session_state["active_doc_id"] = None
    st.rerun()

pdf_bytes = get_pdf_bytes(active_id)

if pdf_bytes is None:
    st.error(
        "The stored PDF could not be found. Upload it again to continue."
    )
    st.stop()

summary = document["summary"]
messages = load_messages(active_id)
has_user_message = any(m["role"] == "user" for m in messages)

render_doc_header(
    document["name"],
    f"{datetime.fromtimestamp(document['created_at']):%d %b %Y, %H:%M}",
)

# ----- summary & key points panel
with st.expander("📋 Summary & key points", expanded=not has_user_message):

    if summary and summary.get("status") == "SUMMARY_READY":
        render_summary(summary)

        st.download_button(
            "⬇  Download summary (.md)",
            data=summary_to_markdown(document["name"], summary),
            file_name=f"summary_{document['name'].rsplit('.', 1)[0]}.md",
            mime="text/markdown",
        )
    else:
        message = (summary or {}).get(
            "message", "No summary has been generated yet."
        )
        st.error(message)

        if st.button("Retry summary"):
            with st.spinner("Writing a summary locally..."):
                new_summary = safe_summarize(pdf_bytes)

            save_summary(active_id, new_summary)
            st.rerun()

# ----- previous messages of this PDF
for message in messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            render_assistant(message["data"])

# ----- starter questions (only before the first question)
clicked_prompt = None
starters_slot = st.empty()

if not has_user_message:
    with starters_slot.container():
        st.caption("Try asking")
        columns = st.columns(2)

        for index, text in enumerate(STARTER_QUESTIONS):
            if columns[index % 2].button(
                text,
                key=f"starter_{index}",
                use_container_width=True,
            ):
                clicked_prompt = text

# ----- chat input
typed_prompt = st.chat_input("Ask anything about this document\u2026")
prompt = typed_prompt or clicked_prompt

if prompt:
    starters_slot.empty()

    add_message(active_id, "user", prompt)

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):

        if (
            is_summary_request(prompt)
            and summary
            and summary.get("status") == "SUMMARY_READY"
        ):
            # reuse the stored summary: no second model call
            reply = summary
        else:
            with st.spinner("Searching the document locally..."):
                reply = safe_answer(pdf_bytes, prompt)

            if reply.get("status") == "SUMMARY_READY":
                save_summary(active_id, reply)

        render_assistant(reply)

    add_message(active_id, "assistant", reply)
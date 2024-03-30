import client
import streamlit as st


# def show_pdf(base64_pdf: str) -> str:
#     """Show a base64 encoded PDF in the browser using an HTML tag"""
#     return f'<embed src="data:application/pdf;base64,{base64_pdf}" width=100% height=800 type="application/pdf">'


def retrieval_form_container() -> None:
    """Container to enter RAG query and sent /rag_summary GET request"""
    left, right = st.columns(2)
    with left:
        form = st.form(key="retrieval_query")
        rag_query = form.text_area(
            "Retrieval Query", value="What are the main challenges of deploying ML models?"
        )

    if form.form_submit_button("Search"):
        with st.status("Running"):
            response = client.get_rag_summary(rag_query)
        st.session_state["history"].append(dict(query=rag_query, response=response.json()))


def history_display_container(history):
    if len(history) > 1:
        st.header("History")
        max_idx = len(history) - 1
        history_idx = st.slider("History", 0, max_idx, value=max_idx, label_visibility="collapsed")
        entry = history[history_idx]
    else:
        entry = history[0]

    st.subheader("Query")
    st.write(entry["response"]["question"])

    st.subheader("Response")
    st.write(entry["response"]["answer"])
    count = 0
    with st.expander("Sources"):
        for source in entry["response"]["context"]:
            count += 1
            doc_count = f"--- Source {count} ---"
            st.write(doc_count)
            st.write(source["page_content"])
        st.write(entry["response"]["answer"])


def app() -> None:
    """Streamlit entrypoint for PDF Summarize frontend"""
    # config
    st.set_page_config(
        page_title="📤 rag_with_sources",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )

    st.title("📤 RAG with sources")

    retrieval_form_container()

    if history := st.session_state.get("history"):
        history_display_container(history)
    else:
        st.session_state["history"] = list()


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()

import arxiv
import client
import streamlit as st




def arxiv_search_container() -> None:
    """Container to query Arxiv using the Python `arxiv` library"""
    form = st.form(key="arxiv_search_form")
    query = form.text_area(
        "arXiv Search Query",
        value="LLM in production",
        help="[See docs](https://lukasschwab.me/arxiv.py/index.html#Search)",
    )

    with st.expander("arXiv Search Parameters"):
        max_results = st.number_input("Max results", value=5)
        sort_by = st.selectbox(
            "Sort by",
            [
                arxiv.SortCriterion.Relevance,
                arxiv.SortCriterion.LastUpdatedDate,
                arxiv.SortCriterion.SubmittedDate,
            ],
            format_func=lambda option: option.value[0].upper() + option.value[1:],
        )
        sort_order = st.selectbox(
            "Sort order",
            [arxiv.SortOrder.Ascending, arxiv.SortOrder.Descending],
            format_func=lambda option: option.value[0].upper() + option.value[1:],
        )

    if form.form_submit_button("Search"):
        st.session_state["arxiv_search"] = dict(
            query=query,
            max_results=max_results,
            sort_by=sort_by,
            sort_order=sort_order,
        )


def article_selection_container(arxiv_form: dict) -> None:
    """Container to select arXiv search results and send /store_arxiv POST request, limiting to one article at a time."""
    # Perform the arXiv search based on the given form inputs

    results = list(arxiv.Search(**arxiv_form).results())

    # Create a form for article selection
    form = st.form(key="article_selection_form")

    # Use a selectbox for single article selection
    selection = form.selectbox("Select an article to store", results, format_func=lambda r: r.title)

    # Button to submit the selected article for storage
    if form.form_submit_button("Store"):
        # Get the short ID of the selected article
        arxiv_id = selection.get_short_id()
        url = selection.pdf_url
        print(url)

        # Status message while storing the article
        with st.status("Storing arXiv article"):
            # Store the selected article's ID (adjust the function name as per your actual implementation)
            client.post_store_arxiv([url])


def pdf_upload_container():
    """Container to uploader arbitrary PDF files and send /store_pdfs POST request"""
    uploaded_files = st.file_uploader("Upload PDF", type=["pdf"])
    if st.button("Upload"):
        with st.status("Storing PDFs"):
            client.post_store_pdfs(uploaded_files)


def stored_documents_container():
    """Container showingstored PDF documents, results of /documents GET request"""
    response = client.get_all_documents_file_name().json()
    documents = response["documents"]
    st.table({"PDF file name": documents})


def app() -> None:
    """Streamlit entrypoint for PDF Summarize frontend"""
    # config
    st.set_page_config(
        page_title="📥 ingestion",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )


    st.title("📥 Ingestion")

    left, right = st.columns(2)

    with left:
        st.subheader("Download from arXiv")
        arxiv_search_container()
        if arxiv_form := st.session_state.get("arxiv_search"):
            article_selection_container(arxiv_form)

    with right:
        st.subheader("Upload PDF files")
        pdf_upload_container()


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()

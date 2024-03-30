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

    with right:
        st.write("Hybrid Search Parameters")
        retrieve_top_k = st.number_input(
            "top K", value=3, help="The number of chunks to consider for response"
        )
        hybrid_search_alpha = st.slider(
            "alpha",
            min_value=0.0,
            max_value=1.0,
            value=0.75,
            help="0: Keyword. 1: Vector.\n[Weaviate docs](https://weaviate.io/developers/weaviate/api/graphql/search-operators#hybrid)",
        )

    if form.form_submit_button("Search"):
        with st.status("Running"):
            response = client.get_rag_summary(rag_query, hybrid_search_alpha, int(retrieve_top_k))
        st.session_state["history"].append(dict(query=rag_query, response=response))


def history_display_container(history):
    if len(history) > 1:
        st.header("History")
        max_idx = len(history) - 1
        history_idx = st.slider("History", 0, max_idx, value=max_idx, label_visibility="collapsed")
        entry = history[history_idx]
    else:
        entry = history[0]

    st.subheader("User")
    st.write(entry["query"])

    st.subheader("assistant")
    st.write(entry["response"])


def app() -> None:
    st.set_page_config(page_title="Chat Interface", page_icon="🗨️", layout="centered")
    st.title("🗨️ Chat Interface")

    user_sub = st.text_input("Enter your User ID:")
    if 'new_conversation_id' not in st.session_state:
        st.session_state['new_conversation_id'] = None
    if 'selected_conversation_id' not in st.session_state:
        st.session_state['selected_conversation_id'] = None
    # Initialize session state for conversations
    if 'conversations' not in st.session_state:
        st.session_state['conversations'] = {}

    if user_sub:
        if st.button("Start New Conversation"):
            new_conversation_id = client.create_conversation(user_sub)
            st.session_state['conversations'][new_conversation_id] = []
            st.session_state['selected_conversation_id'] = new_conversation_id

        # Fetch conversations for the user
        conversation_ids = client.get_conversations(user_sub)
        for conversation_id in conversation_ids:
            if conversation_id not in st.session_state['conversations']:
                st.session_state['conversations'][conversation_id] = []

        # Use session_state to pre-select the conversation
        selected_conversation_id = st.selectbox(
            "Select a Conversation", options=list(st.session_state['conversations'].keys()),
            index=list(st.session_state['conversations'].keys()).index(st.session_state['selected_conversation_id']) if st.session_state['selected_conversation_id'] in st.session_state['conversations'] else 0
        )
        st.session_state['selected_conversation_id'] = selected_conversation_id

        if selected_conversation_id:
            # Fetch messages for the selected conversation
            messages = client.get_messages(selected_conversation_id)
            st.session_state['conversations'][selected_conversation_id] = messages

            # Display conversation history
            if st.session_state['conversations'][selected_conversation_id]:
                st.write("Conversation History:")
                for message in st.session_state['conversations'][selected_conversation_id]:
                    with st.chat_message("user"):
                        st.write(message["user_message"])
                    with st.chat_message("assistant"):
                        st.write(message["agent_message"])

            # Form for sending a new message
            with st.form(key='message_form'):
                message_input = st.text_input("Enter your message here:")
                send_message = st.form_submit_button("Send Message")

                if send_message and message_input:
                    if send_message and message_input:
                        with st.spinner("Thinking..."):
                            response = client.send_message(selected_conversation_id, message_input)
                            with st.chat_message("assistant"):
                                st.write(response)
                        st.rerun()

if __name__ == "__main__":
    app()
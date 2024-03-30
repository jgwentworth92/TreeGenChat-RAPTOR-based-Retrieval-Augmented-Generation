import client
import streamlit as st


def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://mintlify.s3-us-west-1.amazonaws.com/dagworksinc/logo/dark.png);
                background-repeat: no-repeat;
                background-size: 70%;
                background-position: 20px 20px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def app() -> None:
    """Streamlit entrypoint for PDF Summarize frontend"""
    # config
    st.set_page_config(
        page_title="TreeGenChat",
        page_icon="📚",
        layout="centered",
        menu_items={"Get help": None, "Report a bug": None},
    )


    st.title("📚 TreeGenChat")

    if client.get_fastapi_status() is False:
        st.warning("FastAPI is not ready. Make sure your backend is running")
        st.stop()  # exit application after displaying warning if FastAPI is not available

    st.header("Information")
    st.markdown(
        """The RAG (Retrieval-Augmented Generation) Application is a comprehensive system designed to leverage the 
        power of FastAPI, PostgreSQL, and vector database technologies for efficient document processing, retrieval, 
        and conversational interfaces. The application provides a robust API for document upload, retrieval, 
        and conversation management, facilitating advanced text analysis and interaction capabilities.

    """
    )

    st.subheader("Key Features")
    st.markdown(
        """


- **Document Upload and Processing**: Supports uploading and processing documents in PDF format, incorporating them into the system for future retrieval and analysis.
- **Document Retrieval**: Enables querying of documents by IDs, allowing for efficient data retrieval.
- **Conversational Interface**: Facilitates the creation and management of conversations, along with quick response generation for interactive applications.
- **Advanced Text Analysis**: Utilizes vector databases for semantic search and retrieval, enhancing the application's ability to understand and process natural language queries.
## Getting Started

### Environment Setup

The application requires specific environment variables for its operation, including configurations for Auth0, database URLs, and API keys. These variables should be defined in a `.env` file at the root of the project:

```ini
# .env example configuration
AUTH0_DOMAIN=
AUTH0_API_AUDIENCE=
AUTH0_ISSUER=
AUTH0_ALGORITHMS=
DATABASE_URL=postgresql+asyncpg://postgres:postgres@convo-db:5432/postgres
DATABASE_URL2=postgresql+psycopg2://myuser:mypassword@db:5432/mydatabase
collection_name=
```

### Docker Compose

Docker Compose is used to orchestrate the application and its dependencies, including the FastAPI service and PostgreSQL databases. Use the following commands to manage your Docker environment:

- **Start the Application**: `docker-compose up --build`
- **Build Images**: `docker-compose build`

### API Endpoints

The application provides a set of RESTful endpoints for document management and conversation processing, accessible through FastAPI's interactive documentation at `http://localhost:8000/docs` or `http://localhost:8000/redoc`.

## Directory Structure

A brief overview of the project's directory structure:

```
.
├── app/                    # Main FastAPI application
├── appfrwk/                # Common framework code
├── .env                    # Environment variables
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
└── setup.py                # Python package setup
```

## Conclusion

The RAG Application stands at the intersection of document processing and conversational AI, providing a versatile platform for developing advanced text analysis and interaction solutions. By leveraging Docker, FastAPI, and PostgreSQL, it offers a scalable and efficient infrastructure for a wide range of applications.

    """
    )


if __name__ == "__main__":
    # run as a script to test streamlit app locally
    app()

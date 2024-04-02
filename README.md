
# TreenGenChat Application Documentation

## Overview

TreenGenChat, powered by the Retrieval-Augmented Generation (RAG) framework, is a pioneering system designed to enhance document processing, retrieval, and conversational interfaces through the integration of FastAPI, PostgreSQL, and vector database technologies. This application leverages the novel RAPTOR methodology—Recursive Abstractive Processing for Tree-Organized Retrieval—to surpass traditional limitations by facilitating holistic understanding and processing of documents. TreenGenChat provides an advanced API for document upload, retrieval, conversation management, and interactive applications, setting a new benchmark in text analysis and interaction capabilities.

## Key Features

- **Document Upload and Processing**: Support for PDF document uploads, with processing and integration for future retrieval and analysis.
- **Advanced Document Retrieval**: Utilizes the RAPTOR approach for semantic search and retrieval across documents, employing recursive summaries for enhanced understanding.
- **Conversational Interface**: Manages conversations with rapid response generation, underpinned by RAPTOR's tree-organized retrieval for depth and accuracy.
- **Streamlit Frontend**: A user-friendly interface for interaction with TreenGenChat's features, including document management and conversation processing.
- **Scalable Infrastructure**: Leveraging Docker, FastAPI, and PostgreSQL for a robust and scalable application framework.

## Getting Started

### Environment Setup

Environment variables are crucial for configuring TreenGenChat, including Auth0 settings, database URLs, and API keys. These should be specified in a `.env` file located at the project's root:

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

Docker Compose orchestrates TreenGenChat and its dependencies, ensuring all services are networked under 'rag'. To manage your Docker environment:

- **Start the Application**: `docker-compose up --build`
- **Build Images**: `docker-compose build`

### API Endpoints

Access RESTful endpoints for document and conversation management via FastAPI's interactive documentation at `http://localhost:8000/docs` or `http://localhost:8000/redoc`.

## Directory Structure

An outline of the TreenGenChat project structure:

```
.
├── app/                    # Main FastAPI application
├── appfrwk/                # Common framework code
├── frontend/               # Streamlit Application
├── .env                    # Environment variables
├── docker-compose.yml      # Docker Compose configuration for TreenGenChat
├── requirements.txt        # Python dependencies
└── setup.py                # Python package setup
```

## Conclusion

TreenGenChat, with its foundation in the RAG framework and enhanced by RAPTOR's novel methodology, provides an unmatched platform for developing sophisticated text analysis and interactive solutions. Its use of Docker, FastAPI, PostgreSQL, and Streamlit frontends propels it to the forefront of conversational AI applications, enabling scalable and efficient infrastructures for diverse applications.

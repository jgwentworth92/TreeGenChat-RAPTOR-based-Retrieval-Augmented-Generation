from langchain_community.embeddings import OpenAIEmbeddings

from .store import AsnyPgVector, ExtendedPgVector


def get_vector_store(
    connection_string: str,
    embeddings: OpenAIEmbeddings,
    collection_name: str,
    mode: str = "async",
):
    if mode == "sync":
        return ExtendedPgVector(
            connection_string=connection_string,
            embedding_function=embeddings,
            collection_name=collection_name,
        )
    elif mode == "async":
        return AsnyPgVector(
            connection_string=connection_string,
            embedding_function=embeddings,
            collection_name=collection_name,
        )

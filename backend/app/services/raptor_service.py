import hashlib

from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.llms.openai import OpenAI
from langchain_core.documents import Document

from app.config import get_config

config = get_config()

import numpy as np
import pandas as pd
import tiktoken
import umap
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.mixture import GaussianMixture
from icecream import ic

RANDOM_SEED = 224  # Fixed seed for reproducibility


### --- Code from citations referenced above (added comments and docstrings) --- ###


class TextClusterSummarizer:
    def __init__(
            self,
            token_limit,
            max_iterations,
            data_directory,
            chat_model=None,  # Optional chat_model parameter
    ):
        print("Initializing TextClusterSummarizer...")
        self.token_limit = token_limit
        self.max_iterations = max_iterations
        self.loader = PyMuPDFLoader(data_directory)
        self.data_directory = data_directory
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        self.embedding_model = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)

        # Use the provided chat_model if one is passed, otherwise instantiate a new one
        if chat_model is None:
            self.chat_model = ChatOpenAI(temperature=0, openai_api_key=config.OPENAI_API_KEY, model="gpt-3.5-turbo")
        else:
            self.chat_model = chat_model

        self.iteration_summaries = []

    def load_and_split_documents(self):
        print("Loading and splitting documents...")
        docs = self.loader.load()
        return self.text_splitter.split_documents(docs)

    def embed_texts(self, texts):
        print("Embedding texts...")
        return [self.embedding_model.embed_query(txt) for txt in texts]

    def reduce_dimensions(self, embeddings, dim, n_neighbors=None, metric="cosine"):
        print(f"Reducing dimensions to {dim}...")
        if n_neighbors is None:
            n_neighbors = int((len(embeddings) - 1) ** 0.5)
        return umap.UMAP(
            n_neighbors=n_neighbors, n_components=dim, metric=metric
        ).fit_transform(embeddings)

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding("cl100k_base")
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def cluster_embeddings(self, embeddings, threshold, random_state=0):
        print("Clustering embeddings...")
        n_clusters = self.get_optimal_clusters(embeddings)
        gm = GaussianMixture(n_components=n_clusters, random_state=random_state).fit(
            embeddings
        )
        probs = gm.predict_proba(embeddings)
        return [np.where(prob > threshold)[0] for prob in probs], n_clusters

    def get_optimal_clusters(self, embeddings, max_clusters=50, random_state=1234):
        print("Calculating optimal number of clusters...")
        max_clusters = min(max_clusters, len(embeddings))
        bics = [
            GaussianMixture(n_components=n, random_state=random_state)
            .fit(embeddings)
            .bic(embeddings)
            for n in range(1, max_clusters)
        ]
        print(f"Optimal number of clusters: {np.argmin(bics) + 1}")
        return np.argmin(bics) + 1

    def format_cluster_texts(self, df):
        print("Formatting cluster texts...")
        clustered_texts = {}
        for cluster in df["Cluster"].unique():
            cluster_texts = df[df["Cluster"] == cluster]["Text"].tolist()
            clustered_texts[cluster] = " --- ".join(cluster_texts)
        return clustered_texts

    def generate_summaries(self, texts):
        print("Generating summaries...")
        template = """You are an assistant to create a detailed summary of the text input provided.
Text:
{text}
"""
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.chat_model | StrOutputParser()

        summaries = {}
        for cluster, text in texts.items():
            token_count = self.num_tokens_from_string(text)

            if token_count > self.token_limit:
                raise ValueError(
                    f"Token limit exceeded for cluster {cluster} with {token_count} tokens. Unable to generate summary."
                )

            summary = chain.invoke({"text": text})
            summaries[cluster] = summary
        return summaries

    def run(self):
        print("Running TextClusterSummarizer...")
        docs = self.load_and_split_documents()
        texts = [doc.page_content for doc in docs]
        all_summaries = texts

        iteration = 1

        self.iteration_summaries.append(
            {"iteration": 0, "texts": texts, "summaries": []}
        )

        while True:
            print(f"Iteration {iteration}")
            embeddings = self.embed_texts(all_summaries)

            # Need enough neighbours for UMAP
            n_neighbors = min(int((len(embeddings) - 1) ** 0.5), len(embeddings) - 1)
            if n_neighbors < 2:
                print("Not enough data points for UMAP reduction. Stopping iterations.")
                break

            embeddings_reduced = self.reduce_dimensions(
                embeddings, dim=2, n_neighbors=n_neighbors
            )
            labels, num_clusters = self.cluster_embeddings(
                embeddings_reduced, threshold=0.5
            )

            if num_clusters == 1:
                print("Reduced to a single cluster. Stopping iterations.")
                break

            simple_labels = [label[0] if len(label) > 0 else -1 for label in labels]
            df = pd.DataFrame(
                {
                    "Text": all_summaries,
                    "Embedding": list(embeddings_reduced),
                    "Cluster": simple_labels,
                }
            )

            clustered_texts = self.format_cluster_texts(df)
            summaries = self.generate_summaries(clustered_texts)

            all_summaries = list(summaries.values())
            self.iteration_summaries.append(
                {
                    "iteration": iteration,
                    "texts": all_summaries,
                    "summaries": list(summaries.values()),
                }
            )
            if iteration > self.max_iterations:
                print("max iterations reached")
                break
            iteration += 1

        final_summary = all_summaries[0] if all_summaries else ""
        all_texts = []
        all_texts.extend(self.iteration_summaries[-1]["summaries"])
        all_texts.extend(texts)
        docs = [
            Document(
                page_content=doc,
                metadata=(

                    {"digest": hashlib.md5(doc.encode()).hexdigest(), "source": self.data_directory}
                ),
            )
            for doc in all_texts
        ]

        ic("--- Raw Text Start ---")
        for page in texts:
            ic("--- Text Content Start ---")
            ic(page)
            ic("---Text Content End ---\n")
        ic("--- Summary  Start ---")
        for page in self.iteration_summaries[-1]["summaries"]:
            ic("--- Summary Content Start ---")
            ic(page)
            ic("---Summary Content End ---\n")

        return docs

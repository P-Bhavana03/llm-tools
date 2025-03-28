from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_vector_store(embeddings):

    return Chroma(
        collection_name="tools",
        embedding_function=embeddings,
        persist_directory="./chroma_db",
    )

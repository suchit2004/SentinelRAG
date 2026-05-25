import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Import RBAC helper
from app.ingestion.rbac_metadata import get_required_role_for_doc

load_dotenv()

# Embedding model config (all-MiniLM-L6-v2 generates 384-dimensional vectors)
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "company_docs"
VECTOR_STORE_DIR = "vectorstore"

class DocumentIngestor:
    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.client = QdrantClient(path=VECTOR_STORE_DIR)

    def init_collection(self):
        """
        Recreates the Qdrant collection with 384 dimensions and Cosine distance.
        """
        print(f"Initializing collection '{COLLECTION_NAME}' in {VECTOR_STORE_DIR}...")
        self.client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print(f"Collection '{COLLECTION_NAME}' initialized successfully.")

    def load_and_split_documents(self, data_dir: str):
        """
        To be implemented in Commit 4.
        Loads PDF files from data_dir and splits them.
        """
        pass

    def index_documents(self, chunks):
        """
        To be implemented in Commit 5.
        Generates embeddings and indexes chunks in Qdrant.
        """
        pass

if __name__ == "__main__":
    ingestor = DocumentIngestor()
    ingestor.init_collection()
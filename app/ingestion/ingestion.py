from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from dotenv import load_dotenv
import os

load_dotenv()
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

client = QdrantClient(path="vectorstore")

client.recreate_collection(
    collection_name="company_docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
)

loader = PyPDFLoader("data/finance_report.pdf")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)
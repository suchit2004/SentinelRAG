from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, Range
from sentence_transformers import SentenceTransformer
from app.ingestion.rbac_metadata import Role

class RBACRetriever:
    def __init__(self, vectorstore_path: str = "vectorstore", collection_name: str = "company_docs"):
        self.client = QdrantClient(path=vectorstore_path)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = collection_name

    def retrieve(self, query: str, user_role: Role, limit: int = 5):
        """
        Retrieves top K chunks matching the query, filtered by the user's role.
        A user with role level L can only access chunks with required_role_level <= L.
        """
        query_vector = self.embedding_model.encode(query).tolist()
        
        # Construct filter: required_role_level <= user_role.value
        rbac_filter = Filter(
            must=[
                FieldCondition(
                    key="required_role_level",
                    range=Range(lte=user_role.value)
                )
            ]
        )
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=rbac_filter,
            limit=limit
        )
        
        docs = []
        for hit in results.points:
            docs.append({
                "page_content": hit.payload.get("page_content", ""),
                "source": hit.payload.get("source", ""),
                "required_role_name": hit.payload.get("required_role_name", "ADMIN"),
                "required_role_level": hit.payload.get("required_role_level", 3),
                "score": hit.score,
                "metadata": hit.payload.get("metadata", {})
            })
            
        return docs

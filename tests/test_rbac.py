import pytest
from app.ingestion.rbac_metadata import Role, has_access, get_required_role_for_doc
from app.rag.retriever import RBACRetriever

def test_role_hierarchy():
    # Admin should access everything
    assert has_access(Role.ADMIN, Role.ADMIN) is True
    assert has_access(Role.ADMIN, Role.EXECUTIVE) is True
    assert has_access(Role.ADMIN, Role.EMPLOYEE) is True

    # Executive should access Executive and Employee, but not Admin
    assert has_access(Role.EXECUTIVE, Role.ADMIN) is False
    assert has_access(Role.EXECUTIVE, Role.EXECUTIVE) is True
    assert has_access(Role.EXECUTIVE, Role.EMPLOYEE) is True

    # Employee should access only Employee
    assert has_access(Role.EMPLOYEE, Role.ADMIN) is False
    assert has_access(Role.EMPLOYEE, Role.EXECUTIVE) is False
    assert has_access(Role.EMPLOYEE, Role.EMPLOYEE) is True

def test_document_role_mapping():
    assert get_required_role_for_doc("financial_report.pdf") == Role.EXECUTIVE
    assert get_required_role_for_doc("IPO-IndustryReport.pdf") == Role.EMPLOYEE
    # Default fallback for safety
    assert get_required_role_for_doc("secret_formula.docx") == Role.ADMIN

def test_retriever_rbac_filtering():
    """
    Unit test using an in-memory Qdrant database to verify that
    retrieved documents adhere strictly to RBAC level constraints.
    """
    from qdrant_client.models import VectorParams, Distance, PointStruct
    
    # Initialize in-memory retriever
    retriever = RBACRetriever(vectorstore_path=":memory:")
    
    # Setup collection
    retriever.client.recreate_collection(
        collection_name=retriever.collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE)
    )
    
    # Index dummy employee chunk (level 1)
    emp_content = "The industry is growing rapidly with new cloud services."
    emp_vector = retriever.embedding_model.encode(emp_content).tolist()
    retriever.client.upsert(
        collection_name=retriever.collection_name,
        points=[
            PointStruct(
                id=1,
                vector=emp_vector,
                payload={
                    "page_content": emp_content,
                    "source": "IPO-IndustryReport.pdf",
                    "required_role_name": "EMPLOYEE",
                    "required_role_level": 1
                }
            )
        ]
    )
    
    # Index dummy executive chunk (level 2)
    exec_content = "Q3 financial reports show profit margins are up by 15%."
    exec_vector = retriever.embedding_model.encode(exec_content).tolist()
    retriever.client.upsert(
        collection_name=retriever.collection_name,
        points=[
            PointStruct(
                id=2,
                vector=exec_vector,
                payload={
                    "page_content": exec_content,
                    "source": "financial_report.pdf",
                    "required_role_name": "EXECUTIVE",
                    "required_role_level": 2
                }
            )
        ]
    )
    
    # 1. As an Employee, we should only see employee document
    employee_docs = retriever.retrieve("profit margins or cloud services", Role.EMPLOYEE, limit=10)
    for doc in employee_docs:
        assert doc["required_role_level"] <= Role.EMPLOYEE.value
        assert doc["source"] != "financial_report.pdf"
    assert len(employee_docs) == 1
    assert employee_docs[0]["source"] == "IPO-IndustryReport.pdf"
        
    # 2. As an Executive, we should see both documents
    executive_docs = retriever.retrieve("profit margins or cloud services", Role.EXECUTIVE, limit=10)
    assert len(executive_docs) == 2
    sources = [doc["source"] for doc in executive_docs]
    assert "financial_report.pdf" in sources
    assert "IPO-IndustryReport.pdf" in sources

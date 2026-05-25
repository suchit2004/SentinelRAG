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
    Integration test using the active local Qdrant database to verify that
    retrieved documents adhere strictly to RBAC level constraints.
    """
    retriever = RBACRetriever()
    
    # 1. As an Employee, we should NOT get any financial_report.pdf documents (level 2)
    employee_docs = retriever.retrieve("revenue profits or company performance", Role.EMPLOYEE, limit=10)
    for doc in employee_docs:
        assert doc["required_role_level"] <= Role.EMPLOYEE.value
        assert doc["source"] != "financial_report.pdf"
        
    # 2. As an Executive, we can get financial_report.pdf documents (level 2)
    executive_docs = retriever.retrieve("revenue profits or company performance", Role.EXECUTIVE, limit=10)
    has_financial_report = any(doc["source"] == "financial_report.pdf" for doc in executive_docs)
    # Check that at least some matches are from financial_report.pdf if results are found
    if len(executive_docs) > 0:
        # Since the query is about revenue/profits, it should match the financial report chunks
        assert has_financial_report is True

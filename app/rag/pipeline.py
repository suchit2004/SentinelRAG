from app.ingestion.rbac_metadata import Role
from app.rag.retriever import RBACRetriever
from app.rag.guardrails import Guardrails
from app.rag.llm_client import GroqLLMClient

class SentinelRAGPipeline:
    def __init__(self, vectorstore_path: str = "vectorstore", collection_name: str = "company_docs", model_name: str = "llama-3.1-8b-instant"):
        self.retriever = RBACRetriever(vectorstore_path=vectorstore_path, collection_name=collection_name)
        self.llm_client = GroqLLMClient(model_name=model_name)

    def run(self, query: str, user_role_str: str) -> dict:
        """
        Runs the full SentinelRAG pipeline for a given query and user role.
        Enforces input guardrails, RBAC retrieval, Groq generation, and output guardrails.
        """
        user_role = Role.from_str(user_role_str)
        
        # 1. Validate Input Guardrails
        input_guard = Guardrails.validate_input(query)
        if not input_guard["is_safe"]:
            return {
                "query": query,
                "input_is_safe": False,
                "input_safety_reason": input_guard["reason"],
                "retrieved_docs": [],
                "raw_response": "",
                "processed_response": f"Request blocked: {input_guard['reason']}",
                "pii_detected": False,
                "pii_types": []
            }
            
        # 2. Retrieve Documents with RBAC filter
        retrieved_docs = self.retriever.retrieve(query, user_role)
        
        # 3. Format Context
        context_blocks = []
        for idx, doc in enumerate(retrieved_docs):
            context_blocks.append(f"Source: {doc['source']} (Access Required: {doc['required_role_name']})\nContent: {doc['page_content']}")
            
        context = "\n\n---\n\n".join(context_blocks)
        
        # 4. Generate LLM Prompt
        system_message = (
            "You are SentinelRAG, a secure enterprise RAG system. "
            "Use the provided context to answer the user's query. "
            "If the context does not contain the answer, say that you cannot find it in the company documents. "
            "Do not disclose any details that are not in the context. "
            "Always follow security protocols and protect sensitive data."
        )
        
        prompt = (
            f"Context from company documents:\n"
            f"{context if context else '[No documents matched or accessible for your role.]'}\n\n"
            f"User Query: {query}\n\n"
            f"Answer:"
        )
        
        # 5. LLM Call
        raw_response = self.llm_client.generate(prompt=prompt, system_message=system_message)
        
        # 6. Apply Output Guardrails (PII Masking)
        output_guard = Guardrails.process_output(raw_response)
        
        return {
            "query": query,
            "input_is_safe": True,
            "input_safety_reason": "",
            "retrieved_docs": retrieved_docs,
            "raw_response": raw_response,
            "processed_response": output_guard["processed_text"],
            "pii_detected": output_guard["pii_detected"],
            "pii_types": output_guard["pii_types"]
        }

if __name__ == "__main__":
    # Quick sanity test
    import sys
    try:
        pipeline = SentinelRAGPipeline()
        # Test query
        res = pipeline.run("What are the financial metrics mentioned?", "EXECUTIVE")
        print(f"Query: {res['query']}")
        print(f"Processed Response: {res['processed_response'][:300]}...")
        print(f"Number of retrieved docs: {len(res['retrieved_docs'])}")
    except Exception as e:
        print(f"Pipeline sanity test error: {e}")

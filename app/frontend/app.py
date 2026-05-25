import streamlit as st
import os
import sys

# Ensure parent directory is in path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.rag.pipeline import SentinelRAGPipeline
from app.ingestion.rbac_metadata import Role

# Page config
st.set_page_config(
    page_title="SentinelRAG Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pipeline" not in st.session_state:
    try:
        st.session_state.pipeline = SentinelRAGPipeline()
    except Exception as e:
        st.session_state.pipeline = None
        st.error(f"Error initializing RAG pipeline: {e}")

# Sidebar
with st.sidebar:
    st.title("🛡️ SentinelRAG Control")
    st.write("Secure Enterprise Search with Role-Based Access Control and AI Guardrails.")
    st.markdown("---")
    
    # User Profile / Role Simulation
    st.subheader("Simulate User Identity")
    user_name = st.text_input("Name", value="Jane Doe")
    user_role_name = st.selectbox(
        "User Role",
        options=[role.name for role in Role],
        index=0  # Defaults to EMPLOYEE
    )
    
    current_role = Role.from_str(user_role_name)
    st.info(f"Active Role: **{user_role_name}** (Level {current_role.value})")
    
    # Access matrix visualization
    st.markdown("### 📋 Access Level Rules")
    st.markdown(
        f"""
        - **ADMIN** (Level 3): Full system access
        - **EXECUTIVE** (Level 2): Financials + Market Reports
        - **EMPLOYEE** (Level 1): Market Reports only
        """
    )
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main Application Window
st.title("SentinelRAG: Secure Retrieval & Generation")
st.markdown("Use this secure playground to query company documents. The system will filter references based on your active role and apply guardrails to both queries and responses.")

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Display sources if any were retrieved
        if "sources" in msg and msg["sources"]:
            with st.expander("🔍 View Retrieved Sources"):
                for idx, src in enumerate(msg["sources"]):
                    st.markdown(
                        f"**Source {idx+1}:** `{src['source']}` (Required Role: `{src['required_role_name']}`, Similarity Score: `{src['score']:.4f}`)"
                    )
                    st.text_area(f"Snippet {idx+1}", value=src["page_content"], height=100, disabled=True, key=f"src_{msg['id']}_{idx}")
        
        # Display guardrail warning
        if "guardrail_warning" in msg and msg["guardrail_warning"]:
            st.warning(msg["guardrail_warning"])

# Chat Input
if prompt := st.chat_input("Ask a question about financial or IPO reports..."):
    # Display user query
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Store user message
    msg_id = len(st.session_state.messages)
    st.session_state.messages.append({
        "id": msg_id,
        "role": "user",
        "content": prompt
    })
    
    # Run pipeline
    if st.session_state.pipeline is None:
        st.error("RAG Pipeline is not initialized. Please verify Groq API key and Qdrant database.")
    else:
        with st.spinner("Retrieving secure documents and generating response..."):
            pipeline_result = st.session_state.pipeline.run(prompt, user_role_name)
            
        # Parse result
        if not pipeline_result["input_is_safe"]:
            response_content = f"❌ **Request Blocked by Input Guardrail**"
            guard_warning = f"Reason: {pipeline_result['input_safety_reason']}"
            sources = []
        else:
            response_content = pipeline_result["processed_response"]
            sources = pipeline_result["retrieved_docs"]
            
            # Format output guardrail warning if PII was redacted
            if pipeline_result["pii_detected"]:
                guard_warning = f"⚠️ **Security Notice:** Sensitive personal data ({', '.join(pipeline_result['pii_types'])}) was detected and redacted in the generated answer."
            else:
                guard_warning = None
                
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response_content)
            
            if sources:
                with st.expander("🔍 View Retrieved Sources"):
                    for idx, src in enumerate(sources):
                        st.markdown(
                            f"**Source {idx+1}:** `{src['source']}` (Required Role: `{src['required_role_name']}`, Similarity Score: `{src['score']:.4f}`)"
                        )
                        st.text_area(f"Snippet {idx+1}", value=src["page_content"], height=100, disabled=True, key=f"src_new_{idx}")
                        
            if guard_warning:
                st.warning(guard_warning)
                
        # Store assistant response in session state
        st.session_state.messages.append({
            "id": msg_id + 1,
            "role": "assistant",
            "content": response_content,
            "sources": sources,
            "guardrail_warning": guard_warning
        })

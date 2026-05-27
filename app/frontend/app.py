import streamlit as st
import os
import sys

# Ensure parent directory is in path so we can import app modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.rag.pipeline import SentinelRAGPipeline
from app.ingestion.rbac_metadata import Role
from app.auth.auth_manager import AuthManager


# Page config
st.set_page_config(
    page_title="SentinelRAG Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Premium UI CSS Injection
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;500;700&display=swap');
    
    /* General styles */
    .stApp {
        background-color: #0d0f1d;
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3, .stSubheader {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Header Gradient styling */
    .hero-container {
        background: linear-gradient(135deg, rgba(31, 38, 135, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: left;
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 50%);
        pointer-events: none;
    }
    
    .hero-title {
        font-size: 2.8rem;
        background: linear-gradient(to right, #00f2fe, #4facfe, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 5px;
        font-weight: 800;
    }
    
    .hero-subtitle {
        font-size: 1.15rem;
        color: #94a3b8;
        font-weight: 300;
        margin-bottom: 0px;
    }
    
    /* Access Level Badges */
    .role-badge {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .role-admin {
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);
        color: #ffffff;
        border: 1px solid rgba(239, 68, 68, 0.4);
    }
    
    .role-executive {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #ffffff;
        border: 1px solid rgba(245, 158, 11 0.4);
    }
    
    .role-employee {
        background: linear-gradient(135deg, #10b981 0%, #047857 100%);
        color: #ffffff;
        border: 1px solid rgba(16, 185, 129, 0.4);
    }
    
    /* Source Cards Glassmorphism styling */
    .source-card {
        background: rgba(22, 28, 45, 0.5);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: transform 0.2s ease, border-color 0.2s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    .source-card:hover {
        transform: translateY(-2px);
        border-color: rgba(139, 92, 246, 0.3);
        background: rgba(22, 28, 45, 0.7);
    }
    
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 8px;
    }
    
    .source-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .source-score {
        font-size: 0.8rem;
        color: #64748b;
    }
    
    .source-body {
        font-size: 0.85rem;
        color: #cbd5e1;
        line-height: 1.5;
        white-space: pre-wrap;
    }
    
    /* Sidebar glassmorphic styling */
    section[data-testid="stSidebar"] {
        background-color: #090a12 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Modern Streamlit adjustments */
    div[data-testid="stExpander"] {
        background: rgba(22, 28, 45, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
    }
    
    /* Styled warnings & errors */
    .stWarning, .stError {
        border-radius: 10px !important;
    }
    
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "auth_manager" not in st.session_state:
    st.session_state.auth_manager = AuthManager()
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = Role.EMPLOYEE

if "pipeline" not in st.session_state:
    try:
        # Load local vector store, model
        st.session_state.pipeline = SentinelRAGPipeline()
    except Exception as e:
        st.session_state.pipeline = None
        st.error(f"Error initializing RAG pipeline: {e}")

# Login Screen Layout
if not st.session_state.authenticated:
    st.markdown(
        """
        <div class="hero-container" style="max-width: 500px; margin: 80px auto; text-align: center;">
            <div class="hero-title" style="font-size: 2.2rem; text-align: center;">🛡️ SentinelRAG Login</div>
            <div class="hero-subtitle" style="margin-bottom: 20px; text-align: center;">Access restricted to authorized personnel.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.container():
        # Center column trick
        _, login_col, _ = st.columns([1, 2, 1])
        with login_col:
            username_input = st.text_input("Username", key="login_username")
            password_input = st.text_input("Password", type="password", key="login_password")
            login_btn = st.button("Authenticate", use_container_width=True)
            
            if login_btn:
                if st.session_state.auth_manager.authenticate_user(username_input, password_input):
                    st.session_state.authenticated = True
                    st.session_state.username = username_input
                    st.session_state.user_role = st.session_state.auth_manager.get_user_role(username_input)
                    st.success("Authentication successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
            
            # Simple credentials hint for demo
            st.markdown(
                """
                <p style="color: #64748b; font-size: 0.8rem; text-align: center; margin-top: 15px;">
                    Simulated Credentials:<br/>
                    • <b>admin_user</b> / password123 (ADMIN)<br/>
                    • <b>executive_user</b> / password123 (EXECUTIVE)<br/>
                    • <b>employee_user</b> / password123 (EMPLOYEE)
                </p>
                """,
                unsafe_allow_html=True
            )
    st.stop()


# Sidebar
with st.sidebar:
    st.markdown("## 🛡️ SentinelRAG")
    st.markdown("<p style='color: #64748b; font-size: 0.85rem;'>Enterprise RAG SecOps System</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # User Profile
    st.subheader("Authenticated User")
    user_name = st.session_state.username
    user_role_name = st.session_state.user_role.name
    current_role = st.session_state.user_role
    
    # Active role display using custom badges
    badge_class = f"role-{user_role_name.lower()}"
    st.markdown(
        f"""
        <div style='background-color: rgba(255,255,255,0.02); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px;'>
            <p style='margin: 0; font-size: 0.8rem; color: #64748b;'>USER</p>
            <p style='margin: 0 0 8px 0; font-weight: 600; font-size: 1.1rem;'>👤 {user_name}</p>
            <p style='margin: 0; font-size: 0.8rem; color: #64748b; margin-bottom: 4px;'>CLEARANCE LEVEL</p>
            <span class='role-badge {badge_class}'>{user_role_name}</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Access matrix visualization
    st.markdown("### 📋 Access Policies")
    st.markdown(
        f"""
        <div style="background-color: rgba(255,255,255,0.03); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem;">
            <p style="margin: 0 0 8px 0;"><span class="role-badge role-admin">ADMIN</span>: Full repository</p>
            <p style="margin: 0 0 8px 0;"><span class="role-badge role-executive">EXECUTIVE</span>: Financials + IPO Reports</p>
            <p style="margin: 0;"><span class="role-badge role-employee">EMPLOYEE</span>: IPO Reports only</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("Log Out", type="secondary", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.rerun()

# Hero Header section
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">SentinelRAG</div>
        <div class="hero-subtitle">Role-Based Document Retrieval Engine with Integrated AI Guardrails</div>
    </div>
    """,
    unsafe_allow_html=True
)

# Create tabs based on user role
tabs_to_create = ["💬 Secure Chat"]
if current_role >= Role.EXECUTIVE:
    tabs_to_create.append("🗂️ Document Registry")
    tabs_to_create.append("📊 Quality Analytics")
if current_role >= Role.ADMIN:
    tabs_to_create.append("🛡️ Security Audits")

tabs = st.tabs(tabs_to_create)

# Tab 0: Chat interface
with tabs[0]:
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
            # Display sources if any were retrieved (styled as custom HTML Cards)
            if "sources" in msg and msg["sources"]:
                with st.expander("🔍 View Retrieved Sources"):
                    for idx, src in enumerate(msg["sources"]):
                        role_class = f"role-{src['required_role_name'].lower()}"
                        st.markdown(
                            f"""
                            <div class="source-card">
                                <div class="source-header">
                                    <div class="source-title">📄 {src['source']}</div>
                                    <div>
                                        <span class="role-badge {role_class}">{src['required_role_name']}</span>
                                        <span class="source-score" style="margin-left: 10px;">Score: {src['score']:.4f}</span>
                                    </div>
                                </div>
                                <div class="source-body">{src['page_content']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            
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
            with st.spinner("Processing request through security layers..."):
                pipeline_result = st.session_state.pipeline.run(prompt, user_role_name, username=st.session_state.username)
                
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
                            role_class = f"role-{src['required_role_name'].lower()}"
                            st.markdown(
                                f"""
                                <div class="source-card">
                                    <div class="source-header">
                                        <div class="source-title">📄 {src['source']}</div>
                                        <div>
                                            <span class="role-badge {role_class}">{src['required_role_name']}</span>
                                            <span class="source-score" style="margin-left: 10px;">Score: {src['score']:.4f}</span>
                                        </div>
                                    </div>
                                    <div class="source-body">{src['page_content']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
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

# Tab 1: Document Registry (Executive and Admin)
if current_role >= Role.EXECUTIVE:
    with tabs[1]:
        st.subheader("🗂️ Company Documents Registry")
        st.markdown("All private company PDF documents currently indexed in the secure Qdrant database.")
        
        if st.session_state.pipeline is None:
            st.error("RAG Pipeline is not initialized.")
        else:
            with st.spinner("Fetching document registry..."):
                doc_list = st.session_state.pipeline.retriever.list_indexed_documents()
                
            if not doc_list:
                st.info("No documents are currently indexed in the vector store.")
            else:
                # Render registry table
                if current_role == Role.ADMIN:
                    cols = st.columns([3, 2, 1, 1])
                    cols[0].markdown("**Document Source**")
                    cols[1].markdown("**Required Role Clearance**")
                    cols[2].markdown("**Indexed Chunks**")
                    cols[3].markdown("**Action**")
                else:
                    cols = st.columns([4, 2, 2])
                    cols[0].markdown("**Document Source**")
                    cols[1].markdown("**Required Role Clearance**")
                    cols[2].markdown("**Indexed Chunks**")
                
                st.markdown("---")
                for doc in doc_list:
                    role_c = f"role-{doc['required_role_name'].lower()}"
                    if current_role == Role.ADMIN:
                        cols = st.columns([3, 2, 1, 1])
                        cols[0].markdown(f"📄 {doc['source']}")
                        cols[1].markdown(f"<span class='role-badge {role_c}'>{doc['required_role_name']}</span>", unsafe_allow_html=True)
                        cols[2].markdown(f"{doc['chunks']}")
                        # Generate unique key for button
                        btn_key = f"del_{doc['source'].replace('.', '_').replace('-', '_')}"
                        if cols[3].button("🗑️ Delete", key=btn_key, type="secondary"):
                            with st.spinner("Deleting document..."):
                                success = st.session_state.pipeline.retriever.delete_document(doc['source'])
                            if success:
                                st.success(f"Deleted {doc['source']} successfully!")
                                st.rerun()
                            else:
                                st.error(f"Failed to delete {doc['source']}.")
                    else:
                        cols = st.columns([4, 2, 2])
                        cols[0].markdown(f"📄 {doc['source']}")
                        cols[1].markdown(f"<span class='role-badge {role_c}'>{doc['required_role_name']}</span>", unsafe_allow_html=True)
                        cols[2].markdown(f"{doc['chunks']}")
                    st.markdown("<div style='height: 1px; background-color: rgba(255,255,255,0.05); margin: 6px 0;'></div>", unsafe_allow_html=True)

            # Document uploading (ADMIN only)
            if current_role == Role.ADMIN:
                st.markdown("---")
                st.subheader("📤 Upload New Private Document")
                
                uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])
                req_role = st.selectbox(
                    "Required Clearance Level for Document",
                    options=[r.name for r in Role],
                    index=0,
                    key="upload_clearance"
                )
                upload_btn = st.button("Process and Index Document", use_container_width=True)
                
                if upload_btn and uploaded_file is not None:
                    with st.spinner("Processing PDF and generating embeddings..."):
                        temp_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")), "data")
                        os.makedirs(temp_dir, exist_ok=True)
                        temp_path = os.path.join(temp_dir, uploaded_file.name)
                        
                        try:
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                                
                            from langchain_community.document_loaders import PyPDFLoader
                            from langchain_text_splitters import RecursiveCharacterTextSplitter
                            
                            loader = PyPDFLoader(temp_path)
                            pages = loader.load()
                            
                            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                            doc_chunks = splitter.split_documents(pages)
                            
                            # Index chunks in Qdrant
                            from qdrant_client.models import PointStruct
                            
                            retriever = st.session_state.pipeline.retriever
                            role_enum = Role.from_str(req_role)
                            
                            points = []
                            for idx, chunk in enumerate(doc_chunks):
                                vector = retriever.embedding_model.encode(chunk.page_content).tolist()
                                
                                # Enrich chunk metadata
                                chunk.metadata["source"] = uploaded_file.name
                                chunk.metadata["required_role_name"] = role_enum.name
                                chunk.metadata["required_role_level"] = role_enum.value
                                
                                payload = {
                                    "page_content": chunk.page_content,
                                    "metadata": chunk.metadata,
                                    "source": chunk.metadata.get("source", ""),
                                    "required_role_name": chunk.metadata.get("required_role_name", "ADMIN"),
                                    "required_role_level": chunk.metadata.get("required_role_level", 3)
                                }
                                
                                # Generate unique 64-bit ID from hash
                                point_id = hash(f"{uploaded_file.name}_{idx}") & 0xFFFFFFFFFFFF
                                points.append(
                                    PointStruct(
                                        id=point_id,
                                        vector=vector,
                                        payload=payload
                                    )
                                )
                            
                            retriever.client.upsert(
                                collection_name=retriever.collection_name,
                                points=points
                            )
                            
                            # Remove temp file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                                
                            st.success(f"Successfully processed, embedded, and indexed {uploaded_file.name} ({len(doc_chunks)} chunks)!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error reading PDF: {e}")
                            if os.path.exists(temp_path):
                                os.remove(temp_path)

# Tab 2: Quality Analytics (Executive and Admin)
if current_role >= Role.EXECUTIVE:
    with tabs[2]:
        st.subheader("📊 RAG Quality Analytics (Ragas)")
        st.markdown("Automated evaluation metrics measuring the quality of retrieved context and generation faithfulness.")
        
        # Trigger button
        if st.button("🚀 Trigger Ragas Quality Check", use_container_width=True):
            with st.spinner("Executing Ragas quality checks against test dataset (Llama-3 evaluation)..."):
                from app.monitoring.evaluation import run_ragas_evaluation
                res = run_ragas_evaluation()
                if res:
                    st.success(f"Evaluation complete! Faithfulness: {res.get('faithfulness', 0.0):.4f}, Answer Relevance: {res.get('answer_relevance', 0.0):.4f}")
                else:
                    st.error("Ragas evaluation run failed. Check logs for details.")
                    
        # History rendering
        st.markdown("---")
        st.subheader("📈 Historical Score Trends")
        
        import json
        history_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/eval_history.json"))
        if os.path.exists(history_path):
            try:
                with open(history_path, "r") as f:
                    history = json.load(f)
                if history:
                    import pandas as pd
                    df = pd.DataFrame(history)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    df = df.sort_values("timestamp")
                    
                    st.line_chart(df.set_index("timestamp"))
                    st.dataframe(df.style.format({"faithfulness": "{:.4f}", "answer_relevance": "{:.4f}"}))
                else:
                    st.info("No evaluation runs logged yet.")
            except Exception as e:
                st.error(f"Error loading score history: {e}")
        else:
            st.info("No evaluation history found. Click 'Trigger Ragas Quality Check' to start.")

# Tab 3: Security Audits (Admin only)
if current_role >= Role.ADMIN:
    with tabs[3]:
        st.subheader("🛡️ Security Audit Logs")
        st.markdown("Cryptographic interaction logs showing guardrail safety status and access attempts.")
        
        audit_logger = st.session_state.pipeline.audit_logger
        logs = audit_logger.read_logs()
        
        if st.button("Clear Audit Logs", type="secondary", use_container_width=True):
            if audit_logger.clear_logs():
                st.success("Audit logs cleared successfully!")
                st.rerun()
                
        if not logs:
            st.info("No security events have been logged yet.")
        else:
            # Add filter controls
            col1, col2 = st.columns(2)
            filter_role = col1.selectbox("Filter by Role", ["ALL"] + [r.name for r in Role])
            filter_status = col2.selectbox("Filter by Safety Status", ["ALL", "SAFE", "BLOCKED"])
            
            # Apply filters
            filtered_logs = logs
            if filter_role != "ALL":
                filtered_logs = [l for l in filtered_logs if l["role"] == filter_role]
            if filter_status == "SAFE":
                filtered_logs = [l for l in filtered_logs if l.get("input_is_safe", True)]
            elif filter_status == "BLOCKED":
                filtered_logs = [l for l in filtered_logs if not l.get("input_is_safe", True)]
                
            if not filtered_logs:
                st.info("No logs match the selected filters.")
            else:
                for entry in filtered_logs:
                    status_badge = "🟢 SAFE" if entry.get("input_is_safe", True) else "🔴 BLOCKED"
                    pii_badge = "⚠️ PII REDACTED" if entry.get("pii_detected", False) else "✅ NO PII"
                    
                    st.markdown(
                        f"""
                        <div style="background-color: rgba(22, 28, 45, 0.5); padding: 15px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06); margin-bottom: 12px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 0.85rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px;">
                                <span style="color: #64748b;">🕒 {entry['timestamp']}</span>
                                <span style="color: #38bdf8;">👤 User: <b>{entry['username']}</b> ({entry['role']})</span>
                            </div>
                            <p style="margin: 0 0 8px 0; font-size: 0.9rem; color: #e2e8f0;"><b>Query:</b> <i>"{entry['query']}"</i></p>
                            <div style="display: flex; gap: 20px; font-size: 0.8rem; color: #94a3b8;">
                                <span><b>Safety Status:</b> {status_badge}</span>
                                <span><b>PII:</b> {pii_badge}</span>
                                <span><b>Latency:</b> {entry['latency_ms']} ms</span>
                            </div>
                            {f'<p style="margin: 8px 0 0 0; font-size: 0.85rem; color: #f87171; background-color: rgba(239, 68, 68, 0.1); padding: 6px 10px; border-radius: 6px;">⚠️ <b>Safety Violation:</b> {entry["safety_reason"]}</p>' if not entry.get("input_is_safe", True) else ''}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )




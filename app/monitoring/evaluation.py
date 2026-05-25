import os
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.rag.pipeline import SentinelRAGPipeline

load_dotenv()

# Sample ground-truth evaluation dataset for SentinelRAG
EVAL_QUESTIONS = [
    {
        "question": "What are the major industry trends described in the IPO report?",
        "ground_truth": "The IPO report details key industry trends including rapid digital adoption, market expansion in technology sectors, and growing regulatory compliance requirements.",
        "role": "EMPLOYEE"
    },
    {
        "question": "What is the company's financial status and revenue growth detailed in the financial report?",
        "ground_truth": "The financial report shows positive revenue growth driven by cloud software sales and enterprise services, with net profit margin improving year-over-year.",
        "role": "EXECUTIVE"
    }
]

def run_ragas_evaluation():
    """
    Runs evaluation on SentinelRAG pipeline using Ragas, Groq (Llama-3), and sentence-transformers.
    """
    print("Initializing SentinelRAG pipeline for evaluation...")
    pipeline = SentinelRAGPipeline()
    
    questions = []
    contexts = []
    answers = []
    ground_truths = []
    
    print("Generating responses for test queries...")
    for item in EVAL_QUESTIONS:
        res = pipeline.run(item["question"], item["role"])
        
        questions.append(item["question"])
        answers.append(res["processed_response"])
        ground_truths.append(item["ground_truth"])
        
        # Extract page_contents from retrieved docs
        doc_contents = [doc["page_content"] for doc in res["retrieved_docs"]]
        contexts.append(doc_contents if doc_contents else ["No context retrieved."])
        
    # Build dataset dictionary
    data = {
        "question": questions,
        "contexts": contexts,
        "answer": answers,
        "ground_truth": ground_truths
    }
    
    dataset = Dataset.from_dict(data)
    
    print("Configuring Groq-based Llama-3 model for Ragas evaluation...")
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY is not configured. Cannot run evaluation.")
        return
        
    eval_llm = ChatOpenAI(
        model="llama-3.1-8b-instant",
        openai_api_key=groq_api_key,
        openai_api_base="https://api.groq.com/openai/v1"
    )
    
    eval_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Running Ragas evaluation (evaluating faithfulness and answer relevance)...")
    try:
        # Note: In older Ragas versions, metrics list and custom llm/embeddings are supported
        result = evaluate(
            dataset=dataset,
            metrics=[faithfulness, answer_relevance],
            llm=eval_llm,
            embeddings=eval_embeddings
        )
        print("\n================ RAGAS EVALUATION RESULTS ================")
        print(result)
        print("==========================================================")
        return result
    except Exception as e:
        print(f"Ragas evaluation failed: {e}")
        print("This might be due to API rate limits or network issues with the custom Groq configuration.")
        return None

if __name__ == "__main__":
    run_ragas_evaluation()

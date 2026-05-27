import os
from dotenv import load_dotenv
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from app.rag.pipeline import SentinelRAGPipeline

load_dotenv()

# Comprehensive ground-truth evaluation dataset for SentinelRAG
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
    },
    {
        "question": "Detail the risks listed in the IPO report regarding market volatility.",
        "ground_truth": "The IPO report highlights risks such as market fluctuations, interest rate changes, macroeconomic headwinds, and currency volatility impacting stock performance.",
        "role": "EMPLOYEE"
    },
    {
        "question": "Describe the executive compensation structure mentioned in the financial report.",
        "ground_truth": "The financial report outlines executive compensation consisting of base salaries, stock options, and performance-linked cash bonuses.",
        "role": "EXECUTIVE"
    },
    {
        "question": "What are the core technology assets detailed in the IPO report?",
        "ground_truth": "Core technology assets include proprietary AI algorithms, cloud-native architecture, custom cybersecurity modules, and integrated software platforms.",
        "role": "EMPLOYEE"
    },
    {
        "question": "Explain the tax liabilities and audit findings in the financial report.",
        "ground_truth": "Tax liabilities include deferred corporate taxes, overseas withholding taxes, and audit notes confirming compliance with national accounting standards.",
        "role": "EXECUTIVE"
    },
    {
        "question": "Identify the main underwriters for the company's IPO.",
        "ground_truth": "The primary underwriters listed are global investment banks including Apex Capital, Prime Securities, and Beacon Underwriting Services.",
        "role": "EMPLOYEE"
    },
    {
        "question": "What are the company's strategic growth objectives for the next five years?",
        "ground_truth": "Strategic objectives focus on global market expansion, product diversification, strategic software acquisitions, and scaling cloud service subscriptions.",
        "role": "EMPLOYEE"
    },
    {
        "question": "What is the breakdown of operating expenses in the financial report?",
        "ground_truth": "Operating expenses are divided into R&D costs, sales and marketing investments, administrative payroll, and general operational overhead.",
        "role": "EXECUTIVE"
    },
    {
        "question": "Describe the capitalization table and shareholder allocations in the IPO document.",
        "ground_truth": "The cap table indicates majority holdings by founding partners, early venture capital firms, and allocations for public retail investors.",
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

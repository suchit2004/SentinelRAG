import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()

def init_langsmith():
    """
    Initializes and verifies LangSmith environment variables.
    """
    api_key = os.environ.get("LANGCHAIN_API_KEY")
    tracing = os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    project = os.environ.get("LANGCHAIN_PROJECT", "SentinelRAG")
    
    # Set default project name if not set
    if "LANGCHAIN_PROJECT" not in os.environ:
        os.environ["LANGCHAIN_PROJECT"] = project

    if tracing and api_key and api_key != "your_langsmith_key":
        try:
            client = Client()
            print(f"LangSmith tracing enabled. Project: {project}")
            return client
        except Exception as e:
            print(f"Failed to initialize LangSmith client: {e}")
            return None
    else:
        print("LangSmith tracing is disabled or key is unconfigured. Set LANGCHAIN_API_KEY in .env and LANGCHAIN_TRACING_V2=true.")
        return None

def get_traceable_decorator():
    """
    Returns the @traceable decorator if LangSmith is configured,
    otherwise returns a dummy decorator that does nothing.
    """
    tracing = os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    api_key = os.environ.get("LANGCHAIN_API_KEY")
    
    if tracing and api_key and api_key != "your_langsmith_key":
        try:
            from langsmith import traceable
            return traceable
        except ImportError:
            pass
            
    # Dummy decorator fallback
    def dummy_decorator(*args, **kwargs):
        if len(args) == 1 and callable(args[0]):
            return args[0]
        def inner(func):
            return func
        return inner
    
    return dummy_decorator

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqLLMClient:
    def __init__(self, model_name: str = "llama-3.1-8b-instant"):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            # Check if there is an api key in the parent environment or environment variables
            raise ValueError("GROQ_API_KEY is not configured in environment variables or .env file.")
        
        self.client = Groq(api_key=self.api_key)
        self.model_name = model_name

    def generate(self, prompt: str, system_message: str = "You are a helpful security-aware assistant.", temperature: float = 0.0) -> str:
        """
        Generates text completion using the Groq API.
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error during Groq LLM generation: {e}")
            return f"Generation Error: Unable to query the LLM via Groq. Details: {e}"

import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()


class LLMClient:
    """
    Wrapper around Groq LLM API.
    Handles authentication and request formatting.
    """

    def __init__(self, model: str = "llama-3.1-8b-instant"):

        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment")

        self.client = Groq(api_key=api_key)
        self.model = model  or os.getenv("GROQ_MODEL") or "llama-3.1-8b-instant"

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """
        Send prompt to LLM and return response text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a regulatory reporting assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )

            return response.choices[0].message.content

        except Exception as e:
            raise RuntimeError(f"LLM request failed: {str(e)}")

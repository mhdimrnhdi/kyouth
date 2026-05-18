import os
import sys
from dotenv import load_dotenv

load_dotenv()

ALIASES = {
    "g25f":  "gemini-2.5-flash",
    "g25l":  "gemini-2.5-flash-lite",
    "g3f":   "gemini-3-flash-preview",
    "g31l":  "gemini-3.1-flash-lite",
    "gm26":  "gemma-4-26b-a4b-it",
    "gm31":  "gemma-4-31b-it",
    "ollama": "llama3.1",
    "ophi":  "phi3",
    "ods":   "deepseek-r1:1.5b",
}


def prompt_model(model: str, prompt: str) -> str:
    model = ALIASES.get(model, model)  # resolve alias before routing
    if "gemini" in model or "gemma" in model:
        try:
            from google import genai
            client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
            response = client.models.generate_content(model=model, contents=prompt)
            return response.text
        except Exception as e:
            return f"[Gemini Error] {e}"
    else:
        try:
            import ollama
            response = ollama.generate(model=model, prompt=prompt)
            return response.response
        except Exception as e:
            return f"[Ollama Error] {e}"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: uv run prompt_model.py <model> <prompt>")
        sys.exit(1)
    model = ALIASES.get(sys.argv[1], sys.argv[1])
    result = prompt_model(model, sys.argv[2])
    print("\n--- RESPONSE ---\n")
    print(result)
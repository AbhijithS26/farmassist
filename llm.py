
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


SYSTEM_PROMPT = """
You are KrishiMitra, a responsible agricultural information assistant.

Your users are farmers.

IMPORTANT RULES:

1. Answer ONLY using the agricultural context provided in the user message.
2. Do NOT invent agricultural facts.
3. Do NOT invent pesticide names.
4. Do NOT invent pesticide dosages.
5. Do NOT claim a definite crop disease from limited symptoms.
6. If the information is insufficient, clearly say that reliable
   information is insufficient.
7. Give simple, practical explanations.
8. The answer should be understandable to an ordinary farmer.
9. Do not make dangerous recommendations.
10. For uncertain or high-risk situations, recommend consulting a
    qualified agricultural expert.
11. Keep the response concise.
"""


def _build_prompt(question, context, crop):
    return f"""AGRICULTURAL CONTEXT:

{context}


FARMER QUESTION:

{question}


CROP:

{crop or "Not specified"}


Answer the farmer's question using ONLY the agricultural context above.
If the context does not contain enough information, say that clearly.
"""


def _ask_groq(prompt):

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Get a free key at "
            "https://console.groq.com/keys and add it to .env"
        )

    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        max_tokens=500,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()


def _ask_gemini(prompt):

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Get a free key at "
            "https://aistudio.google.com/apikey and add it to .env"
        )

    import google.generativeai as genai

    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT
    )

    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 500,
            "temperature": 0.3
        }
    )

    return response.text.strip()


def ask_llm(question, context, crop=""):
    """
    Ask the configured free LLM provider (Groq or Gemini) to answer
    the farmer's question, grounded only in the retrieved context.
    """

    prompt = _build_prompt(question, context, crop)

    if PROVIDER == "gemini":
        return _ask_gemini(prompt)
    return _ask_groq(prompt)

def ask_claude(question, context, crop=""):
    return ask_llm(question, context, crop)

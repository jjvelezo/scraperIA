import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

# LLM configuration. Reads credentials from the environment (.env file).
# Works with any OpenAI-compatible endpoint (OpenRouter, LM Studio, Ollama, ...).
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise RuntimeError(
        "OPENROUTER_API_KEY is not set. Copy .env.example to .env and add your "
        "OpenRouter API key (https://openrouter.ai/keys)."
    )

BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
MODEL = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324:free")

model = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model=MODEL,
    temperature=0.1,
    max_tokens=2000,
)

def parse_with_llm(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    parsed_results = []
    
    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            print(f"Parsed batch: {i} of {len(dom_chunks)}")
            parsed_results.append(response.content)
        except Exception as e:
            print(f"Error in batch {i}: {str(e)}")
            print("Make sure LMM is running")
    
    return "\n".join(parsed_results)

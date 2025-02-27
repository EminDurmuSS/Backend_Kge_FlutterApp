import os
import google.generativeai as genai

# Configure Gemini LLM session
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 0.65,
    "top_p": 0.9,
    "top_k": 64,
    "max_output_tokens": 65536,
    "response_mime_type": "text/plain",
}

# Create a conversation-enabled model
chat_session = genai.GenerativeModel(
    model_name="gemini-2.0-flash-thinking-exp-01-21",
    generation_config=generation_config,
).start_chat(history=[])

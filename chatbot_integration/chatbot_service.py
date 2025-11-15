import os
import requests
import json
from dotenv import load_dotenv

class ChatbotService:
    def __init__(self):
        # Load API key from .env
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise RuntimeError("HUGGINGFACE_API_KEY missing in .env")

        # HF Router endpoint
        self.api_url = "https://router.huggingface.co/v1/chat/completions"

        # Model
        self.model_name = "katanemo/Arch-Router-1.5B:hf-inference"

        # Default system instruction
        self.system_instruction = (
            "You are an e-shop assistant. ONLY answer questions about products in this shop. "
            "Do NOT provide information about anything else. "
            "If the requested product is not in the catalog, answer: 'This product is not available in our shop.'"
        )

    def get_chatbot_response(self, user_message, chat_history=None, products_text=None):
        """
        products_text — text representation of the product catalog to include in the system prompt.
        """
        if chat_history is None:
            chat_history = []

        # Create a strict system instruction including the product catalog
        system_content = self.system_instruction
        if products_text:
            system_content += f"\nHere is the product catalog:\n{products_text}"

        # Prepare messages
        messages = [{"role": "system", "content": system_content}]
        messages.extend(chat_history)
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 256
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response_json = response.json()

            # Return only the response text
            content = response_json["choices"][0]["message"]["content"]
            return {"response": content}

        except Exception as e:
            print("HF API error:", e)
            return {"response": "AI service error."}

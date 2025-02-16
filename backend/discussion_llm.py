import json
import os
from mistralai import Mistral
from dotenv import load_dotenv

from models import Product


load_dotenv()

# GET API KEY
api_key = os.environ["MISTRAL_API_KEY"]

# GET MODEL
model = "mistral-large-latest"

# CREATE MISTRAL CLIENT
client = Mistral(api_key=api_key)


# LOAD DISCUSSION SYSTEM PROMPT
system_prompt_file = open("discussion_system_prompt.txt", "r")
DISCUSSION_SYSTEM_PROMPT = system_prompt_file.read()
system_prompt_file.close()


def get_response(message: str, product: Product):
    prompt = f"""
        Voici les donnees du produit: {product}.
        Voici la question: {message}.
    """

    print("prompt: ", prompt)

    chat_response = client.chat.complete(
        model = model,
        messages = [
            #   system promtp
            {
                "role": "system",
                "content": DISCUSSION_SYSTEM_PROMPT
            },
            #   user prompt
            {
                "role": "user",
                "content": prompt,
            },
        ]
    )

    result = str(chat_response.choices[0].message.content)

    print("result: ", result)

    return json.loads(result)
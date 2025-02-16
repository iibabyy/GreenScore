
# CREATE MISTRAL CLIENT
import json
import os
from dotenv import load_dotenv
from mistralai import Mistral

from dtos import ProductDto


load_dotenv()

# GET API KEY
api_key = os.environ["MISTRAL_API_KEY"]

# GET MODEL
model = "mistral-large-latest"

# CREATE MISTRAL CLIENT
client = Mistral(api_key=api_key)

# LOAD SCORE SYSTEM PROMPT
system_prompt_file = open("score_system_prompt.txt", "r")
SCORE_SYSTEM_PROMPT = system_prompt_file.read()
system_prompt_file.close()

def get_green_score(product: ProductDto):
    chat_response = client.chat.complete(
        model = model,
        messages = [
            #   system promtp
            {
                "role": "system",
                "content": SCORE_SYSTEM_PROMPT
            },

            #   user prompt
            {
                "role": "user",
                "content": product.to_json(),
            },
        ]
    )

    result = str(chat_response.choices[0].message.content)
    print(result)

    return json.loads(result)

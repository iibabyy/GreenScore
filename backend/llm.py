import json
import os
from mistralai import Mistral
from dotenv import load_dotenv

from dtos import ProductDto

# LOAD ENV VARIABLES
load_dotenv()

# GET API KEY
api_key = os.environ["MISTRAL_API_KEY"]

# GET MODEL
model = "mistral-large-latest"

# CREATE MISTRAL CLIENT
client = Mistral(api_key=api_key)

# LOAD SYSTEM PROMPT
system_prompt_file = open("system_prompt.txt", "r")
SYSTEM_PROMPT = system_prompt_file.read()
system_prompt_file.close()


def get_green_score(product: ProductDto):
    chat_response = client.chat.complete(
        model = model,
        messages = [
            #   system promtp
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            #   user prompt
            {
                "role": "user",
                "content": str(product),
            },
        ]
    )

    return json.loads(str(chat_response.choices[0].message.content))

# print(get_green_score(
#     {
#       "name": "Insulix",
#       "type": "Antidiabetic",
#       "active_ingredient": "Insulin",
#       "concentration": "100 IU/ml",
#       "administration_route": "Injected",
#       "degradability": {
#         "water": "90%",
#         "soil": "10%",
#         "degradation_duration": "6 months"
#       },
#       "toxicity": {
#         "aquatic": "Very low",
#         "terrestrial": "Very low",
#         "wildlife_impact": "No significant impact"
#       },
#       "production": {
#         "energy_consumed": "50 kWh/kg",
#         "co2_emissions": "0.1 kg CO2/kg",
#         "chemical_waste": "2 kg/kg"
#       },
#       "disposal": {
#         "recyclable": "No",
#         "hazardous_waste": "Yes",
#         "recommendations": "Syringe collection at pharmacies"
#       }
#     }
# ))
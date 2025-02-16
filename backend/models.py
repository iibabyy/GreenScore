import json
import uuid
from dtos import ProductDto
from llm import get_green_score
from pydantic import BaseModel

class DescriptionField(BaseModel):
	score: int
	details: str

class ProductDescription(BaseModel):
	persistence: DescriptionField
	bioaccumulation: DescriptionField
	toxicity: DescriptionField
	ecotoxicological_effects: DescriptionField
	degradation_byproducts: DescriptionField
	release_into_environment: DescriptionField
	regulatory_status: DescriptionField
	mitigation_strategies: list[str]



class Product:
	def __init__(self, infos: ProductDto):
		print("infos: ", infos)
		self.id = uuid.uuid4()
		self.name = infos.name.lower()
		self.infos = infos;

		# Get the green score and description
		green_result = get_green_score(self.infos)
		self.note: int = int(green_result["score"])
		# print(green_result["description"])
		self.description: ProductDescription = green_result["description"]

	def __repr__(self):
		return f"Product(id={self.id}, name={self.name}, greenScore={self.greenScore}, pertinence={self.pertinence})"
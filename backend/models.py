import json
import uuid
from dtos import ProductDto
from score_llm import get_green_score
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
		self.id = uuid.uuid4()
		self.name = infos.name
		self.infos = infos;
		self.picture = infos.picture

		product = ProductDto(
			name=infos.name,
			type=infos.type,
			picture=infos.picture,
			active_ingredient=infos.active_ingredient,
			concentration=infos.concentration,
			administration_route=infos.administration_route,
			degradability=infos.degradability,
			toxicity=infos.toxicity,
			production=infos.production,
			disposal=infos.disposal
		)
		# Get the green score and description
		green_result = get_green_score(product)
		self.note: float = float(green_result["score"])
		# print(green_result["description"])
		description = green_result["description"]
		self.description = ProductDescription(
			persistence=DescriptionField(
				score=int(description["persistence"]["score"]),
				details=description["persistence"]["details"]
			),
			bioaccumulation=DescriptionField(
				score=int(description["bioaccumulation"]["score"]),
				details=description["bioaccumulation"]["details"]
			),
			toxicity=DescriptionField(
				score=int(description["toxicity"]["score"]),
				details=description["toxicity"]["details"]
			),
			ecotoxicological_effects=DescriptionField(
				score=int(description["ecotoxicological_effects"]["score"]),
				details=description["ecotoxicological_effects"]["details"]
			),
			degradation_byproducts=DescriptionField(
				score=int(description["degradation_byproducts"]["score"]),
				details=description["degradation_byproducts"]["details"]
			),
			release_into_environment=DescriptionField(
				score=int(description["release_into_environment"]["score"]),
				details=description["release_into_environment"]["details"]
			),
			regulatory_status=DescriptionField(
				score=int(description["regulatory_status"]["score"]),
				details=description["regulatory_status"]["details"]
			),
			mitigation_strategies=description["mitigation_strategies"]
		) # type: ignore
		
	def __repr__(self):
		return f"Product(id={self.id}, name={self.name}, greenScore={self.note})"
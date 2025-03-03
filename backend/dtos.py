
import json
import uuid
from pydantic import BaseModel


class DegradabilityDto(BaseModel):
	water: str
	soil: str
	degradation_duration: int	# in month

class ToxicityDto(BaseModel):
	aquatic: str
	terrestrial: str
	wildlife_impact: str | None

class ProductionsDto(BaseModel):
	energy_consumed: int	# in kWh/kg
	co2_emissions: float		# in kg CO2/kg
	chemical_waste: int		# in kg/kg

class DisposalDto(BaseModel):
	recyclable: bool
	hazardous_waste: bool
	recommendations: str | None = None

class ProductDto(BaseModel):
		name: str
		type: str
		picture: str
		active_ingredient: str
		concentration: int		# in mg
		administration_route: str
		degradability: DegradabilityDto
		toxicity: ToxicityDto
		production: ProductionsDto
		disposal: DisposalDto

		def to_json(self) -> str:
				return json.dumps(
					self,
					default=lambda o: o.__dict__,
					indent=4
				)


class MessageDto(BaseModel):
		sender: str
		content: str

class DiscussionDto(BaseModel):
		prompt: str
		product_id: uuid.UUID

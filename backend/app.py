import json
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from dtos import ProductDto, DiscussionDto
from discussion_llm import get_response
from models import Product
from types import SimpleNamespace


def get_product_list() -> list[Product]:
	file = open("products.json", "r", encoding="utf-8")
	product_data = file.read()

	file.close()

	load = json.loads(product_data)
	return [Product(ProductDto(
		name= product["name"],
		type= product["type"],
		active_ingredient= product["active_ingredient"],
		concentration= product["concentration"],
		degradability= product["degradability"],
		toxicity= product["toxicity"],
		disposal= product["disposal"],
		production= product["production"],
		administration_route= product["administration_route"],
	)) for product in load["medications"]]

app = FastAPI()

products: list[Product] = get_product_list()

def product_by_id(id: uuid.UUID) -> Product | None:
		for product in products:
			if product.id == id:
				return product

		return None

@app.get("/products/search/{search}")
def index(search: str, sort: str = "default"):
		# maybe split search by space and search for keywords

		list = [product for product in products if search in product.name];

		list.sort(key=lambda x: x.note, reverse=True)

		return list

@app.post("/ai/discussion")
def respond(body: DiscussionDto, response: Response):
	product = product_by_id(body.product_id)
	if product is None:
		response.status_code = 404
		return {"error": "Product not found"}
	
	reponse = get_response(body.prompt, product)
	return {"response": reponse}


@app.get("/products/{id}")
def index(id: uuid.UUID, response: Response, sort: str = "default"):
		for product in products:
			if product.id == id:
				return product

		response.status_code = 404
		return {"error": "Product not found"}

# @app.post("/products")
# def create_product(body: ProductDto, response: Response):
# 		try:
# 			product = Product(body)
# 		except json.decoder.JSONDecodeError as e:
# 				print(f"Erreur de parsing: {e}")
# 				print(f"Position de l'erreur: {e.pos}")
# 				response.status_code = 400
# 				return {"error": "Invalid JSON"}

# 		products.append(product)
# 		return product

@app.get("/")
def index():
		return {"message": "Hello, World!"}


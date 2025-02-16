import json
import uuid
from fastapi import FastAPI, Response
from pydantic import BaseModel
from dtos import ProductDto
from models import Product
from types import SimpleNamespace

def read_products_from_file() -> list[Product]:
	# open and read the products file
	file = open("./products.json", "r")
	data = file.read()
	file.close()

	products: list[Product] = json.loads(data, object_hook=lambda x: SimpleNamespace(**x))
	print("products: ", products)

	return products

products: list[Product] = read_products_from_file()

app = FastAPI()

@app.get("/products/search/{search}")
def index(search: str, sort: str = "default"):
		# maybe split search by space and search for keywords

		list = [product for product in products if search in product.name];

		if sort == "name":
			list.sort(key=lambda x: x.note, reverse=False)
		else:
			list.sort(key=lambda x: x.note, reverse=False)

		return list

@app.get("/products/{id}")
def index(id: int, response: Response, sort: str = "default"):
		for product in products:
			if product["id"] == id:
				product["pertinence"] += 1
				return product

		response.status_code = 404
		return {"error": "Product not found"}

@app.post("/products")
def create_product(body: ProductDto):
		product = Product(body)

		products.append(product)
		return product

@app.get("/")
def index():
		return {"message": "Hello, World!"}


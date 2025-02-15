import json
import uuid
from fastapi import FastAPI, Response
from pydantic import BaseModel
from dtos import ProductDto
from models import Product

products: list[Product] = []

app = FastAPI()

@app.get("/products/search/{search}")
def index(search: str, sort: str = "default"):
		# maybe split search by space and search for keywords

		list = [product for product in products if search in product["name"]];

		if sort == "score":
			list.sort(key=lambda x: x["greenScore"], reverse=True)
		elif sort == "name":
			list.sort(key=lambda x: x["name"], reverse=False)
		elif sort == "default":
			list.sort(key=lambda x: x["pertinence"], reverse=True)

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


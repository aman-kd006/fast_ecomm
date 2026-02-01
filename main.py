from dotenv import load_dotenv
import os
from fastapi import FastAPI, Query, HTTPException, Path, Depends, Request
from fastapi.responses import JSONResponse
from services.serve_product import(
get_all_products, 
add_product, 
remove_product,
change_product,
load_products
)
from schema.product import Product, Update_Product, ProductListResponse
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict

load_dotenv()
app = FastAPI(title="FastAPI E-commerce Product Service", version="1.0.0")

@app.get("/health")
def health_check():
    DB_PATH= os.getenv("BASE_URL")
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "data_path": DB_PATH}
    )

@app.get("/products", response_model=ProductListResponse)
def list_products(
    dep=Depends(load_products),
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Filter products by name"
    ),
    sort_by_price: bool = Query(
        default=False,
        description="Sort products by price ascending"
    ),
    order: str = Query(
        default="asc",
        description="Order of sorting: 'asc' or 'desc'"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Limit the number of products returned"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Offset the number of products returned"
    )
 ):

    products = dep

    if name:
        link = name.strip().lower()
        products = [p for p in products if link in p .get("name", "").lower()]
        
        if not products:
            raise HTTPException(status_code=404, detail=f"No product found with name={name}")
    
    if sort_by_price:
        reverse = order == "desc"
        products.sort(key=lambda x: x.get("price", 0), reverse=reverse)

    total = len(products)
    
    products = products[offset : offset +limit]

    return {"total": total, "items": products}

@app.get("/products/{product_id}")
def get_product_by_id(product_id : str = Path(
    ...,
    min_length=36,
    max_length=36,
    description="The UUID of the product to retrieve",
    example="2f54696f-d3e1-32a3-a3ef-d8593fae2d7b")
):
    products = get_all_products()
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code = 404, detail="Product is unavailable.")

@app.post("/products", status_code=201)
def create_product(product: Product):
    product_dict = product.model_dump(mode="json")
    product_dict["id"] = str(uuid4())
    product_dict["created_at"] = datetime.utcnow().isoformat() + "Z"
    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return product.model_dump(mode="json")

@app.delete("/products/{product_id}")
def delete_product(product_id:UUID = Path(
    ...,
    description="The UUID of the product to delete",
    example="2f54696f-d3e1-32a3-a3ef-d8593fae2d7b"
)):
    try:
        result = remove_product(str(product_id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.put("/products/{product_id}")
def update_product(
    product_id:UUID = Path(
        ...,
        description="The UUID of the product to update",
        example="2f54696f-d3e1-32a3-a3ef-d8593fae2d7b"
    ),
    payload: Update_Product = ...
):
    try:
        updated_product = change_product(
        str(product_id), 
        payload.model_dump(mode="json", exclude_unset=True))
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.patch("/products/{product_id}")
def patch_product(
    product_id:UUID = Path(
        ...,
        description="The UUID of the product to update",
        example="2f54696f-d3e1-32a3-a3ef-d8593fae2d7b"
    ),
    payload: Update_Product = ...
):
    try:
        updated_product = change_product(
        str(product_id), 
        payload.model_dump(mode="json", exclude_unset=True))
        return updated_product
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
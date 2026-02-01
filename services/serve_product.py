from pathlib import Path
from typing import List, Dict
import json

DATA_FILE = Path(__file__).parent.parent / "data" / "products.json"

def load_products():
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)
    
def get_all_products() -> List[Dict]:
    return load_products()

def save_products(products: List[Dict]) -> None:
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def add_product(product: Dict) -> None:
    products=get_all_products()
    if any(p["sku"]==product["sku"] for p in products):
        raise ValueError(f"Product with SKU {product['sku']} already exists.")
    products.append(product)
    save_products(products)
    return product

def remove_product(id: str) -> Dict:
    products=get_all_products()
    for idx, p in enumerate(products):
        if p["id"] == id:
            deleted= products.pop(idx)
            save_products(products)
            return {"message": "Product deleted succesfully",
                    "product": deleted}
        
def change_product(id:str, update_data:List[Dict]):
    products=get_all_products()

    for index, product in enumerate(products):

        for key, value in update_data.items():
            if value is None:
                continue

            if isinstance(value, dict) and isinstance(product.get(key), dict):
                product[key].update(value)
            else:
                product[key] = value

        products[index] = product
        save_products(products)
        return product

    raise ValueError(f"Product with id {id} not found.")

        
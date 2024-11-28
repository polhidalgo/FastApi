from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/item/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id, "nombre": "Item de prueba"}

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    in_stock: bool

@app.post("/items/")
def create_item(item: Item):
    return {"message": "Item created successfully", "item": item}
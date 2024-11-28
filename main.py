from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/item/{item_id}")
def read_item(item_id: int):
    if item_id != 1:  # Simulant un únic element disponible
        return JSONResponse(
            status_code=404,
            content={"message": "Item not found"}
        )
    return {"item_id": item_id, "name": "Sample Item"}
class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    in_stock: bool

@app.post("/items/")
def create_item(item: Item):
    return {"message": "Item created successfully", "item": item}
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = Field(None, max_length=300)
    price: float = Field(..., gt=0)

@app.post("/items/")

async def create_item(item: Item):
    return item
class Address(BaseModel):
    street: str
    city: str

class User(BaseModel):
    name: str
    address: Address

@app.post("/users/")
async def create_user(user: User):
    return user
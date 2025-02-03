from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import random

app = FastAPI()

# Load data from CSV file
file_path = "paraules_temàtica_penjat.csv"
df = pd.read_csv(file_path)

data = df.to_dict(orient="records")

# Extract unique themes
def get_unique_themes():
    themes = {item["THEME"] for item in data}
    return list(themes)

# Get words by theme
def get_words_by_theme(theme):
    words = [item["WORD"] for item in data if item["THEME"] == theme]
    return words

# Pydantic models
class ThemeOption(BaseModel):
    option: str

class WordOption(BaseModel):
    option: str

@app.get("/penjat/tematica/opcions", response_model=list[ThemeOption])
async def get_tematica_opcions():
    themes = get_unique_themes()
    return [{"option": theme} for theme in themes]

@app.get("/penjat/tematica/{option}", response_model=list[WordOption])
async def get_paraula_per_tematica(option: str):
    words = get_words_by_theme(option)
    if not words:
        raise HTTPException(status_code=404, detail="Temàtica no trobada o sense paraules.")
    random_word = random.choice(words)
    return [{"option": random_word}]

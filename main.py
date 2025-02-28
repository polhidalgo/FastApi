from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import options_sch
import read
import conn
from datetime import datetime


app = FastAPI()
conn = conn.connection_db()

# Model per a les dades de la partida

class Option(BaseModel):
    theme: str

class word(BaseModel):
    word: str


@app.get("/")
async def root():
   return {"message":"Benvingut a fastapi"}

class GameRecord(BaseModel):
    user_id: int
    theme: str
    start_game: datetime

# Model per iniciar una partida
class GameStart(BaseModel):
    user_id: int
    theme: str

# Model per registrar un intent
class Attempt(BaseModel):
    user_id: int
    game_id: int
    letter: str
    current_attempt: int

# Model per la resposta de l'abecedari
class AlphabetResponse(BaseModel):
    alphabet: List[str]

# Model per les estadístiques d'un usuari
class ScoreResponse(BaseModel):
    current_points: int
    total_games: int
    games_won: int
    best_game: int

# Endpoint per començar una partida
@app.post("/game/start")
async def start_game(game: GameStart):
    # 1. Inserir un registre de la partida a la base de dades.
    # Suposant que tens un model GameRecord i una sessió de BD (db_session):
    game_record = GameRecord(
        user_id=game.user_id,
        theme=game.theme,
        start_time=datetime.now()
    )
    conn.add(game_record)
    conn.commit()
    
    # 2. Recuperar la llista de paraules per a la temàtica seleccionada.
    word = options_sch.options_schema(read.read_word_db(game.theme))
    if not word:
        raise HTTPException(status_code=404, detail="No hi ha paraules disponibles per aquesta temàtica")
    
    game_record.secret_word = word
    conn.commit()
    # 3. Retornar la informació de la partida.
    # Nota: per a jocs com el penjat, potser no vols enviar la paraula secreta al client.
    return {
        "message": "Partida iniciada",
        "game_id": game_record.id,
        "user_id": game.user_id,
        "theme": game.theme,
    }

# Endpoint per obtenir l'abecedari
@app.get("/alphabet", response_model=AlphabetResponse)
async def get_alphabet():
    # Es pot definir l'abecedari manualment, afegint lletres especials si cal.
    alphabet = list("ABCDEFGHIJKLMNÑOPQRSTUVWXYZ")
    return {"alphabet": alphabet}

# Endpoint per obtenir les estadístiques d'un usuari
@app.get("/user/{user_id}/score", response_model=ScoreResponse)
async def get_user_score(user_id: int):
    # Aquí s'hauria de consultar la BD per obtenir les estadístiques del joc per l'usuari.
    # Aquesta és només una resposta d'exemple.
    return {
        "current_points": 50,
        "total_games": 10,
        "games_won": 6,
        "best_game": 80
    }

# Mètode per extreure les 5 opcions i podre-les mostrar a la llista de selecció d'opcions del penjat
@app.get("/penjat/tematica/opcions", response_model = List[dict])
async def get_options():
   return options_sch.options_schema(read.read_db())


# En aquesta consulta get ecaldrà que el frontend envii a {option} la opció seleccionada en la llista del joc
@app.get("/penjat/tematica/{option}", response_model = List[dict])
async def get_word(option: str):
   word = options_sch.options_schema(read.read_word_db(option))
   print("")
   print("IMPRESSIÓ WORD del mètode GET_WORD")
   print(type(word))
   print(word)
  
   return word



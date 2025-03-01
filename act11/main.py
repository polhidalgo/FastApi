from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import psycopg2
from psycopg2 import sql
import options_sch
import read
import conn
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conn = conn.connection_db()

# Model per a les dades de la partida

class UserCreate(BaseModel):
    nom: str
    email: str
    password: str

class Option(BaseModel):
    theme: str

class word(BaseModel):
    word: str

class StartGameRequest(BaseModel):
    usuari_id: int
    theme: str

class GameResult(BaseModel):
    game_id: int
    resultado: str
    puntos: int 
    
class UserLogin(BaseModel):
    email: str
    password: str
    
@app.get("/")
async def root():
   return {"message":"Benvingut a fastapi"}



@app.post("/start")
async def start_game(game: StartGameRequest):
    secret_options = options_sch.options_schema(read.read_word_db(game.theme))
    if not secret_options:
        raise HTTPException(status_code=404, detail="No hay palabras disponibles para este tema")
    
    secret_word = secret_options[0]["option"]
    cursor = conn.cursor()
    
    try:
        insert_query = """
            INSERT INTO registre_joc (usuari_id, punts, intents, secret_word, estado)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        cursor.execute(insert_query, (game.usuari_id, 0, 0, secret_word, "en_progreso"))
        game_id = cursor.fetchone()[0]
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    finally:
        cursor.close()
    
    return {
        "message": "Partida iniciada",
        "game_id": game_id,
        "usuari_id": game.usuari_id,
        "theme": game.theme
    }
    
@app.get("/games")
def get_all_games():
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, usuari_id, data_joc, punts, intents, secret_word, estado 
            FROM registre_joc
        """)
        rows = cur.fetchall()
        cur.close()
        
        games = []
        for row in rows:
            games.append({
                "game_id": row[0],
                "usuari_id": row[1],
                "data_joc": row[2],
                "puntos": row[3],
                "intentos": row[4],
                "secret_word": row[5],
                "estado": row[6]
            })
        
        return {"games": games}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener las partidas: {e}")
    
@app.get("/users/{user_id}/stats")
def get_user_stats(user_id: int):
    try:
        cur = conn.cursor()

        cur.execute("SELECT COALESCE(SUM(punts), 0) FROM registre_joc WHERE usuari_id = %s", (user_id,))
        total_points = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM registre_joc WHERE usuari_id = %s", (user_id,))
        total_games = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM registre_joc WHERE usuari_id = %s AND estado = 'ganado'", (user_id,))
        games_won = cur.fetchone()[0]
        
        cur.execute("""
            SELECT data_joc, punts 
            FROM registre_joc
            WHERE usuari_id = %s
            ORDER BY punts DESC
            LIMIT 1
        """, (user_id,))
        best_game_row = cur.fetchone()
        
        best_game_date = None
        best_game_points = 0
        
        if best_game_row:
            best_game_date = best_game_row[0]  
            best_game_points = best_game_row[1]  
        
        cur.close()
        
        return {
            "user_id": user_id,
            "total_points": total_points,
            "total_games": total_games,
            "games_won": games_won,
            "best_game_date": best_game_date,
            "best_game_points": best_game_points
        }
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")

    
@app.post("/game/{game_id}/finish")
def finish_game(game_id: int, game_result: GameResult):
    if game_result.resultado not in ["ganado", "perdido"]:
        raise HTTPException(status_code=400, detail="Estado inválido. Debe ser 'ganado' o 'perdido'.")
    
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE registre_joc SET estado = %s, punts = %s WHERE id = %s",
            (game_result.resultado, game_result.puntos, game_id)
        )
        conn.commit()
        cur.close()
        return {"message": f"Partida {game_id} marcada como {game_result.resultado} con {game_result.puntos} puntos"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al actualizar la partida: {e}")

@app.post("/login")
def login(user: UserLogin):
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, nom, email FROM usuaris WHERE email = %s AND password = %s",
            (user.email, user.password)
        )
        result = cur.fetchone()
        cur.close()
        if not result:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        return {"id": result[0], "nom": result[1], "email": result[2]}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error en login: {e}")
    
@app.get("/users")
def get_users():
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nom, email FROM usuaris;")
        rows = cur.fetchall()
        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "nom": row[1],
                "email": row[2]
            })
        cur.close()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener usuarios: {e}")
    
@app.post("/users")
def create_user(user: UserCreate):
    try:
        cur = conn.cursor()

        insert_query = sql.SQL("""
            INSERT INTO usuaris (nom, email, password)
            VALUES (%s, %s, %s)
            RETURNING id;
        """)

        cur.execute(insert_query, (user.nom, user.email, user.password))

        user_id = cur.fetchone()[0]
        conn.commit()

        cur.close()

        return {"id": user_id, "nom": user.nom, "email": user.email}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear el usuario: {e}")
    
@app.get("/game/{game_id}/secret")
def get_secret_word(game_id: int):
    try:
        cur = conn.cursor()
        cur.execute("SELECT secret_word FROM registre_joc WHERE id = %s;", (game_id,))
        result = cur.fetchone()
        cur.close()
        if not result:
            raise HTTPException(status_code=404, detail="Partida no encontrada")
        return {"game_id": game_id, "secret_word": result[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
    
@app.get("/alphabet")
def get_alphabet(extended: bool = False):
    base_alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    if extended:
        extra_letters = ["Ñ", "Ç", "Á", "É", "Í", "Ó", "Ú", "À", "È", "Ò", "Ù"]
        alphabet = base_alphabet + extra_letters
    else:
        alphabet = base_alphabet
    return {"alphabet": alphabet}


# Mètode per extreure les 5 opcions i podre-les mostrar a la llista de selecció d'opcions del penjat
@app.get("/penjat/tematica/opcions", response_model = List[dict])
async def get_options():
   return options_sch.options_schema(read.read_db())





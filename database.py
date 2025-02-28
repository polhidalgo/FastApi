import psycopg2

def create_table():
    conn = psycopg2.connect(
        database="penjat",
        user="user",
        password="pass",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS paraules (
        id SERIAL PRIMARY KEY,
        word TEXT NOT NULL,
        theme TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS usuaris (
        id SERIAL PRIMARY KEY,
        nom TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)
    
    # Taula registre de joc
    cur.execute("""
    CREATE TABLE IF NOT EXISTS registre_joc (
        id SERIAL PRIMARY KEY,
        usuari_id INTEGER REFERENCES usuaris(id),
        data_joc TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        punts INTEGER NOT NULL,
        intents INTEGER NOT NULL
    );
    """)
    
    # Taula per a informació de la pantalla principal
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pantalla_principal (
        id SERIAL PRIMARY KEY,
        usuari_id INTEGER REFERENCES usuaris(id),
        punts_actuals INTEGER,
        total_partides INTEGER,
        partides_guanyades INTEGER,
        millor_partida INTEGER
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_table()
    print("Las taules s'han creat.")
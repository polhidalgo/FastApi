import psycopg2

def insert_users():
    # Conectar a la base de datos
    conn = psycopg2.connect(
        database="penjat",
        user="user",
        password="pass",
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()
    

    sql = "INSERT INTO usuaris (nom, email, password) VALUES (%s, %s, %s);"
    
 
    users = []
    for i in range(10):
        nom = f"User {i+1}"
        email = f"user{i+1}@example.com"
        password = f"password{i+1}"  
        users.append((nom, email, password))
    
    # Insertar todos los usuarios de una sola vez
    cur.executemany(sql, users)
    conn.commit()
    
    cur.close()
    conn.close()
    
    return {"Message": "10 usuarios insertados"}

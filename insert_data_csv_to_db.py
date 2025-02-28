import psycopg2
def insert_data_csv_to_db(pos, data):

    conn = psycopg2.connect(
        database="penjat",
        user="user",
        password="pass",
        host="localhost",
        port="5432"
    )

    cur = conn.cursor()
    sql = "INSERT INTO paraules (word, theme) VALUES (%s, %s);"

    values = ((data.get("WORD")[pos], data.get("THEME")[pos]))

    cur.execute(sql, values)
    conn.commit()

    cur.close()
    conn.close()

    return {"Message":"Data inerted"}
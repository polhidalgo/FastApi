import conn
import pandas as pd
import numpy as np


read_conn = conn.connection_db()
def read_db():


   sql = "SELECT theme FROM paraules"


   df = pd.read_sql_query(sql, read_conn)
   options = df['theme'].unique()


   return options


def read_word_db(option):


   cursor = read_conn.cursor()


   sql = "SELECT word FROM paraules WHERE theme = %s;"
   values = (option,)
   cursor.execute(sql, values)


   options = cursor.fetchall()
   option = options[np.random.randint(len(options))]


   return option


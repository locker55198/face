import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='fyp.mysql.database.azure.com',
        user='ming',
        password='P@ss0wrd',
        database='fyp'
    )
    return conn

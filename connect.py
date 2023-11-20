import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='fyp.mysql.database.azure.com',
        user='ming',
        password='P@ssw0rd',
        database='fyp'
    )
    return conn

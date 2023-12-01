import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='uwefyp.mysql.database.azure.com',
        user='ming',
        password='P@ssw0rd',
        database='fyp'
    )
    return conn

def update_vote(candidate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE facevote SET vote = %s", (candidate,))

    conn.commit()
    cursor.close()
    conn.close()

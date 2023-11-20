import os

from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for, flash
from connect import get_db_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fypfacevote'

@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        conn = get_db_connection()
        cursor = conn.cursor()

        sql_check = "SELECT * FROM facevote WHERE name = %s"
        cursor.execute(sql_check, (name,))
        result = cursor.fetchone()

         if result:
            error_message = 'Name already exists. Please choose a different name.'
            cursor.close()
            conn.close()
            return redirect(url_for('index', message=error_message))
    else:
        sql = "INSERT INTO facevote (name) VALUES (%s)"
        cursor.execute(sql, (name,))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index', message='Registration successful'))
       
    return render_template('register.html')
    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/vote')
def vote():
    return render_template('vote.html')

if __name__ == '__main__':
    app.debug = True
    app.run()

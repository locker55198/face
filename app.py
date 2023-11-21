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
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']

        sql_check = "SELECT * FROM facevote WHERE name = %s"
        cursor.execute(sql_check, (name,))
        result = cursor.fetchone()

        if result:
            cursor.close()
            conn.close()
            return redirect(url_for('register', error_message='Name already exists. Please choose a different name'))
        else:
            sql = "INSERT INTO facevote (name) VALUES (%s)"
            cursor.execute(sql, (name,))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index', success_message='Registration successful'))

    cursor.close()
    conn.close()
    return render_template('register.html', success_message=request.args.get('success_message'), error_message=request.args.get('error_message'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']

        conn = get_db_connection()
        cursor = conn.cursor()

        sql_check = "SELECT * FROM facevote WHERE name = ? AND vote = 0"
        cursor.execute(sql_check, (name,))
        result = cursor.fetchone()

        if result:
              cursor.close()
              conn.close()
             return redirect(url_for('vote', success_message='Login successful'))
        else:
            return render_template('login.html', error='Invalid login')

    return render_template('login.html')
   
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        candidate = request.form['candidate']

        conn = get_db_connection()
        cursor = conn.cursor()

        sql_update = "UPDATE facevote SET vote = 1 WHERE name = %s" % (candidate,)
        cursor.execute(sql_update)
        conn.commit()

        cursor.close()
        conn.close()

        return "Vote submitted successfully."

    return render_template('vote.html')


if __name__ == '__main__':
    app.debug = True
    app.run()

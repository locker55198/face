import os
from base64 import b64decode
import numpy as np
import cv2
from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for, flash, session
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
        image_base64 = request.form['image']

        # 将Base64编码的图像数据解码为字节流
        image_data = b64decode(image_base64)
        
        conn = get_db_connection()
        cursor = conn.cursor()

        sql_check = "SELECT * FROM facevote WHERE name = %s"
        cursor.execute(sql_check, (name,))
        result = cursor.fetchone()

        if result:
            cursor.close()
            conn.close()
            return redirect(url_for('register', error_message='Name already exists. Please choose a different name'))
        else:
            sql = "INSERT INTO facevote (name, image) VALUES (%s, %s)"
            cursor.execute(sql, (name, image_data))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('index', success_message='Registration successful'))

    return render_template('register.html', success_message=request.args.get('success_message'), error_message=request.args.get('error_message'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    return render_template('login.html')
   
@app.route('/vote', methods=['GET', 'POST'])
def vote():
    if request.method == 'POST':
        candidate = request.form['vote']
        name = session.get('name')

        if name is None:
            return redirect(url_for('login'))

        conn = get_db_connection()
        cursor = conn.cursor()

        sql_update = "UPDATE facevote SET vote = %s WHERE name = %s"
        cursor.execute(sql_update, (candidate, name))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('index', success_message='Vote successful'))

    return render_template('vote.html')


if __name__ == '__main__':
    app.debug = True
    app.run()

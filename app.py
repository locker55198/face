import os
from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for, flash, session
from connect import get_db_connection
from base64 import b64decode

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        image_base64 = request.form['image']

        image_data = np.frombuffer(b64decode(image_base64), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Add your face recognition logic here
        # label, confidence = face_recognizer.predict(gray_image)
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute("SELECT * FROM facevote WHERE id=?", (label,))
        # user = cursor.fetchone()

        # if confidence < 100 and user is not None and user[1] == name:
        #     session['name'] = name
        #     cursor.close()
        #     conn.close()
        #     return redirect(url_for('vote', success_message='Login successful'))
        # else:
        #     cursor.close()
        #     conn.close()
        #     return render_template('login.html', error='Invalid login')

        # For testing purposes, always redirect to the vote page
        conn = get_db_connection()
        cursor = conn.cursor()
        sql_check = "SELECT * FROM facevote WHERE name = %s and vote = 0"
        cursor.execute(sql_check, (name,))
        result = cursor.fetchone()
        
        if result:
            session['name'] = name
            cursor.close()
            conn.close()
            return redirect(url_for('vote', success_message='Login successful'))
        else:
            cursor.close()
            conn.close()
            return render_template('login.html', error='Invalid login')
    
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
        cursor.execute("UPDATE facevote SET vote = %s WHERE name = %s", (candidate, name))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index', success_message='Vote successful'))
    
    return render_template('vote.html')

if __name__ == '__main__':
    app.debug = True
    app.run()

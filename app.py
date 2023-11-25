import os
from base64 import b64decode
import numpy as np
import cv2
import hashlib
from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for, flash, session, Response
from connect import get_db_connection
from deepface_detection import start_face_detection, is_face_matched

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fypfacevote'

face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

face_recognizer = cv2.face.LBPHFaceRecognizer_create()
face_recognizer.read('models/haarcascade_frontalface_alt_tree.xml')

cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        ret, frame = cap.read()

        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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

        image_data = b64decode(image_base64)

        image_hash = hashlib.sha256(image_data).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()

        sql_check = "SELECT * FROM facevote WHERE image_hash = %s"
        cursor.execute(sql_check, (image_hash,))
        result = cursor.fetchone()

        if result:
            cursor.close()
            conn.close()
            return redirect(url_for('register', error_message='Image already exists for another user'))

        sql = "INSERT INTO facevote (name, image, imagehash) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, image_data, image_hash))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index', success_message='Registration successful'))

    return render_template('register.html', success_message=request.args.get('success_message'), error_message=request.args.get('error_message'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        image_base64 = request.form['image']

        image_data = np.frombuffer(b64decode(image_base64), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        label, confidence = face_recognizer.predict(gray_image)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM facevote WHERE id=?", (label,))
        user = cursor.fetchone()

        if confidence < 100 and user is not None and user[1] == name:
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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   
if __name__ == '__main__':
    app.debug = True
    app.run()

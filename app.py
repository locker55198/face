import os
from base64 import b64decode
import pickle
import numpy as np
import cv2
from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for, flash, session
from connect import get_db_connection
from deepface_detection import start_face_detection, is_face_matched

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fypfacevote'

# 加載人臉檢測器
face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

# 打開網絡攝像頭
cap = cv2.VideoCapture(0)

def generate_frames():
    while True:
        # 讀取當前幀的圖像
        ret, frame = cap.read()

        if not ret:
            break

        # 將圖像轉換為灰度
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 人臉檢測
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # 在圖像上劃出人臉框
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # 轉換圖像格式為JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # 返回圖像幀
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
    if request.method == 'POST':
        name = request.form['name']
        image_base64 = request.form['image']

        image_data = np.frombuffer(b64decode(image_base64), np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
       
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
        sql_update = "UPDATE facevote SET vote = %s WHERE name = %s"
        cursor.execute(sql_update, (candidate, name))
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

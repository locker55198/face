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

def register_face(name, image_path):
    cap = cv2.VideoCapture(0)

    faceCascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")

    if not cap.isOpened():
        print("Not Cam")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Not Image")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        cv2.imshow("Register", frame)

        if cv2.waitKey(1) == ord('q'):
            cv2.imwrite(image_path, frame)
            break

    cap.release()

    cv2.destroyAllWindows()

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO facevote (name, image) VALUES (%s, %s)"
        values = (name, image_path)
        cursor.execute(query, values)
        conn.commit()
        print("Register Suggest {}！".format(name))
    except mysql.connector.Error as error:
        print("DataBase Error: {}".format(error))
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

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
   
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   
if __name__ == '__main__':
    app.debug = True
    app.run()

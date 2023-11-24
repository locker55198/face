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
   
def generate_frames():
    while True:
        frame = get_frame_with_overlay()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def get_frame_with_overlay():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Error")

    ret, frame = cap.read()

    if ret:
        if is_face_matched():
            cv2.putText(frame, "MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(frame, "NO MATCH!", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    cap.release()

    return frame

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
   
if __name__ == '__main__':
    app.debug = True
    app.run()

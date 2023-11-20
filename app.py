import os

from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, url_for, Response
import cv2
import math
import time
import cvzone
from waitress import serve
from PIL import Image
import numpy as np
import json
import onnxruntime as ort
from ultralytics import YOLO
from connect import get_db_connection

app = Flask(__name__)

def detect_objects():
    confidence = 0.6
    cap = cv2.VideoCapture(0)  # For Webcam
    cap.set(3, 640)
    cap.set(4, 480)
    
    model = YOLO("model/best.pt")

    classNames = ["fake", "real"]

    prev_frame_time = 0
    new_frame_time = 0

    while True:
        new_frame_time = time.time()
        success, img = cap.read()
        results = model(img, stream=True, verbose=False)
        for r in results.pred:
            boxes = r.xyxy[0]
            for box in boxes:
                # Bounding Box
                x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                # Confidence
                conf = math.ceil((box[4] * 100)) / 100
                # Class Name
                cls = int(box[5])
                if conf > confidence:
                    if classNames[cls] == 'real':
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)
                    cvzone.cornerRect(img, (x1, y1, w, h), 20, 1, color, 2)
                    cvzone.putTextRect(img, f'{classNames[cls].upper()} {int(conf*100)}%',
                                       (max(0, x1), max(35, y1)), scale=2, thickness=4, colorR=color, colorB=color)

        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        print(fps)

        ret, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()

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
        image = request.files['image'].read()
        conn = get_db_connection()
        cursor = conn.cursor()
        # 將姓名和圖片插入到資料庫
        sql = "INSERT INTO facevote (name, image) VALUES (%s, %s)"
        cursor.execute(sql, (name, image))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful', 'success') 
        return redirect(url_for('index'))
        
    return Response(detect_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')
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

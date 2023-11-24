import os
from base64 import b64decode
import hashlib
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
   
def compare_images(image1, image2):
    # 将图像转换为灰度图像
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # 计算图像的直方图
    hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])

    # 计算直方图的差异
    diff = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

    return diff

def save_image_to_database(name, image):
    # 将图像转换为字节流
    image_bytes = cv2.imencode('.jpg', image)[1].tobytes()

    # 连接到数据库
    conn = mysql.connector.connect(
        host="fyp.mysql.database.azure.com",
        user="ming",
        password="P@ssw0rd",
        database="fyp"
    )
    cursor = conn.cursor()

    # 插入图像数据到数据库
    sql = "INSERT INTO facevote (name, image) VALUES (%s, %s)"
    val = (name, image_bytes)
    cursor.execute(sql, val)

    # 提交事务
    conn.commit()

    # 关闭游标
    cursor.close()

    # 关闭数据库连接
    conn.close()

def get_images_from_database():
    # 连接到数据库
    conn = mysql.connector.connect(
        host="fyp.mysql.database.azure.com",
        user="ming",
        password="P@ssw0rd",
        database="fyp"
    )
    cursor = conn.cursor()

    # 从数据库中获取图像数据
    sql = "SELECT id, name, image FROM facevote"
    cursor.execute(sql)

    # 获取所有图像数据
    images = cursor.fetchall()

    # 关闭游标
    cursor.close()

    # 关闭数据库连接
    conn.close()

    return images

def capture_image_from_webcam():
    cap = cv2.VideoCapture(0)  # 打开摄像头
    ret, frame = cap.read()  # 读取摄像头帧

    if ret:
        cap.release()  # 释放摄像头
        return frame

    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 获取用户名
        name = request.form['name']
        if name:
            # 从摄像头捕获图像
            img = capture_image_from_webcam()

            if img is not None:
                # 保存图像到数据库
                save_image_to_database(name, img)

                # 比较图像
                authenticated = False
                db_images = get_images_from_database()
                for db_image in db_images:
                    # 将数据库中的图像数据转换为图像
                    db_img = cv2.imdecode(np.frombuffer(db_image[2], np.uint8), cv2.IMREAD_COLOR)

                    # 比较图像
                    similarity = compare_images(db_img, img)

                    if similarity > 0.8:  # 设置相似度阈值
                        authentic

            if authenticated:
                return "Login successful"
                return redirect(url_for('vote', success_message='Vote successful'))
            else:
                return "Login failed"
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

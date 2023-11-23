import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host='fyp.mysql.database.azure.com',
        user='ming',
        password='P@ssw0rd',
        database='fyp'
    )
    return conn

def update_vote(candidate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE facevote SET vote = %s", (candidate,))

    conn.commit()
    cursor.close()
    conn.close()

def detect_faces(image_data):
    image_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    return len(faces)

def login(request):
    if request.method == 'POST':
        name = request.form['name']
        image_data = request.form['image']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        num_faces = detect_faces(image_data)
        
        if num_faces == 1:
            sql_check = "SELECT * FROM facevote WHERE name = %s and vote = 0"
            cursor.execute(sql_check, (name,))
            result = cursor.fetchone()
            
            if result:
                session['name'] = name
                cursor.close()
                conn.close()
                return redirect(url_for('vote', success_message='Login successful'))
        
        return render_template('login.html', error='Invalid login')
    
    return render_template('login.html')

import threading
import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 500)

counter = 0

face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')

face_match = False


def check_face(frame):
    global face_match
    try:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            face_match = True
        else:
            face_match = False
    except ValueError:
        face_match = False


def start_face_detection():
    while True:
        ret, frame = cap.read()

        if ret:
            if counter % 30 == 0:
                try:
                    threading.Thread(target=check_face, args=(frame.copy(),)).start()
                except ValueError:
                    pass
            counter += 1


def is_face_matched():
    return face_match

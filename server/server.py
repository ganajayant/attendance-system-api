import datetime
import os
import pickle
import smtplib
import sqlite3
import threading
from os.path import dirname, join
import cv2
import face_recognition
import numpy as np
from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
CORS(app)


gmail_user = os.environ.get("EMAIL")
gmail_app_password = os.environ.get("PASSWORD")
send_from = os.environ.get("EMAIL")


def send_mailer(sender, body):
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.ehlo()
            server.login(gmail_user, gmail_app_password)
            subject = 'Attendance Alert'
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(send_from, sender, message)
        print('Email sent!')
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed! Please check your credentials.")
    except smtplib.SMTPException as e:
        print(f"Error: Failed to send email. {e}")


@app.post('/sendmaillees')
def sendmail():
    conn = get_db_connection()
    result = conn.execute(
        'SELECT DISTINCT s.student_id, a.date FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id').fetchall()

    unique_ids = set()
    unique_dates = set()

    for row in result:
        student_id = row['student_id']
        date = row['date']

        unique_ids.add(student_id)

        if date is not None:
            unique_dates.add(date)

    total_days = len(unique_dates)

    for student_id in unique_ids:
        result = conn.execute(
            'SELECT COUNT(*) AS count FROM attendance WHERE student_id = ?', (student_id,)
        ).fetchone()

        count = result['count']

        if count / total_days < 0.85:
            student = conn.execute(
                'SELECT * FROM students WHERE student_id = ?', (student_id,)
            ).fetchone()

            if student is not None:
                email = student['email']
                send_mailer(email, "Your attendance is less than 85%")

    conn.close()

    return {
        "message": "Mail sent successfully"
    }, 200


@app.post('/sendmailall')
def sendmail1():
    conn = get_db_connection()

    result = conn.execute(
        'SELECT DISTINCT s.student_id, a.date FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id').fetchall()

    unique_ids = set()
    unique_dates = set()

    for row in result:
        student_id = row['student_id']
        date = row['date']

        unique_ids.add(student_id)

        if date is not None:
            unique_dates.add(date)

    total_days = len(unique_dates)

    for student_id in unique_ids:
        result = conn.execute(
            'SELECT COUNT(*) AS count FROM attendance WHERE student_id = ?', (student_id,)
        ).fetchone()

        count = result['count']

        student = conn.execute(
            'SELECT * FROM students WHERE student_id = ?', (student_id,)
        ).fetchone()

        if student is not None:
            email = student['email']
            send_mailer(
                email, f"Your attendance is {count * 100 / total_days:.2f}%")

    conn.close()

    return {
        "message": "Mail sent successfully"
    }, 200


@app.route('/getdata', methods=['GET'])
def getdata():
    conn = get_db_connection()
    result = conn.execute(
        'SELECT s.student_id, a.date FROM students s LEFT JOIN attendance a ON s.student_id = a.student_id').fetchall()

    unique_ids = set()
    unique_dates = set()

    data = {}

    for row in result:
        student_id = row['student_id']
        date = row['date']

        unique_ids.add(student_id)
        if date is not None:
            unique_dates.add(date)

        if student_id not in data:
            data[student_id] = set()
        if date is not None:
            data[student_id].add(date)

    conn.commit()
    conn.close()

    exportdata = [
        {
            "id": student_id,
            "dates": [1 if date in data[student_id] else 0 for date in unique_dates]
        }
        for student_id in unique_ids
    ]

    return {
        "data": exportdata,
        "ids": list(unique_ids),
        "unique_dates": list(unique_dates)
    }, 200


@app.route('/attendance', methods=['POST'])
def success():
    if request.method == 'POST':
        try:
            f = request.files['file']
            f.save('uploads/upload.jpg')
            with open("recognizer/encode_id.p", "rb") as file:
                encodeListwithIds = pickle.load(file)
            encodeList, actualids = encodeListwithIds
            img = detect('uploads/upload.jpg')
            if img is None:
                return {
                    "message": "No face found"
                }, 404
            img = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            rimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            facesCurFrame = face_recognition.face_locations(rimg)
            encodesCurFrame = face_recognition.face_encodings(
                rimg, facesCurFrame)
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(
                    encodeList, encodeFace)
                faceDis = face_recognition.face_distance(
                    encodeList, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    id_ = actualids[matchIndex]
                    conn = get_db_connection()
                    result = conn.execute(
                        'SELECT * FROM students WHERE student_id = ?', (id_,)).fetchone()

                    if result is None:
                        return {
                            "message": "User not found"
                        }, 404

                    current_datetime = datetime.datetime.now()
                    sqlite_date_format = current_datetime.strftime('%Y-%m-%d')
                    student_id = result['student_id']

                    result = conn.execute(
                        'SELECT * FROM attendance WHERE student_id = ? AND date = ?', (
                            student_id, sqlite_date_format)
                    ).fetchone()

                    if result is not None:
                        return {
                            "message": "Student attendance is already marked for student ID: " + str(student_id)
                        }, 201

                    conn.execute('INSERT INTO attendance (student_id, date) VALUES (?, ?)',
                                 (student_id, sqlite_date_format))
                    conn.commit()
                    conn.close()

                    return {
                        "message": "Attendance marked successfully"
                    }, 200
                else:
                    return {
                        "message": "User not found"
                    }, 404

            return {
                "message": "User not found"
            }, 404
        except:
            return {
                "message": "Internal server error"
            }, 500
    else:
        return {
            "message": "Invalid request"
        }, 400


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        try:
            images = request.files.getlist('images')
            rollno = request.form.get('rollno')
            name = request.form.get('name')
            email = request.form.get('email')

            if images is None:
                return {
                    "message": "No images found"
                }, 400
            if len(images) > 10:
                return {
                    "message": "Maximum 10 images are allowed"
                }, 400
            if rollno is None or name is None or email is None:
                return {
                    "message": "Invalid data"
                }, 400
            conn = get_db_connection()
            result = conn.execute(
                'SELECT * FROM students WHERE student_id = ?', (rollno,)).fetchone()
            if result is not None:
                return {
                    "message": "User already exists"
                }, 400
            for i, image in enumerate(images):
                filename = f'uploads/upload{i}.jpg'
                image.save(filename)
                face = detect(filename)

                user_directory = 'images/' + rollno
                if not os.path.exists(user_directory):
                    os.makedirs(user_directory)

                if face is not None:
                    cv2.imwrite(os.path.join(user_directory,
                                f'{rollno}_{i}.jpg'), face)
            with conn:
                conn.execute('INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)',
                             (rollno, name, email))

            conn.close()
            train_thread = threading.Thread(target=train_model)
            train_thread.start()
            return {
                "message": "User added successfully & training started"
            }, 200
        except:
            return {
                "message": "Internal server error"
            }, 500
    else:
        return {
            "message": "Invalid request"
        }, 400


def detect(image='uploads/upload.jpg', cascade='cascades/haarcascade_frontalface_default.xml'):
    faceCascade = cv2.CascadeClassifier(cascade)
    with open(image, 'rb') as file:
        img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
    if len(faces) == 0:
        return None
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    x, y, w, h = largest_face
    return img[y:y+h, x:x+w]


def train_model():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students')
        result = cursor.fetchall()
        if result is None or len(result) == 0:
            return
        ids = os.listdir('images')
        encodedList = []
        actualids = []
        for id in ids:
            path = 'images/' + id
            images = os.listdir(path)
            for image in images:
                actualids.append(int(id))
                print(path + '/' + image)
                img = cv2.imread(path + '/' + image)
                rgb_small_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(rgb_small_frame)
                if len(encode) > 0:
                    encode = encode[0]
                encodedList.append(encode)
        encode_id = [encodedList, actualids]
        with open("recognizer/encode_id.p", "wb") as file:
            pickle.dump(encode_id, file)


def get_db_connection(dir='db/database.db'):
    conn = sqlite3.connect(dir)
    conn.row_factory = sqlite3.Row
    return conn


port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)

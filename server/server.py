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
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_app_password)
        subject = 'Attendance Alert'
        body = body
        server.sendmail(send_from, sender, body)
        server.close()
        print('Email sent!')
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


@app.post('/sendmaillees')
def sendmail():
    conn = get_db_connection()
    result = conn.execute('SELECT student_id FROM students').fetchall()
    unique_ids = []
    for row in result:
        if row['student_id'] not in unique_ids:
            unique_ids.append(row['student_id'])
    unique_dates = []
    result = conn.execute('SELECT date FROM attendance').fetchall()
    for row in result:
        if row['date'] not in unique_dates:
            unique_dates.append(row['date'])
    totaldays = len(unique_dates)
    for id in unique_ids:
        result = conn.execute(
            'SELECT * FROM attendance WHERE student_id = ?', (id,)).fetchall()
        count = len(result)
        if count/totaldays < 0.85:
            student = conn.execute(
                'SELECT * FROM students WHERE student_id = ?', (id,)).fetchone()
            if student is not None:
                email = student['email']
                send_mailer(email, "Your attendance is less than 85%")
    return {
        "message": "Mail sent successfully"
    }, 200


@app.post('/sendmailall')
def sendmail1():
    conn = get_db_connection()
    result = conn.execute('SELECT student_id FROM students').fetchall()
    unique_ids = []
    for row in result:
        if row['student_id'] not in unique_ids:
            unique_ids.append(row['student_id'])
    unique_dates = []
    result = conn.execute('SELECT date FROM attendance').fetchall()
    for row in result:
        if row['date'] not in unique_dates:
            unique_dates.append(row['date'])
    totaldays = len(unique_dates)
    for id in unique_ids:
        result = conn.execute(
            'SELECT * FROM attendance WHERE student_id = ?', (id,)).fetchall()
        count = len(result)
        student = conn.execute(
            'SELECT * FROM students WHERE student_id = ?', (id,)).fetchone()
        if student is not None:
            email = student['email']
            send_mailer(email, "Your attendance is " +
                        str(count*100/totaldays)+"%")
    return {
        "message": "Mail sent successfully"
    }, 200


@app.route('/getdata', methods=['GET'])
def getdata():
    conn = get_db_connection()
    result = conn.execute('SELECT student_id FROM students').fetchall()
    unique_ids = []
    for row in result:
        if row['student_id'] not in unique_ids:
            unique_ids.append(row['student_id'])
    unique_dates = []
    result = conn.execute('SELECT date FROM attendance').fetchall()
    for row in result:
        if row['date'] not in unique_dates:
            unique_dates.append(row['date'])
    data = []
    # for unique data store it as key and value is array of who are present on that day
    for unique_id in unique_ids:
        x = []
        result = conn.execute(
            'select date from attendance where student_id = ?', (unique_id,)).fetchall()
        for row in result:
            x.append(row['date'])
        data.append({
            "id": unique_id,
            "dates": x
        })
    conn.commit()
    conn.close()
    exportdata = []
    for item in data:
        id = item['id']
        dates = item['dates']
        x = []
        for date in unique_dates:
            if date in dates:
                x.append(1)
            else:
                x.append(0)
        exportdata.append({
            "id": id,
            "dates": x
        })
    return {
        "data": exportdata,
        "ids": unique_ids,
        "unique_dates": unique_dates
    }, 200


@app.route('/attendance', methods=['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        f.save('uploads/upload.jpg')
        file = open("recognizer/encode_id.p", "rb")
        encodeListwithIds = pickle.load(file)
        file.close()
        encodeList, actualids = encodeListwithIds
        img = detect()
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
                    'SELECT * FROM attendance WHERE student_id = ? AND date = ?', (student_id, sqlite_date_format)).fetchone()
                if result is not None:
                    return {
                        "message": "student attendance is marked" + str(student_id)
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
            for image, i in zip(images, range(10)):
                image.save('uploads/upload'+str(i)+'.jpg')
                face = detect('uploads/upload'+str(i)+'.jpg')
                user_directory = 'images/'+rollno
                if not os.path.exists(user_directory):
                    os.makedirs(user_directory)
                if face is not None:
                    cv2.imwrite(os.path.join(
                        user_directory, rollno + "_" + str(i) + '.jpg'), face)

            conn.execute('INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)',
                         (rollno, name, email))
            conn.commit()
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
    img = cv2.imread(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3)
    if faces is None or len(faces) == 0:
        return None
    max_area = faces[0][2] * faces[0][3]
    face = faces[0]
    for f in faces:
        if f[2] * f[3] > max_area:
            max_area = f[2] * f[3]
            face = f
    x, y, w, h = face
    return img[y:y+h, x:x+w]


def train_model():
    conn = get_db_connection()
    result = conn.execute('SELECT * FROM students').fetchall()
    conn.commit()
    conn.close()
    if result is None or len(result) == 0:
        return
    ids = os.listdir('images')
    encodedList = []
    actualids = []
    for id in ids:
        path = 'images/'+id
        images = os.listdir(path)
        for image in images:
            actualids.append(int(id))
            print(path+'/'+image)
            img = cv2.imread(path+'/'+image)
            rgb_small_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(rgb_small_frame)
            if len(encode) > 0:
                encode = encode[0]
            encodedList.append(encode)

    encode_id = [encodedList, actualids]
    file = open("recognizer/encode_id.p", "wb")
    pickle.dump(encode_id, file)
    file.close()


def get_db_connection():
    conn = sqlite3.connect('db/database.db')
    conn.row_factory = sqlite3.Row
    return conn


port = int(os.environ.get('PORT', 5000))
app.run(debug=True, host='0.0.0.0', port=port)

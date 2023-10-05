# Attendance System API

This is a Flask-based API for an attendance system. It allows users to upload images, detect faces, mark attendance, and train the face recognition model.

## Requirements

* Python 3.7 or higher
* OpenCV (cv2) library (opencv-contrib-python)
* Flask library
* NumPy library
* SQLite3 library

## Installation
1. Clone the repository:
```git clone https://github.com/ganajayant/attendance-system-api.git```

2. Navigate to the project directory:
```cd attendance-system-api/server```

3. Install the required dependencies:
```pip install -r requirements.txt```

4. Load Schema into Database
```python init_db.py```


## Run Command
To start the Flask application, use the following command:
* MacOS
```flask --app server run --debug```
* Windows
```python -m flask --app server run --debug```


To start the React application, use the following command:

```npm install && npm start```


## API Endpoints

[Postman Documentation](https://documenter.getpostman.com/view/26671764/2s9YJdX3Cb)

### Upload Images and Add User

Endpoint: /upload

Method: POST

Request Body:

* images (multipart/form-data) - List of images to upload (maximum 10 images).
* rollno (form-data) - Roll number of the student.
* name (form-data) - Name of the student.
* email (form-data) - Email of the student.

Response:
* Success (200 OK):
```
{
    "message": "User added successfully & training started"
}
```
* Bad Request (400):
    * If no images are found:
    ```
    {
        "message": "No images found"
    }
    ```
    * If more than 10 images are uploaded:
    ```
    {
        "message": "Maximum 10 images are allowed"
    }
    ```
    * If the request data is invalid:
    ```
    {
        "message": "Invalid data"
    }
    ```
    * If the user already exists:
    ```
    {
        "message": "User already exists"
    }
    ```
* Internal Server Error (500):
    ```
    {
        "message": "Internal server error"
    }
    ```
### Mark Attendance

Endpoint: /attendance

Method: POST

Request Body:

* file (multipart/form-data) - Image file for attendance marking.

Response:
* Success (200 OK):
```
{
    "message": "Attendance marked successfully"
}
```
* Not Found (404):
    * If no face is found in the uploaded image:
    ```
    {
        "message": "No face found"
    }
    ```
    * If the user is not found in the face recognition model:
    ```
    {
        "message": "User not found"
    }
    ```
    * If the student attendance is already marked for the current date:
    ```
    {
        "message": "Student attendance is marked"
    }
    ```
* Internal Server Error (500):
    ```
    {
        "message": "Internal server error"
    }
    ```


Please note that the API assumes the existence of the following directories:

uploads - for temporary image uploads

images - for storing user images

recognizer - for storing the trained face recognition model

Also, make sure to create an SQLite database file database.db in the db directory before running the application.
# Attendance System API

This is a Flask-based API for an attendance system. It allows users to upload images, detect faces, mark attendance, and train the face recognition model.

## Requirements
Given in ```requirements.txt```

## Installation
1. Clone the repository:
```git clone https://github.com/ganajayant/attendance-system-api.git```

2. Navigate to the project directory:
```cd attendance-system-api/server```

3. Build the Docker Image:
```docker build -t "attendance-api" .```

4. Run The Docker Container
```docker run --name server -p 5000:5000 -d attendance-api```


To start the React application, use the following command:

```npm install && npm start```


## API Endpoints

[Postman Documentation](https://documenter.getpostman.com/view/26671764/2s9YJdX3Cb)

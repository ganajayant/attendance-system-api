# Attendance System API

This is a Flask-based API for an attendance system. It allows users to upload images, detect faces, mark attendance, and train the face recognition model.

## Setup
1. Clone the repository:
```git clone https://github.com/ganajayant/attendance-system-api.git```

### Server
1. Navigate to the project directory:
```cd attendance-system-api/server```

2. Build the Docker Image:
```docker build -t "attendance-api" .```

3. Run The Docker Container
```docker-compose up -d```

4. To stop the Docker container
```docker-compose down```


### Client
1. Navigate to the project directory:
```cd attendance-system-api/client```

2. Install Dependencies:
```npm install```

3. Start Application
```npm start```

## API Endpoints

[Postman Documentation](https://documenter.getpostman.com/view/26671764/2s9YJdX3Cb)

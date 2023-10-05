FROM python:3.10

ENV PYTHONUNBUFFERED True

WORKDIR /app

COPY . .

RUN apt-get update --fix-missing && apt-get install -y libpq-dev build-essential libgl1-mesa-glx
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir uploads
RUN mkdir images
RUN python init_db.py

EXPOSE 5000
CMD [ "python", "server.py"]

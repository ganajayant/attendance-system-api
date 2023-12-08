FROM --platform=linux/amd64 python:3.10

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000
CMD [ "python", "server.py"]

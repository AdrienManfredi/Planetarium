FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

CMD ["./wait-for-it.sh", "kafka:9092", "--", "python3", "app.py"]

# CMD ["python", "app.py"]
# CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
# ENTRYPOINT FLASK_APP=./app.py flask run --host=0.0.0.0
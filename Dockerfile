FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV API_KEY='VENRbDgPZZ9h48RKhf7JQg==GHyAUNRAuMQo6hz7'

CMD ["python", "app.py"]
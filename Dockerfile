FROM python:3.11-alpine

RUN pip install --no-cache-dir --upgrade pip==22.3

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY ./data.jsonl /app/data.jsonl
COPY ./main.py /app/main.py

ENTRYPOINT ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /export

ENV EHRSUCTION_OUTPUT_FOLDER=/export/

CMD ["python3", "ehrsuction.py"]
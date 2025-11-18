FROM python:3.10-slim

WORKDIR /app

COPY /app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy entire project folder
COPY ./app /app

WORKDIR /app/worker

CMD ["python", "consumer.py"]
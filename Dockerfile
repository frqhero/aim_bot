#!/bin/bash
FROM python:3.10.4

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY main.py .

CMD ["python3", "main.py"]
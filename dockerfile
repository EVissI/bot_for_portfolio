# Используем официальный образ Python
FROM python:3.12
WORKDIR /portfolio

COPY requirements.txt /portfolio
RUN pip install --no-cache-dir -r requirements.txt

COPY . /portfolio




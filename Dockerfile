FROM python:3.11-slim

RUN pip install scurrypy

WORKDIR /app
COPY main.py .

CMD ["python", "main.py"]

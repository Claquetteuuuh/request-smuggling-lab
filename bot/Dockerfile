FROM python:3.9-slim
RUN pip install requests
WORKDIR /app
COPY app.py .
CMD ["python", "-u", "app.py"]

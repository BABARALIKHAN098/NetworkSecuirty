FROM python:3.12-slim

WORKDIR /app

# Install dependencies first so Docker can cache this layer
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the app
COPY ./app .

CMD ["python", "app.py"]
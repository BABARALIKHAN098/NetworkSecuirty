FROM Python:3.12-slim-buster
WORKDIR /app
COPY ./app .
RUN apt update -y && apt install -y build-awscli
RUN apt-get update && pip install -r requirements.txt
CMD ["python", "app.py"]
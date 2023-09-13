from python:3.10.13-alpine3.18

WORKDIR /app
COPY . /app

RUN set -o allexport && source .env && set +o allexport
RUN rm .env

RUN pip install -r requirements.txt
CMD ["python", "main.py"]
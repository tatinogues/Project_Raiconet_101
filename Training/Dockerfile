FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
    && apt-get -y install curl \
    && apt-get install libgomp1 libquadmath0

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./train.py .
COPY ./inference.py .
COPY ./credentials.py .
COPY ./training-code.py .
COPY ./inference-code.py .

#CMD ["python", "script.py"]
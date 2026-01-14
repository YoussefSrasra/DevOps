FROM alpine:latest

RUN apk update \
    && apk add python3 py3-pip

COPY ./ /app/

WORKDIR /app/

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install -r requirements.txt

EXPOSE 5000

CMD ["python3", "./app.py"]

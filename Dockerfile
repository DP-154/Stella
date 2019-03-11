FROM python:3.7.2-slim

WORKDIR /stella

COPY . /stella

RUN apt-get update \
    && pip3 install pip --upgrade \
    && pip3 install -r requirements.txt

EXPOSE 8000

CMD ["python3.7", "manage.py", "run", "bot"]

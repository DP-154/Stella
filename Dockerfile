FROM python:3.7.2-stretch

WORKDIR /stella

COPY . /stella

RUN apt-get update \
    # && apt-get install postgresql-dev \
    && pip3 install pip --upgrade \
    && pip3 install -r requirements.txt

EXPOSE 8000

CMD python3.7 manage.py create && python3.7 manage.py run bot

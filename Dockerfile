FROM python:3.7.2

WORKDIR /stella

COPY . /stella

RUN apt-get update \
    && pip3 install pip --upgrade \
    && pip3 install -r requirements.txt

EXPOSE 5000

CMD python3.7 manage.py run all --check

FROM python:3.7.2-alpine

WORKDIR /stella
COPY . /stella

RUN apt-get -y update
RUN apt-get -y install python-opencv
RUN apt-get -y install tesseract-ocr

RUN pip3 install --upgrade pip
RUN pip3 install pipenv
RUN pipenv install --dev
RUN pipenv run pip freeze > requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3.7", "manage.py", "--runbot"]

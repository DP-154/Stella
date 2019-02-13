FROM python:3.7.2

WORKDIR /stella

COPY . /stella

RUN pip install pipenv && \
    pipenv install --system --dev

EXPOSE 8000

CMD ["python3.7", "manage.py"]
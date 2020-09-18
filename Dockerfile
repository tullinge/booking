FROM tiangolo/uwsgi-nginx-flask:python3.8

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pipenv install --system

COPY . /app
WORKDIR /app

FROM tiangolo/meinheld-gunicorn-flask:python3.7

# Installing netcat for usage in start script
RUN apt-get update && apt-get install -y netcat

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
RUN chmod u+x ./entrypoint.sh

ENTRYPOINT [ "./entrypoint.sh" ]

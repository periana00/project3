FROM python:3.8-slim


COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt 

ENV FLASK_APP=flask_app

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]
FROM python:3.12

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY app.py /app

CMD [ "python", "/app/app.py" ]

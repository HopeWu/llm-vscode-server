FROM python:3.8
WORKDIR /app
ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# CMD gunicorn --workers=2 main:app -b 127.0.0.1:5000
CMD python main.py
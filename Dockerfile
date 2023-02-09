FROM python:3.8

WORKDIR /opt/valentines_day_bot

ADD ./requirements.txt .
RUN pip install -r requirements.txt

ADD . .

CMD PYTHONPATH=${PWD} python3 -u src/main.py
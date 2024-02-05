FROM python:3.12-alpine AS server

COPY ./requirements.txt ./requirements.txt
COPY src/ .

RUN pip install -r requirements.txt

EXPOSE 64000

RUN ls cvs

ENTRYPOINT [ "waitress-serve", "--port", "64000", "server:app" ]
FROM python:3.5-alpine

WORKDIR /app
ADD require.txt /app/require.txt
RUN pip install -r require.txt
ADD . /app
CMD python /app/server.py

FROM amancevice/pandas:0.21.0-python3-alpine

WORKDIR /app
ADD require.txt /app/require.txt
RUN pip3 install -r require.txt

ADD . /app
CMD python3 /app/server.py

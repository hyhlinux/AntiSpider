FROM python:3.5-alpine

WORKDIR /app
ADD require.txt /app/require.txt
RUN apk add --update curl gcc g++ \
    && rm -rf /var/cache/apk/* \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install -r require.txt

ADD . /app
CMD python /app/server.py

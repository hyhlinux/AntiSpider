import os

elasticsearch_conf =\
{
    "host": [
        'http://172.16.1.53:9200/',
        'http://172.16.1.54:9200/',
    ],
    "index": "nginx-access-log-*"
}

web_port = 8000
# file_path = '/tmp/'
file_path = os.path.join(os.path.dirname(__file__), 'html')
file_name = 'anti_spider.csv'
file_log = os.path.join(file_path, 'antispider.log')
file_name_path = os.path.join(file_path, file_name)

anti_spider = {
    "total": 1000,
    "rate": "100.00%",
}
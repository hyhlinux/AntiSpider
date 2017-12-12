import os
from handlers import AutoHandler, IpHandler
from tornado.web import StaticFileHandler

ip_api_urls = [
    (r'^/api/ip?', IpHandler),
    (r'^/api/auto', AutoHandler),
]

urls = []
urls.extend(ip_api_urls)
static_path_dir = os.path.join(os.path.dirname(__file__), 'html')
urls.extend([(r'/static/(.*)', StaticFileHandler, {'path': static_path_dir})])
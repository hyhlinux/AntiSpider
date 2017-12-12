import os
from handlers.BaseHandler import *
from handlers import Auto, Ip
from tornado.web import StaticFileHandler

ip_api_urls = [
    # (r'^/api/ips?', VerifyCode.ImageCodeHandler),
    (r'^/api/ip?', Ip.IpHandler),
    (r'^/api/auto', Auto.AutoHandler),
    # (r'^/api/aioip', Ip.AioIpHandler),
    # (r'^/api/aioipauto', Ip.AioAutoIpsHandler),
    # (r'^/api/aioauto', Auto.AioAutoHandler),
]

urls = []
urls.extend(ip_api_urls)
static_path_dir = os.path.join(os.path.dirname(__file__), 'html')
urls.extend([(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path_dir})])
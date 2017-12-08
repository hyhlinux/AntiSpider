from handlers.BaseHandler import *
from handlers import Auto, Ip

ip_api_urls = [
    # (r'^/api/ips?', VerifyCode.ImageCodeHandler),
    (r'^/api/ip?', Ip.IpHandler),
    (r'^/api/auto', Auto.AutoHandler),
]

urls = []
urls.extend(ip_api_urls)

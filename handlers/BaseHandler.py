import json
import tornado.web
from tornado.web import RequestHandler
from utils import get_log

logger = get_log(name='handler')


class BaseHandler(RequestHandler):
    """请求处理基类"""

    @property
    def es(self):
        return self.application.es

    @property
    def loop(self):
        return self.application.loop

    @property
    def logger(self):
        return logger

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None

    def set_default_headers(self):
        self.set_header("Content-Type", "application/json; charset=UTF-8")


class StaticFileHandler(tornado.web.StaticFileHandler):
    def __init__(self, *args, **kwargs):
        super(StaticFileHandler, self).__init__(*args, **kwargs)

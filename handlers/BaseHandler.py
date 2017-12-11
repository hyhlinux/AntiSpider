import tornado.ioloop
import json
import tornado.web
from tornado.web import RequestHandler
from .log import get_log

logger = get_log()


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

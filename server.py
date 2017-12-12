import tornado.web
import asyncio
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options, define
from urls import urls
from utils.esapi import ES

define("port", default=8000, help="run on the given port", type=int)


class Application(tornado.web.Application):

    def __init__(self):
        self.es = ES()
        self.loop = asyncio.get_event_loop()
        super(Application, self).__init__(urls)


def main():
    tornado.options.parse_command_line()
    app = Application()
    print("ser port: ", options.port)
    print("cvs: /tmp/anti_spider.cvs")
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()

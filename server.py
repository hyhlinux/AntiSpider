import tornado.web
import asyncio
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options, define
from urls import urls
from utils.esapi import ES

define("port", default=8000, help="run on the given port", type=int)
define("file_name", default="/tmp/anti_spider.cvs", help="run on the given port", type=int)


class Application(tornado.web.Application):

    def __init__(self):
        self.es = ES()
        self.loop = asyncio.get_event_loop()
        self.file_name = options.file_name
        super(Application, self).__init__(urls)


def main():
    tornado.options.parse_command_line()
    app = Application()
    print("ser port: ", options.port, 'cvs:', options.file_name)
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()

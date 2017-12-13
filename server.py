import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.options
from tornado.options import options, define
from urls import urls
from utils import get_log
from utils.esapi import ES
from config import web_port, file_name_path, elasticsearch_conf

define("port", default=web_port, help="run on the given port", type=int)
define("file_name", default=file_name_path, help="tmp data file name", type=str)
logger = get_log('ser')


class Application(tornado.web.Application):

    def __init__(self):
        self.es = ES(hosts=elasticsearch_conf.get('host'), index=elasticsearch_conf.get('index'))
        self.file_name = options.file_name
        super(Application, self).__init__(urls)


def main():
    tornado.options.parse_command_line()
    app = Application()
    logger.info("port:{port}  csv:{csv}".format(port=options.port, csv=options.file_name))
    app.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()

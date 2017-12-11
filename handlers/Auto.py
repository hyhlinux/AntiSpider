import json
import asyncio
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from .BaseHandler import BaseHandler


class AutoHandler(BaseHandler):
    """
    启动获取top20_ip 进行分析访问的域名比例

    """

    def get(self):
        data_list = {}
        top_ip_list = self.es.get_top_ip()
        for ip in top_ip_list:
            data = self.es.get_ip_rate(ip.get('key', ""))
            ip_key = ip.get('key', "")
            ip_cnt = ip.get('doc_count', 0)
            self.logger.info("{:<15}\t\t:{cnt}:\t\t{data}".format(
                ip_key, cnt=ip_cnt, data=data))
            data_list[ip_key] = data
        self.write(json.dumps(data_list))


class AioAutoHandler(BaseHandler):
    """
    启动获取top20_ip 进行分析访问的域名比例

    """

    def get(self):
        # top_ip = self.loop.run_until_complete(self.es.async_get_top_ip())
        # responses = yield {ip: self.loop.run_until_complete(self.es.async_get_ip_rate(ip)) for ip in top_ip}
        # print('response:', responses)
        # self.write(json.dumps(responses))
        data = self.loop.run_until_complete(self.aio_ip_rete())
        self.write(json.dumps(data))

    @asyncio.coroutine
    def aio_ip_rete(self):
        top_ip = yield from self.es.async_get_top_ip()
        data = {}
        for item in top_ip:
            ip = item.get('key', '')
            data[ip] = yield from self.es.async_get_ip_rate(ip)
        if not data:
            data = {}

        return data

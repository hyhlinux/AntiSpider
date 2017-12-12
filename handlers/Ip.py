import json
import asyncio
from tornado import gen
from .BaseHandler import BaseHandler


class IpHandler(BaseHandler):
    """
    启动获取top20_ip 进行分析访问的域名比例

    """

    def get(self):
        ips = self.get_arguments('ips')
        self.logger.info("ips:{}".format(ips))
        if not ips or len(ips) == 0:
            self.redirect('/api/auto')
            return

        data_list = {
        }

        # 字符串，非空即可
        only_ip = self.get_argument('only_ip')
        if only_ip:
            top_ip = self.es.get_top_ip()
            self.write(json.dumps(dict(ips=top_ip)))
            return

        try:
            for ip in ips:
                data = self.es.get_ip_rate(ip)
                data_list[ip] = data
            self.write(json.dumps(data_list))
        except Exception as e:
            self.write(json.dumps({"err": "{}".format(e)}))
            self.logger.error("{}".format(e))

    def post(self):
        ips = self.get_body_arguments('ips')
        self.logger.debug("ips:{}".format(ips))
        if not ips:
            self.redirect('/api/auto')
            return
        data_list = {
        }
        try:
            for ip in ips:
                data = self.es.get_ip_rate(ip)
                data_list[ip] = data
            self.write(json.dumps(data_list))
        except Exception as e:
            self.write(json.dumps({"err": "{}".format(e)}))
            self.logger.error("{}".format(e))


class AioIpHandler(BaseHandler):
    """
    启动获取top20_ip

    """

    def get(self):
        only_ip = self.get_argument('only_ip')
        if only_ip:
            top_ip = self.loop.run_until_complete(
                self.es.async_get_top_ip())
            self.write(json.dumps(dict(ips=top_ip)))
            return

        ips = self.get_arguments('ips')
        data = {}
        for ip in ips:
            data[ip] = self.loop.run_until_complete(self.es.async_get_ip_rate(ip))
        if not data:
            data = {}

        self.write(json.dumps(data))
        return


class AioAutoIpsHandler(BaseHandler):
    """
    启动获取top20_ip

    """

    @gen.coroutine
    def get(self):
        top_ip = yield from self.es.async_get_top_ip()
        responses = yield from {ip.get('key', ''): self.es.async_get_ip_rate(ip.get('key', '')) for ip in top_ip}
        print(responses)
        # data = {}
        # for item in top_ip:
        #     ip = item.get('key', '')
        #     data[ip] = yield from self.loop.run_until_complete(self.es.async_get_ip_rate(ip))
        # if not data:
        #     data = {}
        # data = self.loop.run_until_complete(self.aio_ip_rete())
        self.write(json.dumps(responses))
        return

    @gen.coroutine
    def parallel_fetch_dict(self, top_ip=None):
        responses = yield {ip.get('key', ''): self.es.async_get_ip_rate(ip.get('key', '')) for ip in top_ip}
        print(responses)

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


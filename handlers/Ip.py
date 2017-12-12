import json
from .BaseHandler import BaseHandler


class IpHandler(BaseHandler):
    """
    启动获取top20_ip 进行分析访问的域名比例

    """

    def get(self):
        try:
            only_ip = self.get_argument('only_ip', default='true')
            if only_ip == "true":
                top_ip = self.es.get_top_ip()
                self.write(json.dumps(dict(ips=top_ip)))
                return
        except Exception as e:
            self.logger.warning("{} onlyip:{}".format(e, only_ip))

        ips = self.get_arguments('ips')
        self.logger.info("ips:{}".format(ips))
        if not ips or len(ips) == 0:
            self.redirect('/api/auto')
            return

        data_list = {}
        try:
            # todo async
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


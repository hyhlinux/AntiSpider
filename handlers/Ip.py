import json
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

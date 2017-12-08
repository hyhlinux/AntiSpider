import json
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
			self.logger.info("{:<15}\t\t:{cnt}:\t\t{data}".format(ip_key, cnt=ip_cnt, data=data))
			data_list[ip_key] = data
		self.write(json.dumps(data_list))
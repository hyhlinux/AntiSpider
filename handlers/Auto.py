import json
import datetime
import os
import asyncio
import pandas as pd
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from .BaseHandler import BaseHandler
# from urls import static_path_dir


class AutoHandler(BaseHandler):
    """
    启动获取top20_ip 进行分析访问的域名比例

    """

    def get(self):
        top_ip_list = self.es.get_top_ip()
        df = pd.DataFrame(columns=['ip', 'total', 'download.pureapk.com', 'apkpure.com'])
        df.index_lable = 'index'
        for index, ip in enumerate(top_ip_list):
            data = self.es.get_ip_rate(ip.get('key', ""))
            ip_key = ip.get('key', "")
            ip_cnt = ip.get('doc_count', 0)
            df.loc[index] = [ip_key, ip_cnt, data.get('download.pureapk.com', '0.00%'), data.get('apkpure.com', '0.00%')]

        # 数据直接输出到日志中
        self.logger.info("df:\n{}".format(df))
        df = df.sort_values(['total', 'download.pureapk.com'], ascending=False)
        df_spider = df[df['download.pureapk.com'] == '100.00%']
        df_spider = df_spider[df_spider['total'] > 1000]
        self.logger.info("df_spider:\n{}".format(df_spider))
        file_name = "/tmp/anti_spider.cvs"
        df.to_csv(file_name, sep=',', encoding='utf-8', index=False, index_label='index')
        self.write(json.dumps(df_spider.T.to_dict()))


# class AioAutoHandler(BaseHandler):
#     """
#     启动获取top20_ip 进行分析访问的域名比例
#
#     """
#
#     def get(self):
#         data = self.loop.run_until_complete(self.aio_ip_rete())
#         self.write(json.dumps(data))
#
#     @asyncio.coroutine
#     def aio_ip_rete(self):
#         top_ip = yield from self.es.async_get_top_ip()
#         data = {}
#         for item in top_ip:
#             ip = item.get('key', '')
#             data[ip] = yield from self.es.async_get_ip_rate(ip)
#         if not data:
#             data = {}
#
#         return data

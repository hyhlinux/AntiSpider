import json
import asyncio
import types
import pandas as pd
from tornado import gen
from .BaseHandler import BaseHandler
from config import file_name_path, anti_spider


class AioAutoHandler(BaseHandler):
    """
    启动获取topN_ip 进行分析访问的域名比例

    """
    def get(self):
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(self.get_ip_rate())
        self.write(data)

    async def get_ip_rate(self):
        # total ip总数
        total = int(self.get_argument('total', default=1000))
        try:
            top_ip_list = self.es.get_top_ip(size=total)
        except Exception as e:
            self.logger.error("{}".format(e))
            self.write(json.dumps({"err": "{}".format(e)}))
            return
        if total < 0:
            total = 100
        elif total > 5000:
            total = 5000

        # size: 一次处理ip
        size = int(self.get_argument('size', default=100))
        if size < 0:
            size = 100
        elif size > 100:
            size = 100

        # from
        size_from = int(self.get_argument('from', default=1))
        if size_from < 0:
            size_from = 1
        elif size_from > total:
            size_from = total

        start = size_from - 1
        if start < 0:
            start = 0
        end = start + size
        if end > len(top_ip_list):
            end = len(top_ip_list)
        top_ip_list = top_ip_list[start:end]
        self.logger.info("top_ip_list:{}".format(len(top_ip_list)))
        df = pd.DataFrame(columns=['ip', 'total', 'download.pureapk.com', 'apkpure.com'])
        ip_tasks = [self.es.async_get_ip_rate(ip.get('key', '')) for ip in top_ip_list]
        completed, pending = await asyncio.wait(ip_tasks)
        for index, t in enumerate(completed):
            data = t.result()
            self.logger.info("index:{} data:{}".format(index, data))
            ip_key = data.get('ip', '')
            ip_cnt = data.get('total', 0)
            df.loc[start+index] = [ip_key, ip_cnt, data.get('download.pureapk.com', '0.00%'), data.get('apkpure.com', '0.00%')]

        if pending:
            self.logger.warning('pending:{}'.format(pending))
            for t in pending:
                t.cancel()
        # from
        src = self.get_argument('src', default="")
        self.logger.info("total:{} start:{} end:{} src:{}".format(total, start, end, src))
        try:
            df = df.sort_values(['total', 'download.pureapk.com'], ascending=False)
            self.logger.info("src-df:\n{}".format(df))
            # 是否返回元数据
            if src == "true":
                return json.dumps(df.T.to_dict())

            df_spider = df[df['download.pureapk.com'] == anti_spider.get('rate', '100.00%')]
            df_spider = df_spider[df_spider['total'] > anti_spider.get('total', 1000)]
            self.logger.info("df_spider:\n{}".format(df_spider))
            return json.dumps(df_spider.T.to_dict())
        except Exception as e:
            self.logger.error("{}".format(e))
            return json.dumps({"err": "{}".format(e)})
        finally:
            df.to_csv(file_name_path, sep=',', encoding='utf-8', index=False, index_label='index')

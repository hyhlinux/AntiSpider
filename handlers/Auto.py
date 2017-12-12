import json
import types
import pandas as pd
from .BaseHandler import BaseHandler
from config import file_name_path, anti_spider


class AutoHandler(BaseHandler):
    """
    启动获取top20_ip 进行分析访问的域名比例

    """

    def get(self):
        try:
            size = int(self.get_argument('size', default=10))
        except Exception as e:
            self.logger.warning("size:{} type:{} err:{}".format(size, type(size), e))
            size = 10
        self.logger.info("size:{} ".format(size))
        if size < 0:
            size = 10
        elif size > 100:
            size = 100

        try:
            top_ip_list = self.es.get_top_ip(size=size)
        except Exception as e:
            self.logger.error("{}".format(e))
            self.write(json.dumps({"err": "{}".format(e)}))
            return

        df = pd.DataFrame(columns=['ip', 'total', 'download.pureapk.com', 'apkpure.com'])
        for index, ip in enumerate(top_ip_list):
            data = self.es.get_ip_rate(ip.get('key', ""))
            ip_key = ip.get('key', "")
            ip_cnt = ip.get('doc_count', 0)
            df.loc[index] = [ip_key, ip_cnt, data.get('download.pureapk.com', '0.00%'), data.get('apkpure.com', '0.00%')]

        self.logger.info("src-df:\n{}".format(df))
        try:
            df = df.sort_values(['total', 'download.pureapk.com'], ascending=False)
            df_spider = df[df['download.pureapk.com'] == anti_spider.get('rate', '100.00%')]
            df_spider = df_spider[df_spider['total'] > anti_spider.get('total', 1000)]
            self.logger.info("df_spider:\n{}".format(df_spider))
            df.to_csv(file_name_path, sep=',', encoding='utf-8', index=False, index_label='index')
            self.write(json.dumps(df_spider.T.to_dict()))
        except Exception as e:
            self.logger.error("{}".format(e))
            self.write(json.dumps({"err": "{}".format(e)}))
            return

import json
import types
import pandas as pd
from .BaseHandler import BaseHandler
from config import file_name_path, anti_spider


class AutoHandler(BaseHandler):
    """
    启动获取topN_ip 进行分析访问的域名比例

    """

    def get(self):
        # total ip总数
        try:
            total = int(self.get_argument('total', default=1000))
        except Exception as e:
            self.logger.warning("total:{} type:{} err:{}".format(total, type(total), e))
            total = 1000

        try:
            top_ip_list = self.es.get_top_ip(size=total)
        except Exception as e:
            self.logger.error("{}".format(e))
            self.write(json.dumps({"err": "{}".format(e)}))
            return

        # size: 一次处理ip
        try:
            size = int(self.get_argument('size', default=100))
        except Exception as e:
            self.logger.warning("size:{} size:{} err:{}".format(size, type(size), e))
            size = 1000

        if size < 0:
            size = 100
        elif size > 100:
            size = 100

        # from
        try:
            size_from = int(self.get_argument('from', default=1))
        except Exception as e:
            self.logger.warning("size_from:{} type:{} err:{}".format(size_from, type(size_from), e))
            size_from = 1
        start = size_from - 1
        if start < 0:
            start = 0
        end = start + size
        if end > len(top_ip_list):
            end = len(top_ip_list)
        top_ip_list = top_ip_list[start:end]
        df = pd.DataFrame(columns=['ip', 'total', 'download.pureapk.com', 'apkpure.com'])
        for index, ip in enumerate(top_ip_list):
            data = self.es.get_ip_rate(ip.get('key', ""))
            ip_key = ip.get('key', "")
            ip_cnt = ip.get('doc_count', 0)
            df.loc[start+index] = [ip_key, ip_cnt, data.get('download.pureapk.com', '0.00%'), data.get('apkpure.com', '0.00%')]

        # from
        try:
            src = self.get_argument('src', default="")
        except Exception as e:
            self.logger.warning("src:{} type:{} err:{}".format(src, type(src), e))
            src = ""

        self.logger.info("total:{} start:{} end:{} src:{}".format(total, start, end, src))
        try:
            df = df.sort_values(['total', 'download.pureapk.com'], ascending=False)
            self.logger.info("src-df:\n{}".format(df))
            # 是否返回元数据
            if src == "true":
                self.write(json.dumps(df.T.to_dict()))
                return
            df_spider = df[df['download.pureapk.com'] == anti_spider.get('rate', '100.00%')]
            df_spider = df_spider[df_spider['total'] > anti_spider.get('total', 1000)]
            self.logger.info("df_spider:\n{}".format(df_spider))
            self.write(json.dumps(df_spider.T.to_dict()))
        except Exception as e:
            self.logger.error("{}".format(e))
            self.write(json.dumps({"err": "{}".format(e)}))
            return
        finally:
            df.to_csv(file_name_path, sep=',', encoding='utf-8', index=False, index_label='index')

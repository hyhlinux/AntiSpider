import datetime
import asyncio
import elasticsearch
from aioes import Elasticsearch as AsyncElasticsearch
from .log import get_log

logger = get_log()

hosts = [
    'http://172.16.1.53:9200/',
    'http://172.16.1.54:9200/',
]

logger = get_log()


class ES(object):

    def __init__(self, index="nginx-access-log-*"):
        self.index = index
        self.es = self.connect_host()
        self.aioes = self.aio_connect_host()

    def aio_connect_host(cls, hosts=hosts):
        aioes = AsyncElasticsearch(
            hosts,
            sniffer_timeout=600
        )
        return aioes

    def connect_host(cls, hosts=hosts):
        es = elasticsearch.Elasticsearch(
            hosts,
            # sniff_on_start=True,
            # sniff_on_connection_fail=True,
            sniffer_timeout=600
        )
        return es

    def get_top_ip(self, size=100):
        now = datetime.datetime.now()
        time_gte = now - datetime.timedelta(days=1)
        body = {
            "query": {
                "bool": {
                    "must": [{
                        "match_all": {}
                    }, {
                        "match_phrase": {
                            "domain": {
                                "query": "download.pureapk.com"
                            }
                        }
                    }, {
                        "range": {
                            "@timestamp": {
                                "gte": int(time_gte.timestamp()*1000),
                                "lte": int(now.timestamp()*1000),
                                "format": "epoch_millis"
                            }
                        }
                    }],
                    "must_not": []
                }
            },
            "size": 0,
            "_source": {
                "excludes": []
            },
        }
        aggs = {
            "topip": {
                "terms": {
                    "field": "remote_ip.keyword",
                    "size": size,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        }

        body["aggs"] = aggs
        logger.info("body:{}".format(body))
        res = self.es.search(index=self.index, body=body)
        top_ip_list = res.get('aggregations', {}).get(
            'topip', {}).get('buckets', [])
        if len(top_ip_list) == 0:
            return None
        logger.info("top{}_ip".format(len(top_ip_list)))
        return top_ip_list

    def get_ip_rate(self, ip=""):
        if not ip:
            return None
        now = datetime.datetime.now()
        time_gte = now - datetime.timedelta(days=1)
        body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "range": {
                                "@timestamp": {
                                    "gte": int(time_gte.timestamp() * 1000),
                                    "lte": int(now.timestamp() * 1000),
                                    "format": "epoch_millis"
                                }
                            }
                        },
                        {
                            "term": {
                                "remote_ip": {
                                    "value": ip
                                }
                            }
                        }
                    ]
                }
            },
            "size": 0,
        }
        aggs = {
            "rate": {
                "terms": {
                    "field": "domain.keyword",
                    "size": 10,
                    "order": {
                        "_count": "desc"
                    }
                }
            }
        }

        body["aggs"] = aggs
        logger.debug("{}".format(body))
        res = self.es.search(index=self.index, body=body)
        total = res.get('hits', {}).get('total', 0)
        rate = res.get('aggregations', {}).get(
            'rate', {}).get('buckets', [])
        if len(rate) == 0:
            return None

        # 计算百分比
        data = {
            "ip:": ip,
            "total": total,
        }
        for domain in rate:
            domain_key = domain.get('key', '')
            domain_num = domain.get('doc_count', 0)
            if not domain_key:
                continue
            data[domain_key] = "{:.2%}".format(domain_num / total)

        return data


def main():
    es = ES()
    top_ip_list = es.get_top_ip()
    for ip in top_ip_list:
        data = es.get_ip_rate(ip.get('key', ""))
        # ip_key = ip.get('key', "")
        # ip_cnt = ip.get('doc_count', 0)
        # print("{:<15}\t\t:{cnt}:\t\t{data}".format(ip_key, cnt=ip_cnt, data=data))
        logger.info("{data}".format(data=data))
    # 查看对应的ip 在24小时访问域名的比例


if __name__ == '__main__':
    main()

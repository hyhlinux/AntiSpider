import datetime
import elasticsearch
from .log import get_log

logger = get_log(name='esapi')


class ES(object):

    def __init__(self, hosts=None, index="nginx-access-log-*"):
        self.index = index
        self.es = self.connect_host(hosts=hosts)
        self.logger = logger

    @staticmethod
    def connect_host(hosts=None):
        if not hosts:
            raise Exception("host can't be empty ")
        es = elasticsearch.Elasticsearch(
            hosts,
            # sniff_on_start=True,
            # sniff_on_connection_fail=True,
            sniffer_timeout=600
        )
        return es

    def get_top_ip(self, size=1000, ip_white_list=None, ip_white_prefix_list=None):
        now = datetime.datetime.now()
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
        where_term = [
            {
                "field_name": "domain",
                "field_value": "download.pureapk.com"
            }
        ]
        must_not = []
        if ip_white_list:
            must_not.append({
                "terms": {
                  "remote_ip": ip_white_list,
                }
            })
        # ip段
        if ip_white_prefix_list:
            for ipp in ip_white_prefix_list:
                prefix = {
                    "prefix": {
                        "remote_ip": {
                            "value": ipp
                        }
                    }
                }
                must_not.append(prefix)

        body = self.make_body(where_term=where_term,
                              now_time=now, query_size=0, days=1, aggs=aggs, must_not=must_not)
        res = self.es.search(index=self.index, body=body)
        top_ip_list = res.get('aggregations', {}).get('topip', {}).get('buckets', [])
        if len(top_ip_list) == 0:
            return None
        self.logger.info("top{}_ip".format(len(top_ip_list)))
        return top_ip_list

    def get_ip_rate(self, ip=""):
        if not ip:
            return None
        now = datetime.datetime.now()
        where_term = [
            {
                "field_name": "remote_ip",
                "field_value": ip
            }
        ]

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

        body = self.make_body(where_term=where_term,
                              now_time=now, query_size=0, days=1, aggs=aggs)
        res = self.es.search(index=self.index, body=body)
        total = res.get('hits', {}).get('total', 0)
        rate = res.get('aggregations', {}).get(
            'rate', {}).get('buckets', [])
        if len(rate) == 0:
            return None

        # 计算百分比
        data = {
            "ip": ip,
            "total": total,
        }
        for domain in rate:
            domain_key = domain.get('key', '')
            domain_num = domain.get('doc_count', 0)
            if not domain_key:
                continue
            data[domain_key] = "{:.2%}".format(domain_num / total)

        return data


    def make_body(self, where_terms=None, where_term=None,
                  now_time=None, days=1, sort=None,
                  query_size=0, aggs=None, time_stamp="@timestamp",
                  must_not=None):
        """

        :param where_terms: 
        :param where_term: 
        :param now_time: 
        :param days: 
        :param sort: 
        :param query_size: 
        :param aggs: 
        :return: 
        """
        body = {
            "query": {
                "bool": {
                    "must": [
                    ],
                    "must_not": [
                    ],
                }
            },
        }
        # 0. must_not
        if must_not:
            body['query']['bool']['must_not'] = must_not
        # 1. size query 返回的结果数量
        if query_size:
            body['size'] = query_size

        # 2. sort
        if sort:
            body['sort'] = sort

        if not now_time:
            now_time = datetime.datetime.now()

        start_time = now_time - datetime.timedelta(days=days)
        query_range = {
            "range": {
                time_stamp: {
                    "gte": int(start_time.timestamp() * 1000),
                    "lte": int(now_time.timestamp() * 1000),
                    "format": "epoch_millis"
                }
            }
        }
        body['query']['bool']['must'].append(query_range)

        if where_terms:
            for item in where_terms:
                query_terms = {
                    "terms": {}
                }
                query_terms['terms'][item.field_name] = item.field_value
                body['query']['bool']['must'].append(query_terms)

        if where_term:
            for item in where_term:
                query_term = {
                    "term": {}
                }

                field_name = item.get('field_name', None)
                if not field_name:
                    continue
                query_term['term'][field_name] = {
                    "value": item.get('field_value', "")}
                body['query']['bool']['must'].append(query_term)

        if aggs:
            body["aggs"] = aggs

        self.logger.debug("{}".format(body))
        return body


def main():
    es = ES()
    top_ip_list = es.get_top_ip()
    for ip in top_ip_list:
        data = es.get_ip_rate(ip.get('key', ""))
        logger.info("{data}".format(data=data))
    # 查看对应的ip 在24小时访问域名的比例


if __name__ == '__main__':
    main()

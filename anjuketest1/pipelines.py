# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import cx_Oracle as oracle
from scrapy.exceptions import DropItem
from scrapy import log
# import pymongo
class Anjuketest1Pipeline(object):
    def process_item(self, item, spider):
        return item
class OraclePipeline(object):
    collection_name = 'anjukeurl'
    def __init__(self, oracle_uri):  # ,mongo_uri, mongo_db
        self.oracle_uri = oracle_uri
        # self.mongo_uri = mongo_uri
        # self.mongo_db = mongo_db
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            oracle_uri=crawler.settings.get('ORACLE_URI'),
            # mongo_uri=crawler.settings.get('MONGO_URI'),
            # mongo_db=crawler.settings.get('MONGO_DATABASE'),
        )
    def open_spider(self, spider):
        # self.client = pymongo.MongoClient(self.mongo_uri)
        # self.db = self.client[self.mongo_db]
        self.connect = oracle.connect(self.oracle_uri)
    def close_spider(self, spider):
        self.connect.close()
        # self.client.close()
    def process_item(self, item, spider):
        try:
            # 查重处理
            # if self.db[self.collection_name].find_one({'urls': item['来源链接']}):
                # 是否有重复数据
                # pass
            # else:
                # 插入数据
                # self.db[self.collection_name].update({'urls': item['来源链接']}, {'urls': item['来源链接']}, True)
                self.cursor = self.connect.cursor()
                sql = "insert into t_esf_ajk {0}".format(tuple(item)).replace("'", "") + "values {0}".format(tuple(item.values()))
                self.cursor.execute(sql)
                # 提交sql语句
                self.connect.commit()
        except Exception as error:
            # 出现错误时打印错误日志
            log.err(error)
        return item








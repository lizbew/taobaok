# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo


class MongodbPipeline(object)

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'taobaok')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    class Meta:
        abstract = True


class SaveProductPipeline(MongodbPipeline):
    collection_name = 'products'

    def process_item(self, item, spider):
        # TODO: add fixed id as product_id
        self.db[self.collection_name].replace_one({'num_id': item['num_id']}, dict(item), True)
        return item


class UpdateCrawlStatusPipeline(MongodbPipeline):
    """Update Crawl Status after save to Mongodb"""
    collection_name = 'crawl_uris'

    def process_item(self, item, spider):
        num_id = item['num_id']
        self.db[self.collection_name].update_many(
            {"num_id": num_id, 'status': {'$ne': 'DONE'}},
            {'$set': {'status': 'DONE'}}
        )

        return item


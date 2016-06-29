# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import codecs
import json
import pymongo
from scrapy import Selector


class MongodbPipeline(object):

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


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEPROPS_JSON_DIR = os.path.join(ROOT_DIR, 'cateprops')


class MapCatePropsPipeline(object):
    _cate_date_map = {}
    _not_exists_cate = set()
    
    def process_item(self, item, spider):
        cid = item.get('cid')
        attributes_list = item.get('attributes_list')
        if not cid or not attributes_list:
            return item

        select_props = []
        input_props = []
        for p in attributes_list.split('\n'):
            if p and u':' in p:
                arr = p.split(u':', 1)
                ret = self.__class__.map_cate_prop(cid, arr[0].strip(), arr[1].strip())
                if ret:
                    if isinstance(ret, tuple):
                        input_props.append(ret)
                    elif isinstance(ret, str) or isinstance(ret, unicode):
                        select_props.append(ret)
        if select_props:
            item['cate_props'] = ';'.join(select_props)
        if input_props:
            item['input_pids'] = ';'.join([ipt[0] for ipt in input_props])
            item['input_values'] = u';'.join([ipt[1] for ipt in input_props])

        return item


    @classmethod
    def map_cate_prop(cls, cid, key, value):
        if cid in cls._cate_date_map:
            jdata = cls._cate_date_map[cid]
        elif cid in cls._not_exists_cate:
            return None
        else:
            j_file = os.path.join(CATEPROPS_JSON_DIR,  '{}.json'.format(cid))
            if os.path.exists(j_file):
                jdata = json.load(codecs.open(j_file, 'r', 'utf-8'))
                cls._cate_date_map[cid] = jdata
            else:
                cls._not_exists_cate.add(cid)
                return None
    
        cateProps = jdata['catProps']
        p = None
        for cp in cateProps:
            if key == cp['label']:
                p = cp
                break
        # if not find label
        if not p:
            return None
        # for keySpus, need user input manually. reutrn tuple
        if not 'options' in p:
            return (p['key'], value)
        # select select
        if p['select_mode'] == 'single':
            for opt in p['options']:
                if value == opt[1]:
                    return opt[0]
        elif p['select_mode'] == 'multi':
            ret_list = []
            for v in value.split(' '):
                for opt in p['options']:
                    if v == opt[1]:
                        ret_list.append(opt[0])
            return ';'.join(ret_list)


class BuildWapDescPipeline(object):

    def process_item(self, item, spider):
        desc = item.get('description')
        if desc:
            sel = Selector(text=desc, type='html')
            txt_list = sel.xpath('//text()').extract()
            img_list = sel.xpath('//img/@src').extract()
            item['wireless_desc'] = u'<wapDesc>{}{}</wapDesc>'.format(
                    u''.join([u'<txt>%s</txt>' % txt.strip() for txt in txt_list if txt.strip()]),
                    u''.join([u'<img>%s</img>' % img for img in img_list]))
        return item


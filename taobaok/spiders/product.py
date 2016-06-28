# -*- coding: utf-8 -*-
import json
import copy
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from taobaok import jsutil
from taobaok.items import ProductItem
import pymongo


def get_contain_text(selector):
    text_list = selector.xpath('text()').extract()
    if text_list:
        return text_list[0]
    return ''

def parse_jsonp_data(text):
    t = text[text.index('(')+1 : text.rindex(')')]
    return json.loads(t)


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["taobao.com", "taobaocdn.com", "alicdn.com"]
    #start_urls = (
    #    'https://item.taobao.com/item.htm?id=529332291181',
    #)
    
    def query_new_crawl_uris(self):
        client = pymongo.MongoClient(self.settings['MONGO_URI'])
        db = client[self.settings['MONGO_DB']]
        try:
            cursor = db['crawl_uris'].find({'status': 'NEW'})
            return [doc['detail_url'] for doc in cursor]
        except Exception as ex:
            self.logger.error('Query mongodb collection crawl_uris error %s', repr(ex))
        finally:
            client.close()

    def start_requests(self):
        detail_urls = self.query_new_crawl_uris()
        if detail_urls:
            for url in detail_urls:
                yield self.make_requests_from_url(url)

    def parse(self, response):
        script_text = response.xpath('//head/script[1]/text()').extract()[0]
        var_g_config = jsutil.extract_g_config(script_text)
        idata_item = var_g_config['idata']['item']

        item = ProductItem()

        item['detail_url'] = response.url
        #item['title'] = idata_item['title']  # it's string repr like '\\u5B9E\\u62CD2016', need to parse 
        item['title'] = response.css('#J_Title > .tb-main-title::attr("data-title")').extract()[0]
        item['cid'] = idata_item['cid']
        item['price'] = response.css('#J_StrPrice .tb-rmb-num').xpath('text()').extract()[0]
        item['outer_id'] = item['num_id'] = var_g_config['itemId']
        item['pic'] = idata_item['pic']
        item['auction_images'] = '^'.join(idata_item['auctionImages'])
        item['subtitle'] = get_contain_text(response.css('.tb-subtitle'))
        item['size_group_name'] = idata_item['sizeGroupName']
        item['attributes_list'] = '\n'.join(response.css('.attributes-list li').xpath('text()').extract())

        # .J_Prop_measurement
        prop_li = response.css('#J_isku .J_Prop_measurement li')
        ar = []
        for li in prop_li:
            k = li.xpath('@data-value').extract()[0]
            v = li.css('span').xpath('text()').extract()[0]
            ar.append('%s|%s' % (k, v))
        item['prop_measurement'] = '^'.join(ar)

        # .J_Prop_Color
        prop_li = response.css('#J_isku .J_Prop_Color li')
        ar = []
        for li in prop_li:
            k = li.xpath('@data-value').extract()[0]
            v = li.css('span').xpath('text()').extract()[0]
            ar.append('%s|%s' % (k, v))
        item['prop_color'] = '^'.join(ar)


        meta = {
            'item': item,
            'sibUrl': 'https:' + var_g_config['sibUrl'] + '&callback=onSibRequestSuccess',
            'descUrl': 'http:' + var_g_config['descUrl'],
        }
        yield scrapy.Request(meta['sibUrl'], callback=self.parse_sib_jsonp, errback=self.errback_sib_jsonp, meta=meta)

    def parse_sib_jsonp(self, response):
        meta = copy.copy(response.meta)
        item = meta['item']
        if response.status == 200:
            data = parse_jsonp_data(response.body)['data']
            item['send_city']  = data['deliveryFee']['data']['sendCity']
            delivery_fee = data['deliveryFee']['data']['serviceInfo']['list'][0]
            item['delivery_fee_info'] = delivery_fee['info']
            if 'markInfo' in delivery_fee:
                item['delivery_fee_markinfo'] = delivery_fee['markInfo']
            price = data['price']
            item['quantity'] = data['dynStock']['sellableQuantity']
            item['sku_props'] = ''.join(['%s:%s::%s' % (price, v['stock'], k[1:])  for k, v in data['dynStock']['sku'].items()])
        yield scrapy.Request(meta['descUrl'], callback=self.parse_product_description, errback=self.errback_sib_jsonp, meta=meta)

    def errback_sib_jsonp(self, failure):
        self.logger.error(repr(failure))
        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error('HttpError on %s', response.url)

    def parse_product_description(self, response):
        # Content-Type:text/plain; charset=GBK
        # scrapy.http.TextResponse
        item = response.meta['item']
        try:
            # version 1.1
            content = response.text  # response.body.decode(response.encoding)
        except AttributeError:
            # version 1.0.6
            content = response.body_as_unicode()
        var_index = content.index('var desc=')
        if var_index > -1:
            content = content[var_index + 10:content.rindex("'")]
        item['description'] = content
        yield item

        




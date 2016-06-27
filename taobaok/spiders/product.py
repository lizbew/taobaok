# -*- coding: utf-8 -*-
import json
import copy
import scrapy
from scrapy.spidermiddlewares.httperror import HttpError
from taobaok import jsutil
from taobaok.items import ProductItem


def get_contain_text(selector):
    return selector.xpath('text()').extract()[0]

def parse_jsonp_data(text):
    t = text[text.index('(')+1 : text.rindex(')')]
    return json.loads(t)

class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["taobao.com", "taobaocdn.com", "alicdn.com"]
    start_urls = (
        'https://item.taobao.com/item.htm?id=529332291181',
    )

    def parse(self, response):
        script_text = response.xpath('//head/script[1]/text()').extract()[0]
        var_g_config = jsutil.extract_g_config(script_text)
        idata_item = var_g_config['idata']['item']

        item = ProductItem()

        item['detail_url'] = response.url
        item['title'] = idata_item['title']
        item['cid'] = idata_item['cid']
        item['price'] = response.css('#J_StrPrice .tb-rmb-num').xpath('text()').extract()[0]
        item['outer_id'] = item['num_id'] = var_g_config['itemId']
        item['pic'] = idata_item['pic']
        item['auction_images'] = '<>'.join(idata_item['auctionImages'])
        item['subtitle'] = get_contain_text(response.css('.tb-subtitle'))
        item['size_group_name'] = idata_item['sizeGroupName']
        item['attributes_list'] = '\n'.join(response.css('.attributes-list li').xpath('text()').extract())
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
            delivery_fee = data['deliveryFee']['data']['serviceInfo']['list'][0]
            item['delivery_fee_info'] = delivery_fee['info']
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
        item = response.meta['item']
        content = response.body
        var_index = content.index('var desc=')
        if var_index > -1:
            content = content[var_index + 10:content.rindex("'")]
        item['description'] = content
        yield item

        




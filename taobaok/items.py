# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    detail_url = scrapy.Field()
    title = scrapy.Field()
    cid = scrapy.Field()
    location = scrapy.Field()
    price = scrapy.Field()
    num = scrapy.Field()
    description = scrapy.Field()
    cate_props = scrapy.Field()
    picture = scrapy.Field()
    skui_props = scrapy.Field()
    outer_id = scrapy.Field()
    num_id= scrapy.Field()
    pic = scrapy.Field()
    auction_images = scrapy.Field()
    subtitle = scrapy.Field()
    size_group_name = scrapy.Field()
    attributes_list = scrapy.Field()
    #delivery_fee = scrapy.Field()
    delivery_fee_info = scrapy.Field()
    delivery_fee_markinfo = scrapy.Field()
    quantity = scrapy.Field()
    sku_props = scrapy.Field()
    send_city = scrapy.Field()
    prop_measurement = scrapy.Field()
    prop_color = scrapy.Field()
    





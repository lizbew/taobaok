import os
import sys
import re
from scrapy.commands import ScrapyCommand
from scrapy.exceptions import UsageError

import pymongo

class Command(ScrapyCommand):

    requires_project = True
    default_settings = {'LOG_ENABLED': True}

    def syntax(self):
        return '<num_id>'

    def short_desc(self):
        return 'Add Taobao Item'

    def long_desc(self):
        return 'Add a new Taobao Item <num_id> to the Crawler'

    def _err(self, msg):
        sys.stderr.write(msg + os.linesep)
        self.exitcode = 1

    def run(self, args, opts):
        if len(args) != 1 or not re.match('[0-9]+', args[0]):
            raise UsageError()

         client = pymongo.MongoClient(self.settings['MONGO_URI'])
         db = self.client[self.settings['MONGO_DB']]
         doc = {
             'num_id': args[0],
             'detail_url': 'https://item.taobao.com/item.htm?id=%s' % args[0]
             'status': 'NEW',
         }
         db['crawl_uris'].insert_one(doc)
         client.close()
         

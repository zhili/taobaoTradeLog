#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Parse deals history to give you the price trendency of your favarate.
# huzhili At mail.google.com
import urllib
import codecs
from pyquery import PyQuery as pq
import UserDict
import time
import cgi, urlparse
import sys
import re

class tradeItem(UserDict.UserDict):
   def __unicode__(self):
      return '\t'.join([self[k] for k in self.keys()])
   def __str__(self):
      return unicode(self).encode('utf-8')

class Url(object):
   def __init__(self, url):
      self.scheme, self.netloc, self.path, self.params, self.query, self.fragment = urlparse.urlparse(url)
      self.args = dict(cgi.parse_qsl(self.query))
   def __str__(self):
      self.query = urllib.urlencode(self.args)
      return urlparse.urlunparse((self.scheme, self.netloc, self.path, self.params, self.query, self.fragment))


#item_url = 'http://tbskip.taobao.com/json/show_buyer_list.htm?page_size=15&is_start=false&item_type=b&ends=1313141989000&starts=1312537189000&item_id=12419412251&user_tag=206665744&old_quantity=1392&zhichong=true&sold_total_num=215&seller_num_id=69211806&bidPage='

def parseTaobaoTradeHistory(url, item_store):
   try: 
      orig_data = urllib.urlopen(url).read()
      decoded_data = orig_data.decode('gb2312')
   except:
      time.sleep(2)
      return
   d = pq(decoded_data)
   detail_table = d('table.table-deal-record')
   for row in detail_table('tr'):
      fields = row.getchildren()
      newTradeItem = tradeItem()
      newTradeItem['buyer'] = fields[0].text_content().strip() # buyer
      newTradeItem['goods'] = fields[1].text_content().strip().replace('\r\n', '').replace('\t', '') # goods
      newTradeItem['price'] = fields[2].text_content().strip() # price
      newTradeItem['amount'] = fields[3].text_content().strip() # amount
      newTradeItem['chargetime'] = fields[4].text_content().strip()# time
      newTradeItem['status'] = fields[5].text_content().strip() # status
      item_store.append(newTradeItem.copy())

def logItems(items, file_name):
   output_file = codecs.open(file_name, 'w', 'utf-8-sig')
   for item in items:
      output_file.write(unicode(item)+'\n')
   output_file.close()

def parseItemJsonURL(base_url, goods_name='HTC'):
   """parse item trade history json url from baseurl"""
   json_urls = []
   orig_data = urllib.urlopen(base_url).read()
   d = pq(orig_data)
   trade_view = d('#J_listBuyerOnView')
   base_json_url = trade_view.attr("detail:params")
   temp_json_url = Url(base_json_url)
   temp_json_url.args['isFromDetail'] = 'yes'
   goods_name = temp_json_url.args['title']
   del temp_json_url.args['title']
   pages = int(temp_json_url.args['sold_total_num']) / int(temp_json_url.args['page_size'])
   for i in range(1, pages): 
      temp_json_url.args['bid_page'] = i
      json_urls.append(str(temp_json_url))

   return json_urls, goods_name.decode('gb2312')


def main(goods_url):
   item_urls, file_name = parseItemJsonURL(goods_url)
   # windows filename limit
   # http://msdn.microsoft.com/en-us/library/aa365247.aspx
   valic_filename = re.sub(r'/|\\|<|>|:|"|\?|\*|\|', '', file_name) 
   item_store = []
   for item_url in item_urls:
      parseTaobaoTradeHistory(item_url, item_store)
   logItems(item_store, unicode(valic_filename) + '.csv')

if __name__ == '__main__':
   if len(sys.argv) != 2:
      sys.exit("you must provide the url of your favarate")
   main(sys.argv[1]) 
   

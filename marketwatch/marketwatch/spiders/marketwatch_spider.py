import sys
import os
from pathlib import Path
path_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(1, os.path.join(path_root))

import scrapy
import bs4
import datetime
import re
from marketwatch.items import MarketwatchItem
from util.util import get_random_header, remove_line, remove_first_end_spaces, get_ucodes


class MarketwatchSpiderSpider(scrapy.Spider):
    name = 'marketwatch_spider'

    def start_requests(self):
        start_urls = []
        for k, v in get_ucodes().items():
            for v1 in v:
                if '.HK' in v1:
                    ucode = v1.replace('.HK', '').zfill(4)
                    ucode2 = v1.replace('.HK', '').zfill(5)
                    url = 'https://www.marketwatch.com/investing/stock/'+ucode+'/download-data?countrycode=hk&mod=mw_quote_tab'
                    start_urls.append({'url': url, 'ucode': ucode2})

        # start_urls = [{'url': 'https://www.marketwatch.com/investing/stock/1088/download-data?countrycode=hk&mod=mw_quote_tab', 'ucode': '00700'}]
        for data in start_urls:
            yield scrapy.Request(url=data['url'], headers=get_random_header(), callback=self.parse, meta=data)

    def parse(self, response):
        item = MarketwatchItem()
        html = bs4.BeautifulSoup(response.body, 'lxml')
        item['ucode'] = response.meta.get('ucode')

        for v1 in html.find_all('div', {'class': 'download-data'}):
            for v2 in v1.find_all('tr', {'class': 'table__row'}):
                stime = v2.find('div', {'class': 'fixed--cell'})
                if stime is not None and len(list(stime.getText())) == 10:
                    stime2 = datetime.datetime.strptime(stime.getText(), '%m/%d/%Y')
                    item['stime'] = stime2.strftime('%Y-%m-%d')
                    v3 = v2.find_all('td', {'class': 'overflow__cell'})
                    for i in [1, 2, 3, 4, 5]:
                        v4 = float(v3[i].getText().replace('HK$', '').replace(',', ''))
                        if i == 1:
                            item['open'] = v4
                        elif i == 2:
                            item['high'] = v4
                        elif i == 3:
                            item['low'] = v4
                        elif i == 4:
                            item['last'] = v4
                        elif i == 5:
                            item['vol'] = v4
                    yield item
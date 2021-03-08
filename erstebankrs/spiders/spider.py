import json

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import ErstebankrsItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.erstebank.rs/bin/erstegroup/gemesgapi/feature/gem_site_sr_www-erstebank-rs-sr-es7/,"

base_payload="{\"filter\":[{\"key\":\"path\",\"value\":\"/content/sites/rs/ebs/www_erstebank_rs/sr/o-nama/press/saopstenja" \
        "\"},{\"key\":\"tags\",\"value\":\"rs:ebs/saopstenja,rs:ebs/saopstenja/csr," \
        "rs:ebs/saopstenja/finansijski-rezultati,rs:ebs/saopstenja/istrazivanja," \
        "rs:ebs/saopstenja/obnovljivi-izvori-energije,rs:ebs/saopstenja/prognoze," \
        "rs:ebs/saopstenja/program-sponzorstava,rs:ebs/saopstenja/proizvodi,rs:ebs/saopstenja/superste," \
        "rs:ebs/saopstenja/Edukacija,rs:ebs/saopstenja/socijalno-bankarstvo,rs:ebs/saopstenja/Stednja\"}],\"page\":%s," \
        "\"query\":\"*\",\"items\":15,\"sort\":\"DATE_RELEVANCE\",\"requiredFields\":[{\"fields\":[" \
        "\"teasers.NEWS_DEFAULT\",\"teasers.NEWS_ARCHIVE\",\"teasers.newsArchive\"]}]} "

headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Content-Type': 'application/json',
  'Accept': '*/*',
  'Origin': 'https://www.erstebank.rs',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.erstebank.rs/sr/o-nama/press/saopstenja',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'TCPID=121321448317217215637; lhc_per=vid|ed9494cd05a225bc4040; TC_PRIVACY=0@009@3%2C2@1@1614689313158@; TC_PRIVACY_CENTER=3%2C2; _gcl_au=1.1.16714061.1614689313; _ga=GA1.2.666498560.1614689313; _fbp=fb.1.1614689313267.1441463594; _cs_c=1; _CT_RS_=Recording; WRUID=3188636288041269; _gid=GA1.2.669893293.1615194319; 3cf5c10c8e62ed6f6f7394262fadd5c2=38152618e0350b39d330076005a62c18; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22saopstenja%22%5D%2C%222%22%3A%5B%22Page%20Title%22%2C%22Saop%C5%A1tenja%22%5D%2C%223%22%3A%5B%22Page%20Template%22%2C%22standardContentPage%22%5D%2C%224%22%3A%5B%22Language%22%2C%22sr_me%22%5D%7D; _cs_id=8a5a22f4-8f0f-a713-fc01-e5ecbb1cfb20.1614689313.2.1615196761.1615194321.1.1648853313881.Lax.0; _cs_s=18.1; __CT_Data=gpv=22&ckp=tld&dm=erstebank.rs&apv_55_www56=22&cpv_55_www56=22&rpv_55_www56=21',
}


class ErstebankrsSpider(scrapy.Spider):
	name = 'erstebankrs'
	start_urls = ['https://www.erstebank.rs/sr/o-nama/press/saopstenja']
	page = 0

	def parse(self, response):
		payload = base_payload % self.page
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['hits']['hits']:
			link = post['_source']['url']
			date = post['_source']['date']
			title = post['_source']['title']
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})
		if self.page < raw_data['hits']['total']//15:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date, title):
		description = response.xpath('(//div[@class="w-auto mw-full rte"])[position()>1]//text()[normalize-space()]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ErstebankrsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest
from functools import partial
import os
import scrapy

class Crawling(CrawlSpider):
    name = "beritabali"
    start_urls = ["http://www.balipost.com/bali/denpasar"]

    def __init__(self):
        self.urls = []
        self.index = 0

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.requests)

    def requests(self, response):
        if(len(self.urls) <= 500):
            page = response.xpath("//div[contains(@class, 'page-nav')]//a/@href")
            pageurl = 'http:' + page.extract()[-1]
            links = response.xpath("//h3[contains(@class, 'entry-title td-module-title')]//a/@href")
            for link in links:
                url = 'http:' + link.extract()
                self.urls.append(url)
            yield SplashRequest(pageurl, callback=self.requests)
        else:
            for url in self.urls:
                yield SplashRequest(url, callback=partial(self.parse_page))

    def parse(self, response):
        results = response.xpath("//h3[contains(@class, 'entry-title td-module-title')]//a/@href")
        for res in results:
            url = 'http:' + res.extract()
            self.urls.append(url)
        yield SplashRequest(response.request.url, callback=self.requests)
    
    def parse_page(self, response):
        results = response.xpath("//div[contains(@class, 'td-post-content')]//text()")
        titles = response.xpath("//h1[contains(@class, 'entry-title')]//text()")
        text = ''
        title = ''
        for t in titles:
            title += t.extract()

        for res in results:
            text += res.extract()

        path = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'data'))
        titlePath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'judul'))
        f=open(path+"/berita-"+str(self.index)+".txt","w+")
        f.write(text)

        j=open(titlePath+"/judul-"+str(self.index)+".txt","w+")
        j.write(title)
        self.index +=1
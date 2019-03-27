#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Project: alijob
import pymongo
from pyspider.libs.base_handler import *


class Handler(BaseHandler):
    crawl_config = {
    }
    client = pymongo.MongoClient(host="localhost", port=27017)
    db = client['ali']
    def __init__(self):
        self.page = 1
        self.total_page = 10
        self.baseurl = 'http://job.alibaba.com/zhaopin/positionList.htm?spm=a2obv.11410899.0.0.55ef6c61NoDzQM#page/'
    @every(minutes=24 * 60)
    def on_start(self):
        while self.page < self.total_page:
            self.crawl(self.baseurl+str(self.page), callback=self.index_page, validate_cert=False,fetch_type="js")
            self.page += 1
    @config(age=10 * 24 * 60 * 60)
    def index_page(self, response):
        for each in response.doc('td > span > a').items():
            self.crawl(each.attr.href, callback=self.detail_page)

    @config(priority=2)
    def detail_page(self, response):
        url = response.url
        title = response.doc('body > div.main-box.layout > div > div.lf-border-box > h3').text()
        description = response.doc('.detail-content').text()
        return {
            "url": url,
            "title": title,
            "description": description
        }
    def on_result(self, result):
        if result:
            self.save_to_mongo(result)

    def save_to_mongo(self, result):
        if self.db['ali'].insert(result):
            print("save to mongodb success", result)

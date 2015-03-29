#!/usr/bin/env python
# -*- coding: utf-8 -*-
#! 强制默认编码为utf-8
import sys
import requests
import json
from alfred.feedback import Feedback

token= 'MQftlYBElcsOEzwKSvv2vbZYnQiDOm'

# 扇贝词典
class ShanbayDict():
    def __init__(self):
        self.feedback = Feedback()

    def parse(self, data):
        if(data):
            word = data['content']
            # 发音
            pron = data['pron']
            title = "%s [%s]" % (word, pron)
            subtitle = data['definition']
            self.addItem(title = title, subtitle = subtitle, arg = word)
            # 解释
            if data.has_key('en_definitions') and data['en_definitions']:
                for type in data['en_definitions']:
                    for line in data['en_definitions'][type]:
                        title = type+', '+line
                        if not title:
                            continue
                        self.addItem(title = title, arg = word)
        else:
            self.addItem(title='no results')

    def query(self, word):
        if not word or not isinstance(word, (str, unicode)):
            return
        self.query_word = word

        url = 'https://api.shanbay.com/bdc/search/?word='+word
        try:
            r = requests.get(url)
            res = json.loads(r.text)
            if res['status_code'] == 0:
                self.parse(res['data'])
            else:
                self.addItem(title='query no results')
        except:
            self.addItem(title='query fail')

    def addItem(self, **kwargs):
        self.feedback.addItem(**kwargs)

    def output(self):
        if self.feedback.isEmpty():
            self.addItem(
                title       = self.query_word,
                subtitle    = 'Sorry, no result.',
                arg         = self.query_word )
        print(self.feedback.get(unescape = True))

if __name__ == '__main__':
    d = ShanbayDict()
    d.query(sys.argv[1])
    d.output()

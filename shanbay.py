#!/usr/bin/env python
# -*- coding: utf-8 -*-
#! 强制默认编码为utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os
import urllib
import urllib2
import json
from alfred.feedback import Feedback

token = 'kc8y3MrdvhEHVvTr3BfdnYLBPLnpFw'

# 扇贝词典
class ShanbayDict():
    def __init__(self):
        self.feedback = Feedback()

    def check_token(self, isexit = True):
        if os.path.isfile('shanbay_token'):
            token = open('shanbay_token').read().strip()
            print 'ok'
            print token
            return True
        else:
            self.addItem(title = '授权登陆扇贝', subtitle = '授权后才可以将单词添加到词库')
            if isexit:
                self.output()
                sys.exit()

            return False

    def parse(self, voc):
        if(voc):
            word = voc['content']
            # 发音
            pron = voc['pron']
            title = "%s [%s]" % (word, pron)
            subtitle = voc['definition']
            self.addItem(title = title, subtitle = subtitle, arg = word)
            self.check_token(False)

            # 解释
            if voc.has_key('en_definitions') and voc['en_definitions']:
                for type in voc['en_definitions']:
                    for line in voc['en_definitions'][type]:
                        title = type+', '+line
                        if not title:
                            continue
                        self.addItem(title = title, arg = word)
        else:
            self.addItem(title='no results')

    def query_voc(self, word):
        if not word or not isinstance(word, (str, unicode)):
            return None
        self.query_word = word

        url = 'https://api.shanbay.com/bdc/search/?word='+word
        try:
            r = urllib2.urlopen(url).read()
            res = json.loads(r)
            if res['status_code'] == 0:
                return res['data']
            else:
                return None
        except:
            return None

    def query(self, word):
        voc = self.query_voc(word)
        if voc:
            self.parse(voc)
        else:
            self.addItem(title='word not exists')

    def add(self, word):
        hastoken = self.check_token(0)
        if not hastoken:
            print '请先授权登陆扇贝'
            sys.exit()

        voc = self.query_voc(word)
        if not voc:
            print 'word not exists'
            return False

        url = 'https://api.shanbay.com/bdc/learning/?access_token='+token
        try:
            data = urllib.urlencode({'id':voc['id']})
            req = urllib2.Request(url, data)
            r = urllib2.urlopen(req).read()
            res = json.loads(r)
            if res['status_code'] == 0:
                #通知内容会换行，这里直接返回全部字符
                print '"'+word+'" 添加成功'
            else:
                print 'add fail'
        except:
            print 'request fail'

    def examples(self, word):
        self.check_token()
        voc = self.query_voc(word)
        if not voc:
            self.addItem(title='word not exists')
            return False

        url = 'https://api.shanbay.com/bdc/example/?vocabulary_id=%d&type=%s&access_token=%s' % (voc['id'], 'sys', token)
        try:
            r = urllib2.urlopen(url).read()
            res = json.loads(r)
            if res['status_code'] == 0:
                for s in res['data']:
                    self.addItem(title = s['annotation'], subtitle = s['translation'])
                    #print s['annotation'] + s['translation'] + "\n"
            else:
                self.addItem(title = 'request fail')
        except:
            self.addItem(title = 'request fail')

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
    try:
        op_word = sys.argv[2]
    except:
        op_word = ''

    if op_word:
        if sys.argv[1] == 'add':
            d.add(op_word)
        elif sys.argv[1] == 'examples':
            d.examples(op_word)
            d.output()
        else:
            print 'error'
    else:
        d.query(sys.argv[1])
        d.output()


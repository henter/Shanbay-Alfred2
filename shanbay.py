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
import time
from alfred.feedback import Feedback

token_file = os.path.abspath('token')

# 扇贝词典
class ShanbayDict():
    def __init__(self):
        self.feedback = Feedback()

    def check_token(self, isexit = True):
        if not self.read_token():
            self.addItem(title = '授权登陆扇贝', subtitle = '授权后才可以将单词添加到词库', arg = 'need_auth')
            if isexit:
                self.output()
                sys.exit()
            return False
        return True

    def read_token(self):
        if os.path.isfile(token_file):
            token_json = json.loads(open(token_file).read().strip())
            #已过期
            if token_json and token_json['timestamp'] + token_json['expires_in'] < int(time.time()):
                return ''
            return token_json['access_token']
        return ''

    def parse(self, voc):
        if(voc):
            word = voc['content']
            # 发音
            pron = voc['pron']

            title = "%s [%s]" % (word, pron)
            subtitle = voc['definition'].decode("utf-8")
            subtitle = subtitle.replace("\n", '').replace('&', '')

            self.addItem(title = title, subtitle = subtitle, arg = word)
            self.check_token(False)

            # 解释
            if voc.has_key('en_definitions') and voc['en_definitions']:
                for type in voc['en_definitions']:
                    for line in voc['en_definitions'][type]:
                        title = type+', '+line
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

    def open_word(self, word):
        voc = self.query_voc(word)
        if voc:
            word_url = 'http://www.shanbay.com/bdc/vocabulary/%d/' % (voc['id'])
            os.system('open ' + word_url)
            return True
        else:
            print 'word not exists'

    def open_oauth(self):
        auth_url = 'https://api.shanbay.com/oauth2/authorize/?client_id=00eef0bf7a879381c08b\&response_type=code\&state=123'
        os.system('open ' + auth_url)
        return True

    def get_token(self, code):
        url = 'http://sbalfred.sinaapp.com/token'
        data = urllib.urlencode({'code':code})
        req = urllib2.Request(url, data)

        try:
            r = urllib2.urlopen(req).read()
            res = json.loads(r)
            if 'error' in res:
                print '授权失败: ' + res['error']
                sys.exit()

            #save json to local
            f = open(token_file, 'w')
            f.write(r)
            f.close()
            os.system('open https://sbalfred.sinaapp.com/oauth_success')
            print '授权成功，现在可以使用添加单词或例句了'
        except:
            print '请求错误'

        return True

    def add(self, word):
        if word == 'need_auth':
            self.open_oauth()
            return False

        hastoken = self.check_token(0)
        if not hastoken:
            self.open_oauth()
            print '请先授权登陆扇贝'
            sys.exit()

        voc = self.query_voc(word)
        if not voc:
            print 'word not exists'
            return False

        url = 'https://api.shanbay.com/bdc/learning/?access_token='+self.read_token()
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

        url = 'https://api.shanbay.com/bdc/example/?vocabulary_id=%d&type=%s&access_token=%s' \
            % (voc['id'], '', self.read_token())
        try:
            r = urllib2.urlopen(url).read()
            res = json.loads(r)
        except:
            self.addItem(title = 'request fail')
            return False

        if res['status_code'] == 0:
            for s in res['data']:
                title = s['annotation']
                title = title.replace('<vocab>', '[')
                title = title.replace('</vocab>', ']')
                self.addItem(title = title, subtitle = s['translation'], arg = str(s['id']))
                #print s['annotation'] + s['translation'] + "\n"
        else:
            self.addItem(title = 'request error')

    def add_example(self, example_id):
        hastoken = self.check_token(0)
        if not hastoken:
            self.open_oauth()
            print '请先授权登陆扇贝'
            sys.exit()

        url = 'https://api.shanbay.com/bdc/learning_example/?access_token='+self.read_token()
        try:
            data = urllib.urlencode({'example_id':example_id})
            req = urllib2.Request(url, data)
            r = urllib2.urlopen(req).read()
            res = json.loads(r)
            if res['status_code'] == 0:
                print '例句收藏成功'
            else:
                print 'add fail'
        except:
            print 'request fail'

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
        elif sys.argv[1] == 'open_word':
            d.open_word(op_word)
        elif sys.argv[1] == 'examples':
            d.examples(op_word)
            d.output()
        elif sys.argv[1] == 'add_example':
            d.add_example(op_word)
        elif sys.argv[1] == 'get_token':
            #code = op_word
            d.get_token(op_word)
        else:
            print 'error'
    else:
        d.query(sys.argv[1])
        d.output()


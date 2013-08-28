#!/usr/bin/env python
# -*- coding: utf-8 -*-
#! 强制默认编码为utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8') 

import urllib, urllib2, json, time
from pprint import pprint
from pdb import set_trace
import requests
import copy
from lxml import html
from alfred.feedback import Feedback 

from config import host, service, addword, loginurl, username, pwd

class LoginException(Exception):
    """登录异常
    """
    pass

# 扇贝词典
class ShanbayDict():
    def __init__(self):
        self.service = service
        self.query_word =''
        self.feedback = Feedback()
        # 从字典中安全的取出值
        self.save_get_dict_value = lambda d, k: d[k] if d.has_key(k) else ''

    def login(self):

        headers = {
        'Host': host,
        'User-Agent': (' Mozilla/5.0 (Windows NT 6.2; rv:23.0) Gecko'
                       + '/20100101 Firefox/23.0'),
        }

        # 首先访问一次网站，获取 cookies
        r_first_vist = requests.get(loginurl, headers=headers,
                                    stream=True)
        # 判断 HTTP 状态码是否是 200
        if r_first_vist.status_code != requests.codes.ok:
            raise LoginException
        # 获取 cookies 信息
        cookies_first_vist = r_first_vist.cookies.get_dict()

        # 登陆post操作相关信息
        url_post = loginurl
        # 获取csrftoken
        token = cookies_first_vist.get('csrftoken')
        # post请求的headers
        headers_post = copy.deepcopy(headers)
        headers_post.update({
            'Refere': loginurl,
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        cookies_post = cookies_first_vist
        # post 提交的内容
        data_post = {
            'csrfmiddlewaretoken': token,  # csrf
            'username': username,  # 用户名
            'password': pwd,  # 密码
            'login': '',
            'continue': 'home',
            'u': 1,
            'next': '',
        }

        # 提交登录表单同时提交第一次访问网站时生成的 cookies
        r_login = requests.post(url_post, headers=headers_post,
                                cookies=cookies_post, data=data_post,
                                allow_redirects=False, stream=True)
        
        self.cookies = r_login.cookies
         # print r_login.url
        if r_login.status_code == requests.codes.found:
            # 返回登录成功后生成的 cookies
            self.cookies = r_login.cookies
            return True
        else:
            raise LoginException

    def fetch(self, word):
        islogin = self.login()

        if islogin == False:
            print '登陆失败'
            return

        url = self.service+word

        try:
            r = requests.get(url, cookies = self.cookies)
            res = json.loads(r.text)
        except:
            return {}
        return res

    def parse(self, data):

        if(data['voc']):
            voc = data['voc']
            word = voc['content']

            # 发音
            pron = voc['pron']
            title = "%s [%s]" % (word, pron)
            subtitle = voc['definition']
            self.addItem(title = title, subtitle = subtitle, arg = word)
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

    def query(self, word):
        if not word or not isinstance(word, (str, unicode)):
            return
        self.query_word = word
        self.parse( self.fetch(word) )

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

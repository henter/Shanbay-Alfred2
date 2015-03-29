#!/usr/bin/env python
# -*- coding: utf-8 -*-
#! 强制默认编码为utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import urllib, urllib2, json, time
import requests
import copy
from config import host,service, addword, loginurl, username, pwd

class LoginException(Exception):
    """登录异常
    """
    pass

# 扇贝词典
class ShanbayDict():
    def __init__(self):
        self.service = service
        self.addword = addword

    def login(self):
        headers = {
            'Host': host,
            'User-Agent': (' Mozilla/5.0 (Windows NT 6.2; rv:23.0) Gecko /20100101 Firefox/23.0'),
        }

        # 首先访问一次网站，获取 cookies
        r_first_vist = requests.get(loginurl, headers=headers, stream=True)
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
        r_login = requests.post(url_post, headers=headers_post, cookies=cookies_first_vist, data=data_post, allow_redirects=False, stream=True)
        self.cookies = r_login.cookies
         # print r_login.url
        if r_login.status_code == requests.codes.found:
            # 返回登录成功后生成的 cookies
            self.cookies = r_login.cookies
            return True
        else:
            raise LoginException


    def add(self, word):

        islogin = self.login()
        if islogin == False:
            print '登陆失败'
            return

        url = self.addword+word

        r = requests.get(url, cookies = self.cookies)
        res = json.loads(r.text)
        #通知内容会换行，这里直接返回全部字符
        print '"'+word+'" 添加成功' if res['id'] else 0


if __name__ == '__main__':
    d = ShanbayDict()
    d.add(sys.argv[1])

'''
Created on 2025/05/25

HTTPセッション関連のコードをHttpProducerから分離
RemoteSettings.pyから利用

@author: kuyamakazuhiro
'''

import requests

class HttpSession:
    def __init__(self, post_url, user_name, password, multi):
        self.post_url = post_url
        self.request_pool =[]
        self.user_name = user_name
        self.password = password
        self.multi = multi
        self.hasSession = False
        if self.multi:
            r = self.getSession()
            #print(f"initialize result {r}")
        else:
            self.session = requests.Session()

        
    def getSession(self):
        self.session = requests.Session()
        # csrfトークンを取得する
        try:
            response = requests.get(self.post_url+"account/csrf/")
        except requests.exceptions.ConnectionError as e:
            print("*ConnectionError*")
            print(e)
            return False
        #response = requests.get(self.post_url+"csrf/")
        self.csrf_cookie = response.cookies.get('csrftoken')
        self.csrf = response.headers['X-CSRFToken']

        # ログインして、サーバとセッションを確立する
        request_body ={'username': self.user_name, 'password': self.password}
        #CSRFの対策として、CSRFトークンとリファラーをヘッダにセットして送信
        headers = {"X-CSRFToken": self.csrf, "Referer":self.post_url,}
        cookies = {"csrftoken": self.csrf_cookie}
        try:
            response = self.session.post(self.post_url+"account/api-login/", headers=headers, cookies=cookies, json=request_body)
        except requests.exceptions.ConnectionError as e:
            print("*ConnectionError*")
            print(e)
            return False
        self.csrf_cookie = response.cookies.get('csrftoken')
        self.hasSession = True
        return True


    def close(self):
        if self.multi:
            headers = {"X-CSRFToken": self.csrf_cookie, "Referer":self.post_url,}
            self.session.post(self.post_url+"account/api-logout/",headers=headers)

                
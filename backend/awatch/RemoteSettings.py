'''
Created on 2025/05/25

@author: kuyamakazuhiro
'''
import abc
import os

import csv
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo
import requests
from http import HTTPStatus
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError

from .HttpSession import HttpSession


# Webサーバーと通信を行い設定情報を取得するためのクラス
class RemoteSettings(HttpSession):
    def __init__(self, post_url, user_name, password, multi):
        super().__init__(post_url, user_name, password, multi)

    def get_settings(self, config_target, kind):
        # Webサーバーと通信を行い設定情報を取得する。
        # 設定情報の種別はkindとして与えられる。例えば "audio"だったらaudio関係の設定
        # 併せて、このデーモンのプロセスIDをWebサーバに渡す。これは、Webサーバ側で
        # 設定が変更になった場合に、シグナルを送り,デーモンを再起動するために使われる。
        data = None
        pid = os.getpid()
        try:
            response = self.session.get(config_target, params={'file':kind, 'process_id':pid})
            data = response.json()
        except requests.exceptions.ConnectionError:
                print("ConnectinError")
        except requests.exceptions.HTTPError as e:
            print("HttpError")
            print(e)
        return data

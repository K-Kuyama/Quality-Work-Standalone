'''
Created on 2025/05/25

@author: kuyamakazuhiro
'''

import os
import logging
import requests

from .HttpSession import HttpSession

logger = logging.getLogger(f"QualityWork.{__name__}")

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
        except requests.exceptions.ConnectionError as e:
                logger.error("ConnectinError")
                logger.error(e)
        except requests.exceptions.HTTPError as e:
            logger.error("HttpError")
            logger.error(e)
        return data

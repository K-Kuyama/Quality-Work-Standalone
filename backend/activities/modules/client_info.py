'''
Created on 2025/05/26

@author: kuyamakazuhiro
'''
import threading

class ClientInfo:
    # シングルトンクラス　デーモンプログラムから設定情報を要求された時に、デーモンプログラムのプロセスID
    # を保持しておくために使う。
    _instance = None
    _lock = threading.Lock()
    pid = None

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def setPid(self, pid):
        self.pid = pid



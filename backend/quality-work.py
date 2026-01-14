import os
import threading
import time
import signal
import pathlib
from awatch.aw_start import aw_start
from awatch.audio_watcher_start import audio_watcher_start
from qtserver import server_start
from bootstrap.bootstrap import bootstart
import configparser

def check_file(_handler):
    #audio_settings.jsonファイルの変化を監視。変更があった場合、与えられたハンドラーを呼び出す。
    CONFIG_FILE_PATH = 'media/audio_settings.json'
    cdir = os.path.dirname(os.path.abspath(__file__))
    #print(f"currend directory : {cdir}")
    target_file = os.path.join(cdir, CONFIG_FILE_PATH) 
    print(f"------start checking the file: {target_file} -------")
    p = pathlib.Path(target_file)
    st = p.stat()
    time_stamp = st.st_mtime
    while True:
        time.sleep(2)
        #print(f"->{p.stat().st_mtime}<-")
        current_time_stamp = p.stat().st_mtime
        if time_stamp != current_time_stamp:
            time_stamp = current_time_stamp
            _handler()

def handler(signum, frame):
    print("Quit programs.")
    raise KeyboardInterrupt
    sys.exit()
    
#def term_handler(signum, frame):
def term_handler():
    # SIGTERMを受け取った場合にaudio_watcherを再起動する。
    global auw
    print("restart audio_watcher.")
    stop_event.set()
    auw.join()        # ← 完全停止を待つ
    stop_event.clear()
    #time.sleep(5)
    auw = threading.Thread(target=audio_watcher_start, args=(stop_event,), daemon=False)
    auw.start()
    
    
CONFIG_FILE = 'config.ini'
EV_PRODUCER_CLASS = "HttpEventProducerLocal"
print("------start-----")
if os.path.exists(CONFIG_FILE):
    config_ini = configparser.ConfigParser()
    config_ini.read(CONFIG_FILE, encoding='utf-8')
    try:
        EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
    except (configparser.NoSectionError,configparser.NoOptionError):
        print("EventProducer not defined")          

signal.signal(signal.SIGINT, handler)
#signal.signal(signal.SIGTERM, term_handler)

# データベースファイルのチェック
# 初回はマイグレーションを行う
bootstart()

# Webサーバーのスタート
if EV_PRODUCER_CLASS == "HttpEventProducerLocal":
    #os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"backend"))
    qts = threading.Thread(target=server_start, daemon=False)
    qts.start()
    
# ファイルチェック
fc = threading.Thread(target=check_file, args=(term_handler,), daemon=False)
fc.start()

time.sleep(5)
#オーディオデーモンのスタート
# スレッドにイベントオブジェクトを設定する
print("------Audio watcher start-----")
stop_event = threading.Event()
auw = threading.Thread(target=audio_watcher_start, args=(stop_event,), daemon=False)
auw.start()

#ウインドウイベントデーモンのスタート
print("------Active window watcher start-----")
aw = threading.Thread(target=aw_start, daemon=False)
aw_start()

#time.sleep(2)
    
#while True:
#	time.sleep(1)
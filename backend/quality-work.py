import os
import threading
import time
import signal
import pathlib
import pystray
from PIL import Image

from awatch.aw_start import aw_start
from awatch.audio_watcher_start import audio_watcher_start
from qtserver import server_start
from bootstrap.bootstrap import bootstart
#from bootstrap.QwMenu import QwMenu, run_menu
import configparser

'''
audio_settings.jsonファイルの監視関連機能
'''
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
    stop_event_au.set()
    auw.join()        # ← 完全停止を待つ
    stop_event_au.clear()
    #time.sleep(5)
    auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), daemon=True)
    auw.start()
    

'''
システムトレイメニューからの操作関連機能
'''

# 収集デーモンの稼働状態を管理するフラグ
is_running = True

def stop_running():
    print("stop runnning")
    # データを収集しているデーモンを停止(終了)する
    global auw, aw
    # オーディオイベント収集の停止
    if 'auw' in globals() and auw.is_alive():
        stop_event_au.set()
        auw.join()
        print("-> audio daemon stopped")

    # ウインドウイベントの収集停止
    if 'aw' in globals() and aw.is_alive():
        stop_event_w.set()
        aw.join()
        print("-> window daemon stopped")

def start_running():
    global auw,aw
    print("start runnning")
    # イベントをクリア（セットされたままだと即終了してしまうため）
    stop_event_au.clear()
    stop_event_w.clear()
    # データを収集しているデーモンを起動する
    auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), daemon=True)
    auw.start()
    aw = threading.Thread(target=aw_start, args=(stop_event_w,), daemon=True)
    aw.start()


def toggle_action(icon, item):
    # メニューのボタンから呼ばれるアクション
    print("toggle_action")
    global is_running
    print(f"state : {is_running}")
    #　状態を反転する
    is_running = not is_running

    if is_running:
        start_running()
    else:
        stop_running()

def stop_all(icon, item):
    stop_running()
    icon.stop()



def run_menu():
    # --- アイコンとメニューの作成 ---
    # 16x16 or 32x32のアイコン画像（icon.png）を読み込み
    image = Image.open("QW3.png")

    menu = pystray.Menu(
        pystray.MenuItem(
            lambda item: f"ステータス: {'実行中' if is_running else '停止中'}",
            lambda icon, item: None, enabled=False
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            lambda item: "停止する" if is_running else "開始する",
            toggle_action
        ),
        pystray.MenuItem("終了", stop_all)
        #pystray.MenuItem("終了", lambda icon, item: icon.stop())
    )

    icon = pystray.Icon("QualityWork", image, "Quality-Work", menu)

    # --- Mac用のテンプレート設定ハック ---
    def setup_template(icon):
        # pystrayが内部で作成したmacOS用オブジェクトにアクセス
        # icon._main_thread_notifier はMac版pystrayの内部構造
        try:
            # アイコンが実際にメニューバーに表示されるまでわずかに待機
            import time
            time.sleep(0.5)
            # pystray内部のNSImageを取得してテンプレート設定
            icon._icon.setTemplate_(True)
        except Exception as e:
            print(f"Template setup failed: {e}")

    # 別スレッドで設定を実行（icon.runがブロックするため）
    threading.Thread(target=setup_template, args=(icon,), daemon=True).start()

    # macOS専用のハック：テンプレートイメージとしてマークする
    # if hasattr(icon, '_icon'): # 内部的なNSImageオブジェクトが存在する場合
    #    icon._icon.setTemplate_(True)

    icon.run()


'''
ここからメインプログラム
'''


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


# ローカルで動くdjangoアプリケーションが設定ファイルを変更した際に
# 送ってくるシグナルを受け取る
signal.signal(signal.SIGINT, handler)
#signal.signal(signal.SIGTERM, term_handler)

# データベースファイルのチェック
# 初回はマイグレーションを行う
bootstart()

# Webサーバーのスタート
if EV_PRODUCER_CLASS == "HttpEventProducerLocal":
    #os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),"backend"))
    qts = threading.Thread(target=server_start, daemon=True)
    qts.start()
    
# ファイルチェック
fc = threading.Thread(target=check_file, args=(term_handler,), daemon=True)
fc.start()

time.sleep(5)
#オーディオデーモンのスタート
# スレッドにイベントオブジェクトを設定する
print("------Audio watcher start-----")
stop_event_au = threading.Event()
auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), daemon=True)
auw.start()

#ウインドウイベントデーモンのスタート
print("------Active window watcher start-----")
stop_event_w = threading.Event()
aw = threading.Thread(target=aw_start, args=(stop_event_w,), daemon=True)
aw.start()


#QwMenu("Quality Work", icon="QWicon_template.png").run()
run_menu()

#time.sleep(2)
    
#while True:
#	time.sleep(1)
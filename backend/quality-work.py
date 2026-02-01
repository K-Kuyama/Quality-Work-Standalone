import os
import sys
import webbrowser
import threading
import time
import signal
from pathlib import Path
import logging
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
    p = Path(target_file)
    st = p.stat()
    time_stamp = st.st_mtime
    while True:
        time.sleep(2)
        #print(f"->{p.stat().st_mtime}<-")
        current_time_stamp = p.stat().st_mtime
        if time_stamp != current_time_stamp:
            time_stamp = current_time_stamp
            _handler()

'''
シグナルハンドラー
'''

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
ログ出力設定機能
'''
def setup_logger():
    # 1. 出力先ディレクトリの決定
    if getattr(sys, 'frozen', False):
        # PyInstallerで実行されている場合
        if sys.platform == "darwin":
            log_dir = Path.home() / "Library/Application Support/Quality-Work/logs"
        elif sys.platform == "win32":
            log_dir = Path(os.getenv("APPDATA")) / "Quality-Work/logs"
    else:
        # 通常のスクリプト実行の場合
        base_dir = Path(__file__).parent
        log_dir = base_dir / "logs"

    # 2. フォルダが存在しない場合は作成
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file_path = log_dir / "daemon.log"

    # 3. ロガーの設定
    logger = logging.getLogger("QualityWork")
    logger.setLevel(logging.DEBUG)

    # 4. ハンドラーの作成（ファイル出力）
    #file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    # 毎日(midnight)に切り替え、7日分保存する
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file_path,
        when="midnight",
        interval=1,
        backupCount=7,
        encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 5. ロガーにハンドラーを追加
    if not logger.handlers:
        logger.addHandler(file_handler)
        
        # コンソールにも出力したい場合は以下の2行を追加
        # console_handler = logging.StreamHandler()
        # logger.addHandler(console_handler)

    return logger


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

def open_browser(icon, item):
    webbrowser.open("http://localhost:8000/dashboard")

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



def get_icon_file():
    
    # PyInstallerで同梱されたリソースの実体パスを返す
    if getattr(sys, "frozen", False):
        # PyInstaller 実行時
        base_path = Path(sys._MEIPASS)
    else:
        # その他
        #base_path = Path(__file__).resolve().parent.parent
        base_path = Path(__file__).parent
    if sys.platform == "darwin":
        file_name = "QW3.png"
    else:
        file_name = "QTicon_S.ico"
    return base_path / file_name


def run_menu():
    # --- アイコンとメニューの作成 ---
    # 16x16 or 32x32のアイコン画像（icon.png）を読み込み
    
    
    #image = Image.open("QTicon_S.ico")
    #if sys.platform == "darwin":
    #    image = Image.open("QW3.png")
    image = Image.open(get_icon_file())

    menu = pystray.Menu(

        pystray.MenuItem(
            lambda item: f"ステータス: {'実行中' if is_running else '停止中'}",
            lambda icon, item: None, enabled=False
        ),

        pystray.MenuItem(
            lambda item: "停止する" if is_running else "開始する",
            toggle_action
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("ダッシュボードを開く", open_browser, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("終了", stop_all)
        #pystray.MenuItem("終了", lambda icon, item: icon.stop())
    )

    icon = pystray.Icon("QualityWork", image, "Quality-Work", menu,
                        # Windowsの左クリック用。Macでは設定しても無害（無視されるだけ）。
                        default_action=open_browser)

    icon.run()


'''
ここからメインプログラム
'''


CONFIG_FILE = 'config.ini'
EV_PRODUCER_CLASS = "HttpEventProducerLocal"

#ロガーを取得する
logger = setup_logger()

logger.info("------Quality-Work start-----")
if os.path.exists(CONFIG_FILE):
    config_ini = configparser.ConfigParser()
    config_ini.read(CONFIG_FILE, encoding='utf-8')
    try:
        EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
    except (configparser.NoSectionError,configparser.NoOptionError):
        logger.warning("EventProducer not defined")          


# ローカルで動くdjangoアプリケーションが設定ファイルを変更した際に
# 送ってくるシグナルを受け取る
signal.signal(signal.SIGINT, handler)
#signal.signal(signal.SIGTERM, term_handler)

# データベースファイルのチェック
# 初回はマイグレーションを行う
bootstart()

# Webサーバーのスタート
if EV_PRODUCER_CLASS == "HttpEventProducerLocal":
    qts = threading.Thread(target=server_start, daemon=True)
    qts.start()
    
# ファイルチェック用デーモンのスタート
fc = threading.Thread(target=check_file, args=(term_handler,), daemon=True)
fc.start()

#　Web Serverが立ち上がるのを待つため、5秒スリープ
time.sleep(5)

# オーディオデーモンのスタート
# スレッドにイベントオブジェクトを設定する
logger.info("------Audio watcher start-----")
stop_event_au = threading.Event()
auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), daemon=True)
auw.start()

#ウインドウイベントデーモンのスタート
logger.info("------Active window watcher start-----")
stop_event_w = threading.Event()
aw = threading.Thread(target=aw_start, args=(stop_event_w,), daemon=True)
aw.start()

# トレイメニューの表示
run_menu()


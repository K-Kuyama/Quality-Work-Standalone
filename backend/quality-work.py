import os
import sys
import webbrowser
import threading
import time
import signal
from pathlib import Path
import logging
import pystray
from PIL import Image, ImageOps

from awatch.aw_start import aw_start
from awatch.audio_watcher_start import audio_watcher_start
from qtserver import server_start
from bootstrap.bootstrap import bootstart
#from bootstrap.MsixMigrator import migrate_msix_data
from bootstrap.SplashScreen import show_splash_screen
from bootstrap.GetServerPort import get_server_port
from system.utils import get_app_dir
import configparser

if sys.platform == "win32":
    from bootstrap.MsixMigrator import migrate_msix_data
elif sys.platform == "darwin":
    import AppKit
    import PyObjCTools.MachSignals

'''
audio_settings.jsonファイルの監視関連機能
'''
def check_file(_handler, port_num):
    # ユーザーディレクトリにあるaudio_settings.jsonファイルの変化を監視。
    # 変化があった場合に、与えられたハンドラーを呼び出す。
    CONFIG_FILE = 'audio_settings.json'
    target_file = get_app_dir() / "config" / CONFIG_FILE
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
            _handler(port_num)

'''
ハンドラー群
'''

def handler(signum, frame):
    # キーボードインターラプとがあった時の処理
    print("Quit programs.")
    raise KeyboardInterrupt
    sys.exit()

def sigterm_handler(*args):
    # OSからの終了要求(システム終了・ログアウト等)を受けて、
    # デーモンスレッドとCoreAudioリソース(集約デバイス/タップ)を解放してから、
    # トレイアイコンを止めてicon.run()のブロックを抜けさせる。
    print("SIGTERM received. Shutting down.")
    stop_running()
    if _tray_icon is not None:
        _tray_icon.stop()

    #os._exit(0)

    
def restart_audio_watcher_on_config_change(port_num):
    # audio_watcherを再起動する。
    # check_fileにハンドラーとして渡され、configファイルが変更された時に呼び出される。
    global auw
    print("restart audio_watcher.")
    stop_event_au.set()
    auw.join()        # ← 完全停止を待つ
    stop_event_au.clear()
    #time.sleep(5)
    auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), kwargs={"port":port_num}, daemon=True)
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
            log_dir = Path(os.environ.get("LOCALAPPDATA")) / "Quality-Work/logs"
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
システムトレイメニューから呼び出される関連機能
'''

# SIGTERMハンドラーからicon.stop()を呼べるようにするためのtrayアイコンへの参照
_tray_icon = None

# 収集デーモンの稼働状態を管理するフラグ
is_running = True

def stop_running():
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
    # データを収集するデーモンの再起動
    global auw,aw
    # イベントをクリア（セットされたままだと即終了してしまうため）
    stop_event_au.clear()
    stop_event_w.clear()
    # データを収集しているデーモンを起動する
    auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), daemon=True)
    auw.start()
    aw = threading.Thread(target=aw_start, args=(stop_event_w,), daemon=True)
    aw.start()


def open_browser(icon, item, port):
    #デフォルトブラウザにダッシュボード画面を表示する
    webbrowser.open(f"http://127.0.0.1:{port}/dashboard")


def toggle_action(icon, item):
    # メニューのボタンから呼ばれるアクション
    # is_running == Trueの場合 : デーモンを停止する
    #               Falseの場合: デーモンを起動する
    global is_running
    #　状態を反転する
    is_running = not is_running

    if is_running:
        start_running()
    else:
        stop_running()

def stop_all(icon, item):
    # プログラムを終了する
    stop_running()
    icon.stop()

if sys.platform == "darwin":
    class _MacTerminationDelegate(AppKit.NSObject):
        '''
        macOSのシステム終了/ログアウト時にOSが送ってくる終了リクエスト
        (Apple Event経由のNSApplication -terminate:)を受け取るデリゲート。
        ここでデーモンスレッド停止とCoreAudio
        リソース(集約デバイス/タップ)の解放を行ってからNSTerminateNowを返す。
        '''
        def applicationShouldTerminate_(self, sender):
            print("applicationShouldTerminate_: system quit request received.")
            stop_running()
            if _tray_icon is not None:
                _tray_icon.stop()
            #os._exit(0)
            return AppKit.NSTerminateNow

    _app_delegate = None

    def install_mac_termination_delegate():
        print("installing terminataion delegate.")
        global _app_delegate
        _app_delegate = _MacTerminationDelegate.alloc().init()
        AppKit.NSApplication.sharedApplication().setDelegate_(_app_delegate)


def get_icon_file():
    # PyInstallerで同梱されたリソースの実体パスを返す
    # macOSでは、ファイル名に Template という文字列が含まれていると、それを「色の反転を制御すべき特殊な画像」だと判断。
    # 高精細ディスプレイ環境であれば、OSやライブラリが自動的に QWTemplate@2x.png を探しに行ってくれる。
    
    if getattr(sys, "frozen", False):
        # PyInstaller 実行時
        base_path = Path(sys._MEIPASS)
    else:
        # その他
        #base_path = Path(__file__).resolve().parent.parent
        base_path = Path(__file__).parent
    if sys.platform == "darwin":
        file_name = "QWTemplate.png"
    else:
        file_name = "QW.ico"
    return base_path / file_name


def get_tinted_icon(path, color="#555555"):
    # 透過PNGのフォアグラウンド色を指定した色に変更する
    image = Image.open(path).convert("RGBA")
    # アルファチャネル（透明度）を分離
    alpha = image.getchannel('A')
    # 新しい色の画像を作成し、元の透明度を適用する
    new_image = Image.new("RGBA", image.size, color)
    new_image.putalpha(alpha)
    return new_image

def run_menu(port=9416):
    # pystrayを使ってスシステムトレイにメニューを表示する

    # 1. アイコン画像を読み込む
    image_file = get_icon_file()
    if sys.platform == "darwin":
        image = get_tinted_icon(image_file, color="#FFFFFF")
    else:
        image = Image.open(image_file)
    # 2. メニューを構成する
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
        #pystray.MenuItem("ダッシュボードを開く", open_browser, default=True),
        pystray.MenuItem("ダッシュボードを開く", lambda icon, item: open_browser(icon, item, port), default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("終了", stop_all)
        #pystray.MenuItem("終了", lambda icon, item: icon.stop())
    )

    # 3. iconを生成しメニューと紐付ける
    #   MacOSではアイコンクリックでメニュー表示
    #   Windowsではアイコンクリックでdefault_actionのブラウザ表示を実行
    #             右クリックでメニュー表示

    icon = pystray.Icon("QualityWork",
                        image,
                        "Quality-Work", menu,
                        # Windowsの左クリック用。Macでは設定しても無害（無視されるだけ）。
                        default_action=open_browser)

    global _tray_icon
    _tray_icon = icon

    if sys.platform == "darwin":
        install_mac_termination_delegate()
        
    icon.run()


'''
ここからメインプログラム
'''
if __name__ == "__main__":

    import multiprocessing
    
    # Windows/PyInstaller環境での無限起動を防ぐ必須の1行
    multiprocessing.freeze_support()

    CONFIG_FILE = 'config.ini'
    EV_PRODUCER_CLASS = "HttpEventProducerLocal"

    CURRENT_VERSION = "3.6.1" #スプラッシュ画面に表示されるバージョン番号
    CURRENT_SCHEMA_VERSION = 3

    # 1.Splashウインドウの表示
    show_splash_screen(CURRENT_VERSION, duration_ms=3000)
    
    # Windows StoreerotSからダウンロードしたVer3.5のMSIIXからの移行
    if sys.platform == "win32":
        migrate_msix_data()

    # 2.ロガーをセットし取得する
    logger = setup_logger()

    logger.info("------Quality-Work start-----")
    if os.path.exists(CONFIG_FILE):
        config_ini = configparser.ConfigParser()
        config_ini.read(CONFIG_FILE, encoding='utf-8')
        try:
            EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("EventProducer not defined")          

    # 3.シグナルハンドラーを設定
    signal.signal(signal.SIGINT, handler)
    #signal.signal(signal.SIGTERM, term_handler)

    if sys.platform == "darwin":
        PyObjCTools.MachSignals.signal(signal.SIGTERM, sigterm_handler)
    else:
        signal.signal(signal.SIGTERM, sigterm_handler)

    # 4.macOSのアクセシビリティ権限が設定されていなければ、これを要求
    if sys.platform == "darwin":
        from Foundation import NSRunLoop, NSDate
        from awatch.window_info_for_mac import request_accessibility_permission, is_accessibility_trusted
        request_accessibility_permission()

        # アクセシビリティ許可が確定する(または一定時間経過する)まで待ってから後続のデーモン起動に進む。
        # macOSのTCCは、1つの許可ダイアログに応答待ちの間に別の許可要求が来た場合、
        # それを黙って無視する（後で自動的に出し直したりはしない）ので、これを防止する。
        ACCESSIBILITY_WAIT_TIMEOUT_SEC = 60
        waited_sec = 0
        while not is_accessibility_trusted() and waited_sec < ACCESSIBILITY_WAIT_TIMEOUT_SEC:
            #time.sleep(1)
            NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(1.0))
            waited_sec += 1
            logger.debug(f"{waited_sec}:{is_accessibility_trusted()}")
    
    # 5.データベースファイルのチェック
    #   初回はマイグレーションを行う
    bootstart(CURRENT_SCHEMA_VERSION)

    # ポート番号を取得
    port_num = get_server_port()

    # Webサーバーのスタート
    if EV_PRODUCER_CLASS == "HttpEventProducerLocal":
        try:
            qts = threading.Thread(target=server_start, args=(port_num,), daemon=True)
            qts.start()
        except Exception as e:
            logger.debug(f"exception : {e}")
        
    # ファイルチェック用デーモンのスタート
    try:
        fc = threading.Thread(target=check_file, args=(restart_audio_watcher_on_config_change,port_num,), daemon=True)
        fc.start()
    except Exception as e:
        logger.debug(f"exception : {e}")

    #　Web Serverが立ち上がるのを待つため、5秒スリープ
    time.sleep(5)

    # オーディオデーモンのスタート
    # スレッドにイベントオブジェクトを設定する
    logger.info("------Audio watcher start-----")
    try:
        stop_event_au = threading.Event()
        auw = threading.Thread(target=audio_watcher_start, args=(stop_event_au,), kwargs={"port":port_num}, daemon=True)
        auw.start()
    except Exception as e:
        logger.debug(f"exception : {e}")

    #ウインドウイベントデーモンのスタート
    logger.info("------Active window watcher start-----")
    try:
        stop_event_w = threading.Event()
        aw = threading.Thread(target=aw_start, args=(stop_event_w,), kwargs={"port":port_num}, daemon=True)
        aw.start()
    except Exception as e:
        logger.debug(f"exception : {e}")

    # トレイメニューの表示
    run_menu(port_num)


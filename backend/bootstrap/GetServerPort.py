import json
import os
import socket
import sys
import multiprocessing
import logging
from tkinter import messagebox, simpledialog, Tk
from system.utils import get_app_dir

CONFIG_FILE = os.path.join(get_app_dir(), "my_app_config.json")
DEFAULT_PORT = 9416
logger = logging.getLogger(f"QualityWork.{__name__}")


# ==========================================
# 1. 設定の読み込み・保存ロジック
# ==========================================
def load_port():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return config.get("port", DEFAULT_PORT)
        except Exception:
            return DEFAULT_PORT
    return DEFAULT_PORT

def save_port(port):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"port": port}, f)
    except Exception as e:
        logger.warning(f"設定の保存に失敗しました: {e}")

# ==========================================
# 2. ポップアップGUI（Tkinter）
# ==========================================

def _ask_new_port_worker(current_port, return_dict):
    """ポートが衝突したときに新しいポートをユーザーに尋ねる"""
    # Tkinterのルートウィンドウを非表示で作成（ポップアップだけ出すため）
    root = Tk()
    root.withdraw()
    root.lift()
    root.attributes("-topmost", True)
    root.focus_force()
    
    #  ダイアログの位置を画面の指定座標に強制移動する関数
    def move_dialog():
        from tkinter import Toplevel

        try:
            # 画面全体のサイズを取得して、少しずらした位置を計算
            # 例: 画面中央から少し右下にずらしたい場合
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # 💡 ここで出現位置（座標）を指定します
            # 例として、画面の「左上から数えて X=600, Y=500」の位置にする場合
            # (スプラッシュスクリーン（246x300）が画面中央にあるなら、そこから外れる数値を指定します)
            new_x = (screen_width // 2) + 150  # 画面中央から右に150px
            new_y = (screen_height // 2) + 100  # 画面中央から下に100px

            # rootに属する子ウィンドウ（ダイアログの実体）を探して位置を上書き
            for child in root.winfo_children():
                if isinstance(child, Toplevel):
                    child.geometry(f"+{new_x}+{new_y}")
                    break
        except Exception:
            pass

    # 💡 ダイアログが開く「30ミリ秒後」に位置変更を実行するよう予約
    root.after(30, move_dialog)

    # ユーザーに入力を促す（デフォルト値として現在のポート+1などを提案しても良い）
    new_port = simpledialog.askinteger(
        "Quality-Work : ポート競合",
        f"ポート {current_port} 番は既に他のアプリケーションで使用されています。\n\n使用する新しいポート番号（1024-65535）を入力してください:",
        initialvalue=current_port + 1,
        minvalue=1024,
        maxvalue=65535,
        parent=root
    )

    root.destroy()
    
    # 親プロセスに値を返す
    return_dict["chosen_port"] = new_port

def ask_new_port(current_port):
    """メインから呼び出すラッパー関数"""
    # プロセス間でデータをやり取りするための辞書
    manager = multiprocessing.Manager()
    return_dict = manager.dict()

    # 子プロセスを生成して起動
    p = multiprocessing.Process(
        target=_ask_new_port_worker, args=(current_port, return_dict)
    )
    p.start()
    p.join()  # ポップアップが閉じるまで、メインプログラムはここで待機する

    return return_dict.get("chosen_port")
        
# ==========================================
# 3. portの利用状況チェック
# ==========================================

def check_port(port):
    given_port = port
    finalized_port = None
    while True:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # 実際にbindしてみて競合をチェック
            temp_socket.bind(("127.0.0.1", given_port))
            temp_socket.close()
            # bindに成功したらこのポートで確定
            finalized_port = given_port
            break
        except OSError:
            # 競合発生：ソケットを閉じてユーザーに入力を求める
            temp_socket.close()
            new_port = ask_new_port(given_port)
            if new_port is None:
                logger.warning("ポート選択がキャンセルされたため、終了します。")
                sys.exit(0)

            given_port = new_port
            # 新しいポートを保存
            save_port(given_port)  
    return finalized_port


# ==========================================
# 4. メイン関数
# ==========================================

def get_server_port():
    #保存されているポートを読み込む。保存されていなければデフォルトポートになる。
    port = load_port()
    new_port = check_port(port)
    return new_port


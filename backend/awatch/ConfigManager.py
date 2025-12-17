from pathlib import Path
from configobj import ConfigObj
from io import StringIO
import sys

class ConfigManager:
    # 設定ファイル管理クラス

    DEFAULT_CONFIG = """
[DEFAULT]
# ウインドウ情報の取得間隔(秒)
Poll_time = 1

# タイムゾーン
Time_zone = Asia/Tokyo

#取得したイベントをどこに出力するかを設定
#   HttpEventProducerLocal : ローカルにあるHTTPサーバ
#   HttpEventProducer : リモートのHTTPサーバ
#   FileEventProducer : ローカルファイル(csv形式で) 
Ev_producer_class = HttpEventProducer

# Http出力の場合の送信先URL
Post_url = http://localhost/qt/

# サーバー認証のためのユーザ名、パスワード
User_name =
Password =

# ファイル出力の場合の出力先とエンコーディング
Data_file_path = ./data/
Encoding = utf-8

# ファイル出力先を切り替えるタイミング
#   day : 一日単位
#   week : 週単位
#   month : 月単位
File_rotate = day

[Audio]
# Audio設定をどこから読み込むかを指定
# local: このファイルから読み込み
# remote: httpサーバーから読み込み
AUDIO_CONFIG_SOURCE = local 

AUDIO_CONFIG_TARGET = config.ini
AUDIO_FILE_PREFIX = audio-
Poll_time = 0.2
Loop_back_device = BlackHole
Host_api = Core Audio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
Silence_threshold = 10
Start_frame_threshold = 10
End_frame_threshold = 50

#送信リトライ間隔(Poll_time x RETRY_INTERVAL 秒)
RETRY_INTERVAL = 50
"""


    DEFAULT_CONFIG_WIN = """
[DEFAULT]
# ウインドウ情報の取得間隔(秒)
Poll_time = 1

# タイムゾーン
Time_zone = Asia/Tokyo

#取得したイベントをどこに出力するかを設定
#   HttpEventProducerLocal : ローカルにあるHTTPサーバ
#   HttpEventProducer : リモートのHTTPサーバ
#   FileEventProducer : ローカルファイル(csv形式で) 
Ev_producer_class = HttpEventProducer

# Http出力の場合の送信先URL
Post_url = http://localhost/qt/

# サーバー認証のためのユーザ名、パスワード
User_name =
Password =

# ファイル出力の場合の出力先とエンコーディング
Data_file_path = ./data/
Encoding = utf-8

# ファイル出力先を切り替えるタイミング
#   day : 一日単位
#   week : 週単位
#   month : 月単位
File_rotate = day

[Audio]
# Audio設定をどこから読み込むかを指定
# local: このファイルから読み込み
# remote: httpサーバーから読み込み
AUDIO_CONFIG_SOURCE = local 

AUDIO_CONFIG_TARGET = config.ini
AUDIO_FILE_PREFIX = audio-
Poll_time = 0.2
Loop_back_device = VB-Audio
Host_api = Windows WASAPI
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK = 1024
Silence_threshold = 10
Start_frame_threshold = 10
End_frame_threshold = 50

#送信リトライ間隔(Poll_time x RETRY_INTERVAL 秒)
RETRY_INTERVAL = 50
"""

    

    def __init__(self):
        # ホームディレクトリ下の .qw ディレクトリ
        CONFIG_DIR = '.qw'
        CONFIG_FILE = 'config.ini'

        self.config_dir = Path.home() / CONFIG_DIR
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / CONFIG_FILE

        # Windowsの場合、定義ファイルの内容を変更
        if sys.platform == "win32":
            self.DEFAULT_CONFIG = self.DEFAULT_CONFIG_WIN


        # デフォルト設定
        self.default_config = ConfigObj(StringIO(self.DEFAULT_CONFIG))

        # 実際の設定
        if not self.config_file.exists():
            # 初回作成：テンプレート（コメント含む）をそのまま保存
            with open(self.config_file, "w", encoding="utf-8") as f:
                f.write(self.DEFAULT_CONFIG)

        self.config = ConfigObj(str(self.config_file), encoding="utf-8")

        # デフォルト値とのマージ
        self.merge_with_default()
        #self.save()

    # -----------------------------------
    # デフォルト設定とのマージ
    # -----------------------------------
    def merge_with_default(self):
        modified = False

        for section, values in self.default_config.items():

            # セクションがなければ追加
            if section not in self.config:
                self.config[section] = {}
                modified = True

            # 各キーをマージ
            for key, def_value in values.items():
                if key not in self.config[section]:
                    self.config[section][key] = def_value
                    modified = True

        if modified:
            self.save()

    # -----------------------------------
    # 保存
    # -----------------------------------
    def save(self):
        self.config.write()


    # -----------------------------------
    # 設定取得系
    # -----------------------------------

    def get(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)
    
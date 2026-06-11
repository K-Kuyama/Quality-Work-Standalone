import os
import time
import logging

from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from .AudioInfo import is_audio_active
from .WindowInfo import get_window_info
from .RemoteSettings import RemoteSettings

import configparser

from awatch.EventProducer import FileEventProducer, HttpEventProducer 
from awatch.ConfigManager import ConfigManager

logger = logging.getLogger(f"QualityWork.{__name__}")

# Audio Settings Class
class AudioSettings:

    def __init__(self):
        self.Start_frame_threshold = 10

    def get_settings_from_local(self):
        config_ini = ConfigManager()
        logger.info(f"get_settings_from_local: {config_ini}")
        if not config_ini:
            logger.warning(f"{config_ini} not exist")
            pass
        else:

            try:  
                self.Start_frame_threshold = int(config_ini.get('Audio','Start_frame_threshold'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                logger.warning("Start_frame_threshold not defined")
            try:  
                self.Poll_time = float(config_ini.get('Audio','Poll_time'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                logger.warning("Poll_time not defined")
            try:
                self.RETRY_INTERVAL = int(config_ini.get('Audio','RETRY_INTERVAL'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                logger.warning("RETRY_INTERVAL not defined")      


    def get_settings_from_remote(self, target_url, post_url, user_name, password, multi):
        logger.info(f"get_settings_from_remote: {target_url}")
        rm = RemoteSettings(post_url, user_name, password, multi)
        settings = rm.get_settings(target_url, "audio")
        for item in settings.items():
            setattr(self, item[0], item[1])


# Audio_activity_recorder
class AudioActivityRecorder:

    def __init__(self, timezone):
        self.start_time = None
        self.end_time = None
        self.window = None
        self.time_zone = timezone


    def start(self):
        logger.debug(f"start")
        self.start_time = datetime.now(ZoneInfo(self.time_zone))
        self.window = get_window_info()

    def commit_start(self):
        self.active = True
        logger.debug(f"start : {self.start_time}")
        logger.debug(f"  {self.window['app']} : {self.window['title']}")
    
    def end(self):
        logger.debug(f"end")
        self.end_time = datetime.now(ZoneInfo(self.time_zone))

    def cancel_start(self):
        self.window = None
        self.start_time = None

    def cancel_end(self):
        self.end_time = None

    def commit_end(self):
        logger.debug(f"end : {self.end_time}")
        self.active = False
        self.start_time = None
        self.end_time = None
        self.window = None

class RetryCounter:
# 送信に失敗した場合のリトライを管理するクラス

    def __init__(self, interval):
        CONFIG_FILE = 'config.ini'

        self.threshold = interval
        self.state = False
        self.count = 0


    def start(self):
        self.state = True
        self.count +=1

    def reset(self):
        self.state = False
        self.count = 0 

    def check(self):
        if self.state:
            if self.count > self.threshold:
                self.count = 0
                return True
            else:
                self.count += 1
                return False
        else:
            return False


def audio_watcher_start(stop_flag, stand_alone = False, port=8000):
    # stop_flagでイベントオブジェクトが渡される。

    # デフォルト設定
    CONFIG_FILE = 'config.ini'
    TIME_ZONE = "UTC"
    EV_PRODUCER_CLASS ="HttpEventProducerLocal"
    POST_URL = f"http://127.0.0.1:{port}/"
    USER_NAME = "root"
    PASSWORD = ""
    DATA_FILE_PATH = "./data/"
    ENCODING = "utf-8"
    FILE_ROTATE = None
    
    AUDIO_CONFIG_SOURCE = "remote"  # local または rmote
    #AUDIO_CONFIG_TARGET = "audio_conf.ini"
    AUDIO_CONFIG_TARGET = f"http://127.0.0.1:{port}/api/Activity/DaemonSettings/1/"
    
    AUDIO_FILE_PREFIX = "audio-"

    # デフォルト　オーディオ設定


    # silent_threshold以上の音声のレベルをStart_frame_threshold回連続で
    # 検知したらストリームが開始したと判定。

    Start_frame_threshold = 60

    Poll_time = 0.2


    '''
    設定ファイルからの読み込み処理
    
    ローカルサーバがなく、リモートのサーバーに情報をアップロードする場合は、
    stand_alone=trueが渡され、設定ファイルから定義が読み込まれる
    '''

    if stand_alone:
        config_ini = ConfigManager()
        try:
            EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("EventProducer not defined")      
        try:  
            POST_URL = config_ini.get('DEFAULT','Post_url')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("Podt_url not defined")
        try:
            USER_NAME = config_ini.get('DEFAULT','User_name')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("User_name not defined")
        try:
            PASSWORD = config_ini.get('DEFAULT','Password')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("Password not defined")
        try:
            DATA_FILE_PATH = config_ini.get('DEFAULT','Data_file_path')
            if DATA_FILE_PATH.startswith("./"):
                DATA_FILE_PATH = os.path.join(str(config_ini.config_dir), DATA_FILE_PATH.replace("./", ""))
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("Data_file_path not defined")
        try:
            ENCODING= config_ini.get('DEFAULT','Encoding')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("Encoding not defined")
        try:
            tstr = config_ini.get('DEFAULT','File_rotate')
            if tstr == "None":
                FILE_ROTATE = None
            else:
                FILE_ROTATE = config_ini.get('DEFAULT','File_rotate')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("File_rotate_pediod not defined")
        try:
            TIME_ZONE = config_ini.get('DEFAULT','Time_zone')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("Time_zone not defined")    

        try:  
            AUDIO_CONFIG_SOURCE = config_ini.get('Audio','AUDIO_CONFIG_SOURCE')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("AUDIO_CONFIG_SOURCE not defined")
        try:  
            AUDIO_CONFIG_TARGET = config_ini.get('Audio','AUDIO_CONFIG_TARGET')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("AUDIO_CONFIG_TARGET not defined")
        try:  
            AUDIO_FILE_PREFIX = config_ini.get('Audio','AUDIO_FILE_PREFIX')
        except (configparser.NoSectionError,configparser.NoOptionError):
            logger.warning("AUDIO_FILE_PREFIX not defined")
        
 
    aus = AudioSettings()
    if AUDIO_CONFIG_SOURCE=='remote':
        aus.get_settings_from_remote(AUDIO_CONFIG_TARGET, POST_URL, USER_NAME, PASSWORD, False)
    else:
        aus.get_settings_from_local()

        #rm = RemoteSettings(POST_URL, USER_NAME, PASSWORD, False)
        #settings = rm.get_settings(AUDIO_CONFIG_TARGET, AUDIO_CONFIG_SOURCE)


    # 音の変化を監視
    #silence_threshold = 100  # 無音と判断するしきい値
    active_frames = 0        # 音が継続しているフレーム数
    #frame_threshold = 5     # 連続10フレーム音が続いたら動画が再生中と判断
    recording_state = 0     # 初期状態:0、スタート判定中:1、レコード中:2、終了判定中:3
    recordig_flag = False
    starting_flag = False   # スタートしているか判定中の場合True
    ending_flag = False     # 終了しているか判定中の場合True

    start_time = None
    end_time = None
    Poll_time =aus.Poll_time

    ep = None
    if EV_PRODUCER_CLASS == "FileEventProducer":
        ep = FileEventProducer(DATA_FILE_PATH, ENCODING, FILE_ROTATE, TIME_ZONE, prefix=AUDIO_FILE_PREFIX)
    elif EV_PRODUCER_CLASS == "HttpEventProducer":
        ep = HttpEventProducer(POST_URL, TIME_ZONE, USER_NAME, PASSWORD, True)
    else:
        ep = HttpEventProducer(POST_URL, TIME_ZONE, USER_NAME, PASSWORD, False)

    ar = AudioActivityRecorder(TIME_ZONE)

    rc = RetryCounter(aus.RETRY_INTERVAL)

    try:
        while not stop_flag.is_set(): #stop_flagイベントがセットされるとループから抜ける
            time.sleep(Poll_time)

            if recording_state == 0:
                if is_audio_active():
                    ar.start()
                    recording_state = 1
                    active_frames += 1
                    rc.reset()
                else:
                    if rc.check() == True: #RetryCounterをチェックしてイベントを再送信するかどうかを判断する
                        ep.flushEvents()
                        if len(ep.request_pool) > 0: #送信失敗の場合、再度カウンターを0からスタート
                            rc.reset()
                            rc.start()
                        else: #送信成功の場合、カウンターリセット
                            rc.reset()
                continue
            if recording_state == 1:
                if is_audio_active():
                    if(active_frames > aus.Start_frame_threshold):
                        ar.commit_start()
                        recording_state = 2
                        active_frames = 0
                    else:
                        active_frames += 1
                else:
                    ar.cancel_start()
                    recording_state = 0
                    active_frames = 0
                continue
            if recording_state == 2:
                if not is_audio_active():
                    ar.end()
                    recording_state = 3
                    active_frames += 1
                continue
            if recording_state == 3:
                if not is_audio_active(): 
                    ep.createAudioActivityEvent(ar.window, ar.start_time, ar.end_time)
                    if len(ep.request_pool) > 0:
                        rc.start()
                    ar.commit_end()
                    active_frames = 0
                    recording_state = 0
                else:
                    ar.cancel_end()
                    recording_state  = 2
                    active_frames = 0
                continue
            else:
                pass

    except KeyboardInterrupt:
        logger.info("\n🎵 stop listning.")

    
    # 終了処理
    stop_flag.clear()  #イベントにセットされている値をクリアする

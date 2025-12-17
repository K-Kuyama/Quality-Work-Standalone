import os
import signal
import time
#import array

#import pyaudio
#import numpy as np

from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from .AudioInfo import is_audio_active
from .WindowInfo import get_window_info
from .RemoteSettings import RemoteSettings

import requests
import configparser

from awatch.EventProducer import FileEventProducer, HttpEventProducer 
from awatch.ConfigManager import ConfigManager

# Audio Settings Class
class AudioSettings:

    def __init__(self):
        '''
        self.Loop_back_device = "BlackHole"
        self.Host_api = "Core Audio"
        self.FORMAT = pyaudio.paInt16  # 16bit PCM
        self.CHANNELS = 1              # モノラル
        self.RATE = 44100              # サンプルレート (44.1kHz)
        self.CHUNK = 1024              # フレームサイズ
        # silent_threshold以上の音声のレベルをStart_frame_threshold回連続で
        # 検知したらストリームが開始したと判定。End_frame_threshold回連続で、
        # silent_threshold未満のレベルが続いたらストリームは終了したと判定。
        self.Silence_threshold = 100         
        self.Start_frame_threshold = 10
        self.End_frame_threshold = 30
        '''
        self.Start_frame_threshold = 10

        #if source == "remote":
        #    self.get_settings_from_remote(target)
        #else:
        #    self.get_settings_from_local(target)

    def get_settings_from_local(self):
        config_ini = ConfigManager()
        print(f"get_settings_from_local: {config_ini}")
        if not config_ini:
            print(f"{config_ini} not exist")
            pass
        else:
            #config_ini = configparser.ConfigParser()
            #config_ini.read(target, encoding='utf-8')
            '''
            try:  
                self.Loop_back_device = config_ini.get('Audio','Loop_back_device')
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("Loop_back_device not defined")
            try:  
                self.Host_api = config_ini.get('Audio','Host_api')
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("Host_api not defined")
            try:  
                self.FORMAT = eval(config_ini.get('Audio','FORMAT'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("FORMAT not defined")    
            try:  
                self.CHANNELS = int(config_ini.get('Audio','CHANNELS'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("CHANNELS not defined")
            try:  
                self.RATE = int(config_ini.get('Audio','RATE'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("RATE not defined")
            try:  
                self.CHUNK = int(config_ini.get('Audio','CHUNK'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("CHUNK not defined")
            try:  
                self.Silence_threshold = int(config_ini.get('Audio','Silence_threshold'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("Silence_threshold not defined")
            '''
            try:  
                self.Start_frame_threshold = int(config_ini.get('Audio','Start_frame_threshold'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("Start_frame_threshold not defined")
            '''
            try:  
                self.End_frame_threshold = int(config_ini.get('Audio','End_frame_threshold'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("End_frame_threshold not defined")
            '''
            try:  
                self.Poll_time = float(config_ini.get('Audio','Poll_time'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("Poll_time not defined")
            try:
                self.RETRY_INTERVAL = int(config_ini.get('Audio','RETRY_INTERVAL'))
            except (configparser.NoSectionError,configparser.NoOptionError):
                print("RETRY_INTERVAL not defined")      


    def get_settings_from_remote(self, target_url, post_url, user_name, password, multi):
        print(f"get_settings_from_remote: {target_url}")
        rm = RemoteSettings(post_url, user_name, password, multi)
        settings = rm.get_settings(target_url, "audio")
        for item in settings.items():
            setattr(self, item[0], item[1])
            #if item[0] == "FORMAT":
            #    setattr(self, item[0],eval(item[1]))
            #else:
            #    setattr(self, item[0], item[1])
        

# Audio_activity_recorder
class AudioActivityRecorder:

    def __init__(self, timezone):
        self.start_time = None
        self.end_time = None
        self.window = None
        self.time_zone = timezone


    def start(self):
        print(f"start")
        self.start_time = datetime.now(ZoneInfo(self.time_zone))
        self.window = get_window_info()

    def commit_start(self):
        self.active = True
        print(f"start : {self.start_time}")
        print(f"  {self.window['app']} : {self.window['title']}")
    
    def end(self):
        print(f"end")
        self.end_time = datetime.now(ZoneInfo(self.time_zone))

    def cancel_start(self):
        self.window = None
        self.start_time = None

    def cancel_end(self):
        self.end_time = None

    def commit_end(self):
        print(f"end : {self.end_time}")
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

        '''
        if not os.path.exists(CONFIG_FILE):
            pass
        else:
            config_ini = configparser.ConfigParser()
            config_ini.read(CONFIG_FILE, encoding='utf-8')
        try:
            self.threshold = int(config_ini.get('Audio','RETRY_COUNT'))
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("ENTRY_COUNT not defined")   
        '''   

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


def audio_watcher_start(stop_flag, stand_alone = False):
    # stop_flagでイベントオブジェクトが渡される。

    # デフォルト設定
    CONFIG_FILE = 'config.ini'
    TIME_ZONE = "UTC"
    EV_PRODUCER_CLASS ="HttpEventProducerLocal"
    POST_URL = "http://127.0.0.1:8000/"
    USER_NAME = "root"
    PASSWORD = ""
    DATA_FILE_PATH = "./data/"
    ENCODING = "utf-8"
    FILE_ROTATE = None
    
    AUDIO_CONFIG_SOURCE = "remote"  # local または rmote
    #AUDIO_CONFIG_TARGET = "audio_conf.ini"
    AUDIO_CONFIG_TARGET = "http://127.0.0.1:8000/api/Activity/DaemonSettings/1/"
    
    AUDIO_FILE_PREFIX = "audio-"

    # デフォルト　オーディオ設定
    '''
    Loop_back_device = "BlackHole"
    Host_api = "Core Audio"
    FORMAT = pyaudio.paInt16  # 16bit PCM
    CHANNELS = 1              # モノラル
    RATE = 44100              # サンプルレート (44.1kHz)
    CHUNK = 1024              # フレームサイズ
  

    # silent_threshold以上の音声のレベルをStart_frame_threshold回連続で
    # 検知したらストリームが開始したと判定。End_frame_threshold回連続で、
    # silent_threshold未満のレベルが続いたらストリームは終了したと判定。
    Silence_threshold = 100         
    Start_frame_threshold = 10
    End_frame_threshold = 30
    '''
    Start_frame_threshold = 60

    Poll_time = 0.2

#    if not os.path.exists(CONFIG_FILE):
#        print(f"{CONFIG_FILE} not exist")
#        pass
#    else:
#        config_ini = configparser.ConfigParser()
#        config_ini.read(CONFIG_FILE, encoding='utf-8')
    if stand_alone:
        config_ini = ConfigManager()
        try:
            EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("EventProducer not defined")      
        try:  
            POST_URL = config_ini.get('DEFAULT','Post_url')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Podt_url not defined")
        try:
            USER_NAME = config_ini.get('DEFAULT','User_name')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("User_name not defined")
        try:
            PASSWORD = config_ini.get('DEFAULT','Password')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Password not defined")
        try:
            DATA_FILE_PATH = config_ini.get('DEFAULT','Data_file_path')
            if DATA_FILE_PATH.startswith("./"):
                DATA_FILE_PATH = os.path.join(str(config_ini.config_dir), DATA_FILE_PATH.replace("./", ""))
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Data_file_path not defined")
        try:
            ENCODING= config_ini.get('DEFAULT','Encoding')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Encoding not defined")
        try:
            tstr = config_ini.get('DEFAULT','File_rotate')
            if tstr == "None":
                FILE_ROTATE = None
            else:
                FILE_ROTATE = config_ini.get('DEFAULT','File_rotate')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("File_rotate_pediod not defined")
        try:
            TIME_ZONE = config_ini.get('DEFAULT','Time_zone')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Time_zone not defined")    

        try:  
            AUDIO_CONFIG_SOURCE = config_ini.get('Audio','AUDIO_CONFIG_SOURCE')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("AUDIO_CONFIG_SOURCE not defined")
        try:  
            AUDIO_CONFIG_TARGET = config_ini.get('Audio','AUDIO_CONFIG_TARGET')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("AUDIO_CONFIG_TARGET not defined")
        try:  
            AUDIO_FILE_PREFIX = config_ini.get('Audio','AUDIO_FILE_PREFIX')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("AUDIO_FILE_PREFIX not defined")
        
 
    aus = AudioSettings()
    if AUDIO_CONFIG_SOURCE=='remote':
        aus.get_settings_from_remote(AUDIO_CONFIG_TARGET, POST_URL, USER_NAME, PASSWORD, False)
    else:
        aus.get_settings_from_local()

        #rm = RemoteSettings(POST_URL, USER_NAME, PASSWORD, False)
        #settings = rm.get_settings(AUDIO_CONFIG_TARGET, AUDIO_CONFIG_SOURCE)

    '''
    # PyAudio 初期化
    p = pyaudio.PyAudio()
    device_index = None

    print("------ Device list ------")
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if dev["maxInputChannels"] > 0:
            host_api_index = dev['hostApi']
            host_api_info = p.get_host_api_info_by_index(host_api_index)
            print(f"{dev['index']}:{dev['name']}:{dev['defaultSampleRate']}:{host_api_info['name']}")
    print("-------------------------")

    # ループバックデバイスを特定
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        host_api_info = p.get_host_api_info_by_index(dev['hostApi'])
        #if "BlackHole" in dev["name"] and dev["maxInputChannels"] > 0:
        #if "VB-Cable" in dev["name"] and dev["maxInputChannels"] > 0:
        if aus.Host_api in host_api_info["name"] and aus.Loop_back_device in dev["name"] and dev["maxInputChannels"] > 0:
            print(f"使用するデバイス: {dev['name']}")
            print(f"使用するAPI: {host_api_info['name']}")
            device_index = i        

    if device_index is None:
        print("Audio:デバイスが見つかりません。設定を見直してください。")
        stop_flag.wait()
        print("audio: release pyaudio resources.")
        stop_flag.clear() 
        p.terminate()
        return
        

    # 音声ストリームを開始
    print(f"使用するindex: {device_index} {type(device_index)}")
    print(f"使用するRATE: {aus.RATE} {type(aus.RATE)}")
    print(f"使用するFORMAT: {aus.FORMAT} {type(aus.FORMAT)}")
    print(f"使用するCHANNELS: {aus.CHANNELS} {type(aus.CHANNELS)}")
    print(f"使用するCHUNK: {aus.CHUNK} {type(aus.CHUNK)}")
    print(f"使用するSilence_threshold: {aus.Silence_threshold} {type(aus.Silence_threshold)}")
    print(f"使用するEnd_frame_threshold: {aus.End_frame_threshold} {type(aus.End_frame_threshold)}")
    print(f"使用するStart_frame_threshold: {aus.Start_frame_threshold} {type(aus.Start_frame_threshold)}")


    stream = None
    try:
        stream = p.open(format=aus.FORMAT, channels=aus.CHANNELS,
                        rate=aus.RATE, input=True, frames_per_buffer=aus.CHUNK,
                        input_device_index = device_index
        )
    except OSError as e:
        print(f"Can not open stream.: {e}")
        print("Audio:このデバイスは使えません。他のデバイスを設定してください")
        stop_flag.clear() 
        stop_flag.wait()
        print("audio: release all resources.")
        p.terminate()
        return
        
    #stream = p.open(format=pyaudio.paInt16, channels=1,
    #                rate=44100, input=True, frames_per_buffer=1024,
    #                input_device_index = 0
    #            )
    print("Start Listening")
    '''
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
            #data = array.array('h', stream.read(aus.CHUNK, exception_on_overflow=False))
            #volume = sum(abs(x) for x in data) / len(data)
            #data = np.frombuffer(stream.read(aus.CHUNK, exception_on_overflow=False), dtype=np.int16)
            #volume = np.abs(data).mean()  # 音量を取得
            #print(f"音量: {volume:.2f}")

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
        print("\n🎵 stop listning.")

    
    # 終了処理
    stop_flag.clear()  #イベントにセットされている値をクリアする
    '''
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("audio: release resources.")
    del p
    '''
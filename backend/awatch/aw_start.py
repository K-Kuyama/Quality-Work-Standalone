'''
Created on 2024/05/01

@author: kuyamakazuhiro
'''

import sys


#sys.path.append("/Applications/Eclipse_2021-03.app/Contents/ActiveWatch/ActiveWatchModification/aw-watcher-window")
#sys.path.append("/Users/kuyamakazuhiro/sources/ActiveWatch/ActiveWatchModification/aw-watcher-window")
#sys.path.append("/Users/kuyamakazuhiro/sources/ActiveWatch/ActiveWatchModification/aw-client")
import os
import signal
import time
import csv
import re
from pynput import keyboard, mouse
from datetime import timedelta, datetime, timezone
from zoneinfo import ZoneInfo
from .WindowInfo import get_window_info

#from aw_watcher_window.lib import get_current_window
import requests
import configparser

from awatch.EventProducer import FileEventProducer, HttpEventProducer 



class ActionRecorder:
    '''
    ウインドウがアクティブになっている間にに起きた、クリック、スクロール、キーインプットなどのアクションを監視し、
    回数や移動距離などをカウントし、情報として記録する。
    '''
        
    def __init__(self, timezone):
        self.drag_distance_x = 0
        self.drag_distance_y = 0
        self.prev_x = None
        self.prev_y = None
        self.clicks = 0
        self.strokes = 0
        self.scrolls = 0
        self.start_time = None
        self.check_input = False
        self.time_zone = timezone
        
    def start(self):
#        self.start_time = datetime.now(timezone.utc)
        self.start_time = datetime.now(ZoneInfo(self.time_zone))
        m_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll)
        m_listener.start()
        time.sleep(1)
        k_listener = keyboard.Listener(
            on_press=self.on_press)
        k_listener.start()              
 
    def reset(self):
        self.drag_distance_x = 0
        self.drag_distance_y = 0
        self.prev_x = None
        self.prev_y = None
        self.clicks = 0
        self.strokes = 0
        self.scrolls = 0
#        self.start_time = datetime.now(timezone.utc)
        self.start_time = datetime.now(ZoneInfo(self.time_zone))
        self.check_input = False
        
    def get_data(self):
        data =dict()
        data['distance_x'] = self.drag_distance_x
        data['distance_y'] = self.drag_distance_y
        data['clicks'] = self.clicks
        data['strokes'] = self.strokes
        data['scrolls'] = self.scrolls
        return data

    def resetInputFlag(self):
        self.check_input = False  

    def getInputFlag(self):
        return self.check_input
        
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.prev_x =x
            self.prev_y =y
        else:
            if self.prev_x:
                self.drag_distance_x += abs(x - self.prev_x)
                self.drag_distance_y += abs(y - self.prev_y)  
                self.clicks += 1
        self.check_input = True
#            print(f"distance {self.drag_distance_x} . {self.drag_distance_y}")
#            print(get_current_window("applescript"))


    def on_scroll(self, x, y, dx, dy):
        self.scrolls += 1
        self.check_input = True
#        print('Scrolled {0} at {1}'.format(
#            'down' if dy < 0 else 'up',
#            (x, y)))
  
        
    def on_press(self, key):
        if key not in (keyboard.Key.up, keyboard.Key.down, keyboard.Key.right, keyboard.Key.left):
            self.strokes += 1
            self.check_input = True

        
# def on_release(key):
#    print('{0} release'.format(
#        key))

class BlankPeriod:
    
    def __init__(self, timezone):
#        self.start_time = datetime.now(timezone.utc)
        self.start_time = datetime.now(ZoneInfo(timezone))
        self.comitted = False



def aw_start():
    '''
    メインプログラム。ウインドウ情報を取得し、前回のループで取得したものと比較。
    '''
    print("start application.")

    '''
    デフォルト値の設定。設定ファイルに定義がない場合、これが使われる。
    '''
    EV_PRODUCER_CLASS = "HttpEventProducerLocal"
    POST_URL = "http://127.0.0.1:8000/"
    USER_NAME = "root"
    PASSWORD = ""
    #POST_URL = "http://127.0.0.1:8000/api/Activity/"
    #POST_BULK_URL = "http://127.0.0.1:8000/api/Activity/bulk/"
    DATA_FILE_PATH = "./data/"
    ENCODING = "utf-8"
    FILE_ROTATE = None
    CONFIG_FILE = 'config.ini'
    TIME_ZONE = "UTC"

    '''
    設定ファイルからの読み込み処理
    '''
    if not os.path.exists(CONFIG_FILE):
        poll_time = 1
    else:
        config_ini = configparser.ConfigParser()
        config_ini.read(CONFIG_FILE, encoding='utf-8')
        try:  
            poll_time = int(config_ini.get('DEFAULT','Poll_time'))
        except (configparser.NoSectionError,configparser.NoOptionError):
            poll_time = 1
        try:
            TIME_ZONE = config_ini.get('DEFAULT','Time_zone')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Time_zone not defined")     
        try:
            EV_PRODUCER_CLASS = config_ini.get('DEFAULT','Ev_producer_class')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("EventProducer not defined")           
        try:
            POST_URL = config_ini.get('DEFAULT','Post_url')
        except (configparser.NoSectionError,configparser.NoOptionError):
            print("Post_url not defined")
        #try:
        #    POST_BULK_URL = config_ini.get('DEFAULT','Post_bulk_url')
        #except (configparser.NoSectionError,configparser.NoOptionError):
        #    print("Post_bulk_url not defined")
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
 
    print(f"poll_time= {poll_time}")     
    print(f"TIME_ZONE= {TIME_ZONE}")
    print(f"EV_PRODUCER_CLASS= {EV_PRODUCER_CLASS}")
    print(f"POST_URL= {POST_URL}")
    #print(f"POST_BULK_URL= {POST_BULK_URL}")
    print(f"DATA_FILE_PATH= {DATA_FILE_PATH}")
    print(f"ENCODING= {ENCODING}")
    print(f"FILE_ROTATE= {FILE_ROTATE}")


 

                
    last_window = None
    counter = 0
#assumed_start_time = None
    bp = None
    ep = None
    if EV_PRODUCER_CLASS == "FileEventProducer":
        ep = FileEventProducer(DATA_FILE_PATH, ENCODING, FILE_ROTATE, TIME_ZONE)
    elif EV_PRODUCER_CLASS == "HttpEventProducer":
        ep = HttpEventProducer(POST_URL, TIME_ZONE, USER_NAME, PASSWORD, True)
    else:
        ep = HttpEventProducer(POST_URL, TIME_ZONE, USER_NAME, PASSWORD, False)

    # 前回のループ実行時のUNIX時間
    prev_loop_time = None
    # 今回のループ実行時のUNIX時間
    current_loop_time = None

    if(len(sys.argv) >1):
        POST_URL = sys.argv[1]
    
    #def handler(signum, frame):
    #    print("Close file at this time.")
    #    ep.close()
    #    raise KeyboardInterrupt
    #    sys.exit()
    
    #signal.signal(signal.SIGINT, handler)

    window = None
    while True:
        #    print(counter)
        try:
            window = get_window_info()
            #window = get_current_window("applescript")
        except Exception as e:
            print(e)
            pass
        if not last_window :
            last_window = window
            ar = ActionRecorder(TIME_ZONE)
            ar.start()
        else :
            if not last_window == window:
                if last_window['app'] == window['app'] and window['title'] == "":
#                    print("No title event")
                    continue
                else :
                    if bp and bp.comitted:
                        ep.createBlankEvent(bp)
                        #print("Brank period end due to the window change.")
                    else :
                        ep.createEvent(ar, last_window, None)
                        #print(f"event : {last_window['app']}")
                    bp = None
                    #print("bp deleted due to window change.")
                    counter = 0
                    ar.reset()
                    last_window = window

            else :
                if ar.getInputFlag() :
                    ar.resetInputFlag()
                    counter = 0
                    if bp :
                        if bp.comitted :
                            ep.createBlankEvent(bp)
                            bp = None
                            #print("bp deleted due to send event by inputs.")
                            counter = 0
                            ar.reset()
                    bp = None
                    #print("bp deleted due to input")
                else :
                    if not bp :
                        bp = BlankPeriod(TIME_ZONE)
                        #print(f"BP start at {bp.start_time}")
                    counter += 1
                    if counter >= 180 and not bp.comitted:
                        ep.createEvent(ar, last_window, bp.start_time)
                        #print(f"event befor blank period : {last_window['app']}")
                        ar.reset()
                        bp.comitted = True
 
        # システムスリープがあった場合には、スリープ前のウインドウイベントと、スリープ時のブランクイベントを作成する。
        # スリープがあったかどうかを前回ループからの経過時間で判断
        if not current_loop_time :
            current_loop_time = time.time()
            prev_loop_time= current_loop_time
        else:
            prev_loop_time = current_loop_time
            current_loop_time = time.time()
        if (current_loop_time - prev_loop_time) >=60:
            #print(f"prev:{prev_loop_time}, current:{current_loop_time}")
            #print("create blank period by System sleep....")
            bp_st = datetime.fromtimestamp(prev_loop_time, tz=ZoneInfo(TIME_ZONE))
            #print(f"compaire ar - bp : {ar.start_time} - {bp_st}")
            if ar.start_time < bp_st :
                if bp:
                    #blankperiod は存在するが、System Sleep 後に作られたものである場合、Sleep前からのBlankperiodを作り直す
                    if bp.start_time > bp_st:
                        bp =BlankPeriod(TIME_ZONE)
                        bp.start_time=bp_st
                else:
                    bp =BlankPeriod(TIME_ZONE)
                    bp.start_time=bp_st
                #print(f"ar.start_time = {ar.start_time}, bp.start_time = {bp.start_time}")
                if(ar.start_time < bp.start_time):
                    ep.createEvent(ar, last_window, bp.start_time)
            #ep.createBlankEvent(bp)
            #print("Brank period end due to system sleep.")
            bp = None
            counter = 0
            ar.reset()


                    
#            print(f"{start_time}:{duration.seconds}:{event_data}")
        time.sleep(poll_time)
#        print("wait")
#        time.sleep(1)
        
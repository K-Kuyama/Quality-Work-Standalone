'''
Created on 2024/09/07

@author: kuyamakazuhiro
'''
import abc
import os

import csv
from datetime import timedelta, datetime, date
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo
import requests
from http import HTTPStatus
from http.client import RemoteDisconnected
from urllib3.exceptions import ProtocolError

class EventProducer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def createEvent(self, ar, last_window, end_time):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def createBlankEvent(self, bp):
        raise NotImplementedError()

    @abc.abstractmethod
    def close(self):
        raise NotImplementedError()

'''
アクティビティ情報（イベント）をHTTP POSTでサーバに出力する
''' 
    
class HttpEventProducer(EventProducer):
    def __init__(self, post_url, time_zone, user_name, password, multi):
        self.post_url = post_url
        self.request_pool =[]
        self.time_zone = time_zone
        self.user_name = user_name
        self.password = password
        self.multi = multi
        self.hasSession = False
        if self.multi:
            r = self.getSession()
            #print(f"initialize result {r}")
        else:
            self.session = requests.Session()

        
    def getSession(self):
        self.session = requests.Session()
        # csrfトークンを取得する
        try:
            response = requests.get(self.post_url+"account/csrf/")
        except requests.exceptions.ConnectionError as e:
            print("*ConnectionError*")
            print(e)
            return False
        #response = requests.get(self.post_url+"csrf/")
        self.csrf_cookie = response.cookies.get('csrftoken')
        self.csrf = response.headers['X-CSRFToken']

        # ログインして、サーバとセッションを確立する
        request_body ={'username': self.user_name, 'password': self.password}
        #CSRFの対策として、CSRFトークンとリファラーをヘッダにセットして送信
        headers = {"X-CSRFToken": self.csrf, "Referer":self.post_url,}
        cookies = {"csrftoken": self.csrf_cookie}
        try:
            response = self.session.post(self.post_url+"account/api-login/", headers=headers, cookies=cookies, json=request_body)
        except requests.exceptions.ConnectionError as e:
            print("*ConnectionError*")
            print(e)
            return False
        #response = self.session.post(self.post_url+"api-login/", headers=headers, cookies=cookies, json=request_body)
        #print(response.text)
        #print(response)
        self.csrf_cookie = response.cookies.get('csrftoken')
        self.hasSession = True
        return True


    def close(self):
        if self.multi:
            headers = {"X-CSRFToken": self.csrf_cookie, "Referer":self.post_url,}
            self.session.post(self.post_url+"account/api-logout/",headers=headers)
        #self.session.post(self.post_url+"api-logout/",headers=headers)
        

    def createEvent(self, ar, last_window, end_time):
        #ウィンドウ情報をサーバに送信
        event_data = ar.get_data()
        start_time = ar.start_time
        if end_time :
            if end_time >= start_time:
                duration = end_time - start_time
            else :
                #print(f"timedelta 0")
                duration = timedelta()
        else :
            duration = datetime.now(ZoneInfo(self.time_zone)) - start_time
        event_data['window'] = last_window
        # titleフィールドに入れる文字列長さは0<n<256でなければならない
        title_str = event_data['window']['title']
        if(len(title_str) > 0 ):
            if(len(title_str) > 256 ):
                title_str = title_str[:256]
        else:
            title_str ="NONE"

        request_body = {
            'start_time':start_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            'duration':duration.seconds,
            'distance_x':event_data['distance_x'],
            'distance_y':event_data['distance_y'],
            'strokes':event_data['strokes'],
            'scrolls':event_data['scrolls'],
            'app':event_data['window']['app'],
            'title':title_str,
            }
        print(f"request:{request_body}")
        self.sendEvent(request_body, "api/Activity/")


    def createAudioActivityEvent(self, window, start_time, end_time):
        #音声が使われていた期間の情報をAudioActivityイベントとしてサーバーに送信する。
        #windowは、音声が流れ始めた時にアクティブだったウインドウ

        duration = end_time - start_time

        title_str = window['title']
        if(len(title_str) > 0 ):
            if(len(title_str) > 256 ):
                title_str = title_str[:256]
        else:
            title_str ="NONE"

        request_body={
            'start_time':start_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            'end_time':end_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            'duration':duration.seconds,
            'start_app': window['app'],
            'start_title': title_str,
            'longest_app': None,
            'longest_title': None,
            'another_app': None,
            'another_title': None
        }
        print(request_body)
        self.sendEvent(request_body, "api/AudioActivity/CreateActivity/")


    def flushEvents(self):
        #request_poolにあるイベントをフラッシュする
        self.sendEvent(None, "api/AudioActivity/CreateActivity/")


    def sendEvent(self, request_body, local_path):
        # 最終的にPOSTリクエストをサーバーに送信する。送信先のURLは、self.post_url+local_urlで、
        # request_bodyを送信する。
        if self.multi:
            if (self.hasSession == False):
                if (self.getSession() != True):
                    self.request_pool.append(request_body)
                    return None
            #cookies = {"csrftoken": self.csrf_cookie}
            headers = {"X-CSRFToken": self.csrf_cookie, "Referer":self.post_url,}
        else:
            headers ={}
        if (len(self.request_pool)>0): 
            if not request_body == None: # flushEvents()から呼ばれている場合
                self.request_pool.append(request_body)
            try:
                print(self.post_url+local_path+"bulk/")
                print(self.request_pool)
                response = self.session.post(self.post_url+local_path+"bulk/",
                                            headers=headers, json=self.request_pool, allow_redirects=False)
                response.raise_for_status()
                if response.status_code == HTTPStatus.FOUND:
                   if self.multi:
                        self.getSession()
                else:
                    print(f"{response} : {self.request_pool}")
                    self.request_pool =[]
            except requests.exceptions.ConnectionError:
                print("ConnectinError")
            except requests.exceptions.HTTPError as e:
                print("HttpError")
                print(e)
                if(e.response.status_code == HTTPStatus.FORBIDDEN):
                    if self.multi:
                        self.getSession()
        else:
            try:
                response = self.session.post(self.post_url+local_path,
                                            headers=headers, json=request_body, allow_redirects=False)
                response.raise_for_status()
                if response.status_code == HTTPStatus.FOUND:
                    self.hasSession = False
                    self.request_pool.append(request_body)
            except requests.exceptions.ConnectionError as e:
                print(f"ConnectinError {e}")
                self.hasSession = False
                self.request_pool.append(request_body)
            except requests.exceptions.HTTPError as e:
                print(f"HttpError {e}")
                if(e.response.status_code == HTTPStatus.FORBIDDEN):
                    self.hasSession = False
                if(e.response.status_code == HTTPStatus.BAD_REQUEST):
                    print('* BAD REQUEST *')
                    print(e.response.text)
                    #print('******')
                else:
                    self.request_pool.append(request_body)
            except RemoteDisconnected as e:
                print("* Remote Connectin Error *")
                print(e)
                self.hasSession = False
                self.request_pool.append(request_body)
            except ProtocolError as e:
                print("* Protocol Error *")
                print(e)
                self.hasSession = False
                self.request_pool.append(request_body)

 
    def createBlankEvent(self, bp):
        #ウインドウへのアクセスがなかったことを示すイベントを送信
        start_time = bp.start_time
#        duration = datetime.now(timezone.utc) - start_time
        duration = datetime.now(ZoneInfo("Asia/Tokyo")) - start_time
#        print(f"BP end at {datetime.now(timezone.utc)}")
#        print("createBlankEvent")
#        self.writer.writerow([start_time, duration.seconds,0,0,0,0,0,'blank', 'blank'])
#        self.f.flush()
        request_body = {
            'start_time':start_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            'duration':duration.seconds,
            'distance_x':0,
            'distance_y':0,
            'strokes':0,
            'scrolls':0,
            'app':'blank',
            'title':'blank',
            }
        print(f"request:{request_body}")
        response = self.sendEvent(request_body, "api/Activity/")
#        response = requests.post(POST_URL, json=request_body)
        print(response)



'''
アクティビティ情報（イベント）をローカルファイルに出力する
''' 


class FileEventProducer(EventProducer):
    def __init__(self, path, encoding, period, time_zone, prefix=""):
        
        self.encoding = encoding
        self.period = period
        self.path =path
        self.time_zone = time_zone
        self.filename = ""
        self.end_time = None
        self.file = None
        self.writer = None
        self.suffix = prefix
        self.request_pool =[]

        # 現在時間を取得
        now_time = datetime.now(ZoneInfo(self.time_zone))
 
        # ファイル名を生成する。       
        base_time = self.getBaseTime(now_time)
        self.filename = self.path+"qt-"+self.suffix+base_time.strftime("%Y-%m-%d")+".csv"      
        
        # ファイルを生成するディレクトリがなければ生成する
        os.makedirs(self.path, exist_ok=True)

        # ファイルをオープンする。すでにファイルが存在する場合は、ファイル末尾から追記していく。
        #print(f"file name ={self.filename}")
        if not os.path.exists(self.filename):
            self.file = open(self.filename, 'w', encoding=self.encoding, errors='none')
            #print(f"create file {self.filename}")
        else:
            self.file = open(self.filename, 'a', encoding=self.encoding, errors='none')
            #print(f"open file {self.filename}")
        self.writer = csv.writer(self.file)
            
        # ファイルローテートする時間をend_timeに設定する
        if self.period :
            self.end_time = self.getEndTime(now_time)
            #print(f"set end_time {self.end_time}")
        
    def close(self):
        self.file.close()

        
    def getEndTime(self, now_time): 
        # ファイルローテートする時間を計算
        end_time =None  
        if self.period == "day":
            end_time = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))+timedelta(days=1)
        elif self.period =="week":
            index = date(now_time.year, now_time.month, now_time.day).isoweekday()%7
            end_time = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))+timedelta(days=(7-index))
        elif self.period =="month":
            end_time = datetime(now_time.year, now_time.month, 1, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))+relativedelta(months=1)
        return end_time

        
    def getBaseTime(self, now_time):
        # ファイル名に付ける基準時間を計算
        base_time =None  
        if self.period == "day":
            base_time = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        elif self.period =="week":
            index = date(now_time.year, now_time.month, now_time.day).isoweekday()%7
            base_time = datetime(now_time.year, now_time.month, now_time.day, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))-timedelta(days=index)
        elif self.period =="month":
            base_time = datetime(now_time.year, now_time.month, 1, 0, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        return base_time

    # 書き込まれたアクティビティの時間によって、ファイルをローテート
    def checkDate(self, start_time):
        if(start_time >= self.end_time):
            self.writer = None
            self.file.close()
            # ファイルをオープンする。すでにファイルが存在する場合は、ファイルを書き換え。
            self.filename = self.path+"qt-"+self.suffix+start_time.strftime("%Y-%m-%d")+".csv"
            self.file = open(self.filename, 'w', encoding=self.encoding, errors='none')
            self.writer = csv.writer(self.file)
            # ファイルローテートする時間をend_timeに設定する
            self.end_time = self.getEndTime(start_time)
 
           
    def createEvent(self, ar, last_window, end_time):
        #ウインドウイベント情報を書き込む
        event_data = ar.get_data()
        start_time = ar.start_time
        if end_time :
            duration = end_time - start_time
        else :
            duration = datetime.now(ZoneInfo(self.time_zone)) - start_time
        # ファイルローテートのチェック
        if self.period:
            self.checkDate(start_time)

        event_data['window'] = last_window
        self.writer.writerow([
            start_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            duration.seconds,
            event_data['distance_x'],
            event_data['distance_y'],
            event_data['strokes'],
            event_data['scrolls'],
            event_data['window']['app'],
            event_data['window']['title']
            ])
        self.file.flush()



    def createAudioActivityEvent(self, window, start_time, end_time):
        #音声が使われていた期間の情報をAudioActivityイベントとしてファイルに書き込む。
        #windowは、音声が流れ始めた時にアクティブだったウインドウ
        duration = end_time - start_time
        title_str = window['title']
        if(len(title_str) > 0 ):
            if(len(title_str) > 256 ):
                title_str = title_str[:256]
        else:
            title_str ="NONE"
        # ファイルローテートのチェック
        if self.period:
            self.checkDate(start_time)
            
        self.writer.writerow([
            start_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            end_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            duration.seconds,
            window['app'],
            title_str,
            None,None,
            None,None,
            None,None
        ])
        self.file.flush()


    def flushEvents(self):
        return

    def createBlankEvent(self, bp):
        start_time = bp.start_time
        duration = datetime.now(ZoneInfo(self.time_zone)) - start_time
#        print(f"BP end at {datetime.now(timezone.utc)}")
#        print("createBlankEvent")
        self.writer.writerow([
            start_time.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            duration.seconds,
            0, 0, 0, 0, 'blank', 'blank'
            ])
        self.file.flush()


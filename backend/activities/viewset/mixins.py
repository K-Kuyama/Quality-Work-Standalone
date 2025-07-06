import math
import calendar
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo
from django.conf import settings

class CreateIndexMixin:
    # PeriodicalCateoryViewクラスからcreateIndexDataとcreateArrayメソッドを
    # こちらに移動。
    # PeriodicalCateoryViewとTotalEventTimeForPeriodicalGraphで使われている

    # kind_of_valueに入る値（定数）の定義
    DURATION = 0
    STROKES = 1
    SCROLLS = 2
    DISTANCE = 3

    def createIndexData(self, activity_list):
        # グラフ描画に必要な単位時間あたりの量を計算する
        
        str_index = 0
        if self.kind_of_period == "day":
            str_index = 11
        elif self.kind_of_period == "week":
            str_index = 0
        elif self.kind_of_period == "month":
            str_index = 8
        elif self.kind_of_period == "year":
            str_index = 5  
            
        result = self.createArray()
        category_index_data = result[0]
        n_of_index = result[1]
        for act in activity_list:
            # astimezone()でローカルタイムに変換した後、replace()でそのままの時間でnaive時間に変換する。
            # その後の計算はnaive時間で計算する。
            start_time = act.start_time.astimezone(ZoneInfo(getattr(settings, "TIME_ZONE", None))).replace(tzinfo=None)
            end_time = start_time +timedelta(seconds=act.duration)
            round_time = None
            index = 0

            # start_time以降で、正時、日、月、年をまたぐ基準になる時間を求め、round_timeに設定
            if self.kind_of_period == "week":
                # JavaScriptのweekdayの数値表現に合わせる。日曜日が0になるようにする。
                index = date(start_time.year, start_time.month, start_time.day).isoweekday()%7
                round_time = datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)+timedelta(days=1)
            else:
                date_time = str(start_time)
                index = int(date_time[str_index:str_index+2])

                if self.kind_of_period == "day":
                    round_time = datetime(start_time.year, start_time.month, start_time.day, start_time.hour, 0, 0)+timedelta(hours=1)
                elif self.kind_of_period =="month":
                    round_time = datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)+timedelta(days=1)
                    index -= 1
                elif self.kind_of_period =="year":
                    round_time = datetime(start_time.year, start_time.month, start_time.day, 0, 0, 0)+relativedelta(months=1)
                    index -= 1
            if self.kind_of_value == self.DURATION and end_time > round_time:
                #activityが、正時、日、月、年をまたぐ場合、そのduration時間を前後に振り分ける
                td = end_time - round_time
                after = td.total_seconds()
                before = act.duration-after
                category_index_data[index]['value'] += before

                interval = 3600*24*30   #正しくないが、仮に設定。多分ここまでの時間になることはないと想定。
                if self.kind_of_period == "day":
                    interval = 3600
                elif self.kind_of_period == "month" or self.kind_of_period == "week":
                    interval = 3600*24
                index += 1
                
                while index < n_of_index:
                    print(f"index :{index}")
                    print(f"after={after}, interval={interval}")
                    if after < interval:
                        category_index_data[index]['value'] += after
                        break
                    else:
                        category_index_data[index]['value'] += interval
                        after -= interval
                        index += 1
                #if index+1 <n_of_index:
                #    category_index_data[index+1]['value'] += after
            else:
                #activityが、正時、日、月、年をまたいでいない場合、activityのduration時間をそのままセットする
                #category_index_data[index]['value'] += act.duration
                if self.kind_of_value == self.DURATION:
                    category_index_data[index]['value'] += act.duration
                elif act.scrolls != None:
                    if self.kind_of_value == self.DISTANCE:
                        category_index_data[index]['value'] += math.sqrt(act.distance_x**2 + act.distance_y**2)
                    elif self.kind_of_value == self.STROKES:
                        category_index_data[index]['value'] += act.strokes
                    elif self.kind_of_value == self.SCROLLS:
                        category_index_data[index]['value'] += act.scrolls
            
        return category_index_data
        

    
    def createArray(self):
        # self.start_datetimeから、日、週、月、年いずれかのインデックスリストを作成する
        # indexに文字列を設定、valueには0が入る。

        n_of_index = 0
        adjust = 0
        if self.kind_of_period == "day":
            n_of_index = 24
        elif self.kind_of_period == "week":
            n_of_index = 7
        elif self.kind_of_period == "month":
            n_of_index = calendar.monthrange(self.start_datetime.year, self.start_datetime.month)[1]
            adjust = 1
        elif self.kind_of_period == "year":
            n_of_index = 12
            adjust = 1        
        # 配列の作成
        hourly_data = []
        if self.kind_of_period == "week":
            index_day = self.start_datetime
            for p in range(n_of_index):
                hourly_data.append({'index':str(index_day.day).zfill(2)+f" ({index_day.strftime('%a')})", 'value':0})
                index_day = index_day + timedelta(days=1)
        else:
            for p in range(n_of_index):
                hourly_data.append({'index':str(p+adjust).zfill(2), 'value':0})
        
        return hourly_data, n_of_index 

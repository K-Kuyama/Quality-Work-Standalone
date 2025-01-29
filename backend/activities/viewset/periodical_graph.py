#from django.shortcuts import render

# Create your views here.
#import django_filters
import calendar
from datetime import date
from django.db.models import Sum
from django.db.models.functions import Trunc
from datetime import datetime, timedelta
#import datetime
from rest_framework import generics
from rest_framework.response import Response

from django.db.models import F
from django.db.models.functions import Power, Sqrt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.conf import settings

from activities.models import Activity
from activities.serializer import  PeriodicalGraphSerializer

from django.conf import settings
from activities.decolators import attach_decorator

from django.conf import settings

#USE_POSTGRESQL = True


# 指定された日の、時間ごとの合計作業時間を出力する
class TotalEventTimeForPeriodicalGraph(generics.ListAPIView):
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    serializer_class = PeriodicalGraphSerializer
    kind_of_period = ""     # パラメータとしてクライアントから送られてくるグラフの種別 (day, week, month, yearのいずれか)
    time_strings = ""       # 各グラフにおける単位時間(hour, day, monthのいずれか)
    start_datetime = None   # クライアントから送られてくる、データ取得の開始時間
    end_date_time = None    # クライアントから送られてくる、データ取得の終了時間

    def evaluate_params(self):
        params = self.request.query_params
        if 'kind_of_period' in params:
            self.kind_of_period = params.get('kind_of_period').lower()
        else:
            self.kind_of_period = "day"

        if self.kind_of_period == "day":
            self.time_strings = "hour"
        elif self.kind_of_period == "week":
            self.time_strings = "day"
        elif self.kind_of_period == "month":
            self.time_strings = "day"
        elif self.kind_of_period == "year":
            self.time_strings = "month"
        else:
            self.time_strings = "hour"
            
        if 'kind_of_value' in params:
            self.kind_of_value = params.get('kind_of_value').lower()
        else:
            self.kind_of_value = 'duration'

    # 単位時間ごとの作業時間（単位：秒）をデータモデルから取得する
    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
        #print(f"st_str->:{st_str} ")
        self.start_datetime = datetime.strptime(st_str, self.format_str)
        self.end_datetime = datetime.strptime(end_str, self.format_str)
        
#        return Activity.objects.exclude(title="blank").values("start_time")

        if self.kind_of_value == 'strokes':
            return Activity.objects.filter(
                    start_time__gte=self.start_datetime,
                    start_time__lte=self.end_datetime
                    ).exclude(
                        title="blank"
                        ).annotate(
                            date_time=Trunc("start_time", self.time_strings)
                            ).values('date_time').annotate(total = Sum("strokes")
                                                           ).values('date_time','total')
        elif self.kind_of_value =='scrolls':
            return Activity.objects.filter(
                    start_time__gte=self.start_datetime,
                    start_time__lte=self.end_datetime
                    ).exclude(
                        title="blank"
                        ).annotate(
                            date_time=Trunc("start_time", self.time_strings)
                            ).values('date_time').annotate(total = Sum("scrolls")
                                                           ).values('date_time','total')
            
        elif self.kind_of_value =='distance':
            return Activity.objects.filter(
                    start_time__gte=self.start_datetime,
                    start_time__lte=self.end_datetime
                    ).exclude(
                        title="blank"
                        ).annotate(
                            date_time=Trunc("start_time", self.time_strings)
                            ).values('date_time').annotate(total = Sum(Sqrt(Power(F("distance_x"),2)+Power(F("distance_y"),2)))
                                                           ).values('date_time','total')
        
        else :       
            return Activity.objects.filter(
                    start_time__gte=self.start_datetime,
                    start_time__lte=self.end_datetime
                    ).exclude(
                        title="blank"
                        ).annotate(
                            date_time=Trunc("start_time", self.time_strings)
                            ).values('date_time').annotate(total = Sum("duration")
                                                           ).values('date_time','total')

    # 正時,日、月をまたがるイベントを抽出する    
    def get_subquery(self):
        # query_str文字列の中では以下の注意が必要
        #　djangoの仕様で、必ずマスターキーとなるカラムを返すように書く必要がある。

        
        index_str =""        
        round_str = ""
        unit_str =""
        
        if settings.USE_POSTGRESQL:
            if self.time_strings == "hour":
                unit_key ="HH24"
                unit_str ="hour"
            elif self.time_strings == "day":
                unit_key ="DD"
                unit_str ="day"
            elif self.time_strings == "month":
                unit_key="MM"
                unit_str ="month"
        
            # WHERE句の中でend_timeとroundedTimeを使うには、activities_activityテーブルのSELECT文が先に
            # 評価されている必要がある。このため、一度dummyテーブルを作り、WHERE句につなげる。
            # SQLiteの場合は、この必要がない。。。
            query_str = f"""
                SELECT *
                FROM
                (
                SELECT id, to_char(start_time AT TIME ZONE '{settings.TIME_ZONE}'+ interval '1 {unit_str}','{unit_key}') AS dt_index,
                    start_time AT TIME ZONE '{settings.TIME_ZONE}' AS start_time,
                    date_trunc('{unit_str}', start_time AT TIME ZONE '{settings.TIME_ZONE}'+ interval '1 {unit_str}') AS roundedTime,
                    start_time AT TIME ZONE '{settings.TIME_ZONE}'+ interval '1 second'*duration AS end_time,
                    duration, distance_x, distance_y, strokes, scrolls, title 
                FROM activities_activity 
                ) dummy
                WHERE end_time > to_timestamp(%s, 'YYYY-MM-DD HH24:MI:SS.MS') AND start_time < to_timestamp(%s,'YYYY—MM-DD HH24:MI:SS.MS')
                        AND title != 'blank'
                        AND roundedTime BETWEEN start_time and end_time
                """
        
        
        
        else: 
            if self.time_strings == "hour":
                index_str = "'%%H',datetime(start_time, 'localtime', '+1 hours'"
                round_str = """'+1 hours', '-'||strftime('%%M',start_time, 'localtime')||' minutes', '-'||strftime('%%S',start_time, 'localtime')||' seconds'"""
            elif self.time_strings == "day":
                index_str = "'%%d',datetime(start_time, 'localtime', '+1 days'"
                round_str = """'+1 days', '-'||strftime('%%H',start_time, 'localtime')||' hours', '-'||strftime('%%M',start_time, 'localtime')||' minutes',
                    '-'||strftime('%%S',start_time, 'localtime')||' seconds'"""
            elif self.time_strings == "month":
                index_str = "'%%m',datetime(start_time, 'localtime', '+1 months'"
                round_str = """'+1 months', '-'||strftime('%%H',start_time, 'localtime')||' hours', '-'||strftime('%%M',start_time, 'localtime')||' minutes',
                    '-'||strftime('%%S',start_time, 'localtime')||' seconds'"""
                    
                    
        # - strtimeの第一引数のフォーマット文字列は　%H ではなく %%Hと書く。%とその後に続く文字はエスケープシーケンスと見なされるため。
        # - datetimeの第一引数に渡される%sを'で括っていはいけない。'を使うと%sがエスケープシーケンスとして認識されなくなる。            
            query_str = f"""
                SELECT id, strftime({index_str})) AS dt_index, datetime(start_time, 'localtime') AS start_time,
                    datetime(start_time, 'localtime', {round_str}) as roundedTime,
                    datetime(start_time, 'localtime', '+'||duration||' seconds') as end_time, duration, distance_x, distance_y, strokes, scrolls, title 
                FROM activities_activity 
                WHERE end_time > datetime(%s) AND datetime(start_time, 'localtime') < datetime(%s) AND title != 'blank'
                    AND (roundedTime BETWEEN datetime(start_time, 'localtime') and end_time)
            """ 

        
        #print("query strings --------")
        #print(query_str)

        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
        #print(f"st_str:{st_str}")
        #print(f"end_str:{end_str}")
#        subq = Activity.objects.raw(query_str,[st_str,end_str]).query
        subq = Activity.objects.raw(query_str,[st_str,end_str])
#        subq = Activity.objects.raw(query_str, [st_str,])
#        print(subq.query)
        return subq

    def createResultData(self, query_set, sub_query_set):
        n_of_index = 0
        str_index = 0
        adjust = 0
        if self.kind_of_period == "day":
            n_of_index = 24
            str_index = 11
        elif self.kind_of_period == "week":
            n_of_index = 7
            str_index = 0
        elif self.kind_of_period == "month":
            n_of_index = calendar.monthrange(self.start_datetime.year, self.start_datetime.month)[1]
            str_index = 8
            adjust = 1
        elif self.kind_of_period == "year":
            n_of_index = 12
            str_index = 5
            adjust = 1
        
        # 配列の作成
        hourly_data = []
        #print(f"kind of period :->{self.kind_of_period}")
        if self.kind_of_period == "week":
            index_day = self.start_datetime
            for p in range(n_of_index):
                print(f"p:{p} - index_day:{index_day}")
                hourly_data.append({'index':str(index_day.day).zfill(2)+f" ({index_day.strftime('%a')})", 'value':0})
                index_day = index_day + timedelta(days=1)
            #print("----------")
#                index_day = datetime(index_day, '+1 days')
        else:
            for p in range(n_of_index):
                hourly_data.append({'index':str(p+adjust).zfill(2), 'value':0})
        #print(f"hourly_data: {hourly_data}")
            
        # 単位時間ごとの作業秒数を入力する
        for d in query_set:   
            #print(f"obj:{d}")
            index = 0
            if self.kind_of_period == "week":
                dt = d['date_time']
                # JavaScriptのweekdayの数値表現に合わせる。日曜日が0になるようにする。
                index = date(dt.year, dt.month, dt.day).isoweekday()%7
#                index = calendar.weekday(dt.year, dt.month, dt.day)
            else:
                date_time = str(d['date_time'])
                index = int(date_time[str_index:str_index+2])
            #print(f"index:{index}")
            hourly_data[index-adjust]['value'] += int(d['total'])

        #print("initial data")        
        #for d in hourly_data:
        #    print(d)

        #for d in sub_query_set:
        #    print(d.__dict__)
        #    print(f"id:{d.id}, index:{d.dt_index}, start_time:{d.start_time},end_time:{d.end_time}, duration:{d.duration}")    
        # 正時、日、月またがりのイベントの作業時間の割り振りを計算し、補正をかける
        for d in sub_query_set:
            #print(f"id:{d.id}, start_time:{d.start_time}, roundedTime:{d.roundedTime},end_time:{d.end_time}, duration:{d.duration}")
            #print(d.roundedTime, d.start_time)
            #roundedTimeは文字列型なので変換が必要(SQLiteの場合)
            #SQL文で指定したroundedTimeはオブジェクト化した時に大文字が小文字に変換されroundedtimeとなる(POSTGRESQLの場合)
            if settings.USE_POSTGRESQL:
                rt = d.roundedtime
            else:
                rt = datetime.strptime(d.roundedTime+"+0000",'%Y-%m-%d %H:%M:%S%z')

            td = rt - d.start_time
#            td = d['roundTime'] - d['start_time']
            before = int(td.total_seconds())
            after = int(d.duration)-before
            if self.kind_of_period == "week":
                index = date(rt.year, rt.month, rt.day).isoweekday()%7
            elif self.kind_of_period == "month":
                index = int(d.dt_index)-1
            else:
                index = int(d.dt_index)
            #print(f"index {index}, value {after}")
            if index >0:
                hourly_data[index-1]['value'] -= after
            if index<n_of_index:
                hourly_data[index]['value'] += after
                
        return hourly_data
 
          
    #　generics.ListAPIViewのas_view()から呼び出されるメソッドを上書き
    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))             
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        queryset = self.get_queryset()
        sub_queryset = self.get_subquery()
    
        hl = self.createResultData(queryset,sub_queryset)
        #for h in hl:
        #    print(f"{h['index']} : {h['value']}")

        serializer = self.get_serializer(hl, many=True)
        return Response(serializer.data)



            
        
        
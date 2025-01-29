'''
Created on 2024/08/18

@author: kuyamakazuhiro
'''

import calendar
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .sort_out_by_categories import SortOutByCategoriesView
from activities.serializers.periodical_category_serializer import PeriodicalCategorySerializer

from django.conf import settings
from activities.decolators import attach_decorator

class PeriodicalCategoriesView(SortOutByCategoriesView):
    serializer_class = PeriodicalCategorySerializer

    
    def evaluate_params(self):
        super().evaluate_params()
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

        st_str = self.request.query_params.get("start")
        self.start_datetime = datetime.strptime(st_str, "%Y-%m-%d %H:%M:%S.%f")


    def createResultData(self, c_list):
        index_list = []
        for category in c_list:
            idxd = self.createIndexData(category.activities)
            index_list.append(PeriodicalCategory(category.categoryName, category.backgroundColor, idxd))
        return index_list
        
    def createIndexData(self, activity_list):
        
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
            #print(f"act start time:{act.start_time}")
            #print(type(act.start_time))
            
            #format_str = ""
            #if len(act.start_time) < 20:
            #    print(act.start_time)
            #    format_str = '%Y-%m-%dT%H:%M:%S'
            #elif len(act.start_time) < 26:
            #    format_str = '%Y-%m-%dT%H:%M:%S%z'
            #else:
            #    format_str = '%Y-%m-%dT%H:%M:%S.%f%z'
            #start_time = datetime.strptime(act.start_time, format_str).replace(tzinfo=None)
            start_time = datetime.strptime(act.start_time, '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
            
            #print(f"start_time type:{type(start_time)} {start_time}")
            end_time = start_time +timedelta(seconds=act.duration)
            round_time = None
            index = 0
            if self.kind_of_period == "week":
                # JavaScriptのweekdayの数値表現に合わせる。日曜日が0になるようにする。
                index = date(start_time.year, start_time.month, start_time.day).isoweekday()%7
#                index = calendar.weekday(dt.year, dt.month, dt.day)
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
            #print(f"{end_time = :%X %Z}")
            #print(round_time)
            if end_time > round_time:
                #print(f"end time : {end_time} <-> round time : {round_time}")
                td = end_time - round_time
                before = td.total_seconds()
                after = act.duration-before
                category_index_data[index]['duration'] += before
                if index+1 <n_of_index:
                    #print(f"index {index}: max {n_of_index}")
                    category_index_data[index+1]['duration'] += after
            else:
                #if(self.kind_of_period =="month"):
                #    print(f"index ::{index}")
                category_index_data[index]['duration'] += act.duration
            
        return category_index_data
        
    def createArray(self):
        n_of_index = 0
        #str_index = 0
        adjust = 0
        if self.kind_of_period == "day":
            n_of_index = 24
            #str_index = 11
        elif self.kind_of_period == "week":
            n_of_index = 7
            #str_index = 0
        elif self.kind_of_period == "month":
            n_of_index = calendar.monthrange(self.start_datetime.year, self.start_datetime.month)[1]
            #str_index = 8
            adjust = 1
        elif self.kind_of_period == "year":
            n_of_index = 12
            #str_index = 5
            adjust = 1        
        # 配列の作成
        hourly_data = []
        #print(f"kind of period :->{self.kind_of_period}")
        if self.kind_of_period == "week":
            index_day = self.start_datetime
            for p in range(n_of_index):
                #print(f"p:{p} - index_day:{index_day}")
                hourly_data.append({'index':str(index_day.day).zfill(2)+f" ({index_day.strftime('%a')})", 'duration':0})
                index_day = index_day + timedelta(days=1)
            #print("----------")
#                index_day = datetime(index_day, '+1 days')
        else:
            for p in range(n_of_index):
                hourly_data.append({'index':str(p+adjust).zfill(2), 'duration':0})
        #print(f"hourly_data: {hourly_data}")
        
        return hourly_data, n_of_index 


        
    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))    
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        queryset = self.get_queryset()
        # カテゴリー情報追加
#        cserializer = self.getCSerializer(queryset, many=True, p_id=self.request.query_params.get('p_id'))
        cserializer = self.getCSerializer(queryset, many=True, p_id=self.perspective)
        # カテゴリー別にグルーピング
        c_list = self.sortOut(cserializer.data)
        # 単位時間ごとのデータを作成
        pl = self.createResultData(c_list)
        
        serializer = self.get_serializer(pl, many=True)
        return Response(serializer.data)
        
class PeriodicalCategory:
    def __init__(self, name, color, data):
        self.name = name
        self.backgroundColor = color
        self.data_array = data
        
    
        
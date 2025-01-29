#from django.shortcuts import render

# Create your views here.
#import django_filters
import math
from django.db.models import Sum, F, Value, IntegerField
from django.db.models.functions import Trunc
from datetime import datetime, timezone, timedelta
#import datetime
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from operator import attrgetter

from .models import Activity
from .serializer import ActivitySerializer, ByHourSerializer
#from .serializer import ActivitySerializer

from django.conf import settings


class ActivityViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )
    
class BulkCreateActivityView(generics.CreateAPIView):
    serializer_class = ActivitySerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(BulkCreateActivityView, self).get_serializer(*args, **kwargs)

# 時間指定でリストを取り出す。ブランクは除外する。

class TimePeriodView(generics.ListAPIView):
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    serializer_class = ActivitySerializer
    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
        return Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str)).exclude(title="blank")

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000
    
    def get_paginated_response(self, data):
        return Response({
            'current' :self.page.number,
            'count': self.page.paginator.count,
            'final': self. page.paginator.num_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            })

# シンプルにアクティビティリストをページネートする
class PaginatedEventView(generics.ListAPIView):
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    serializer_class = ActivitySerializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        print(st_str)
        end_str = self.request.query_params.get("end")
        print(end_str)
        return Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str)).exclude(title="blank")   

# 指定された日の、時間ごとの合計作業時間を出力する
# TotalEventTimeForPeriodicalGraphに機能を移したので、折を見て消去する

class TotalEventTimeByHour(generics.ListAPIView):
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    serializer_class = ByHourSerializer

    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
#        return Activity.objects.exclude(title="blank").values("start_time")
        return Activity.objects.filter(
                    start_time__gte=datetime.strptime(st_str, self.format_str),
                    start_time__lte=datetime.strptime(end_str, self.format_str)
                    ).exclude(
                        title="blank"
                        ).annotate(
                            date_time=Trunc("start_time", "hour")
                            ).values('date_time').annotate(total_time = Sum("duration")
                                                           ).values('date_time','total_time')


    def get_subquery(self):
        # 正時をまたがるイベントの抽出
        # query_str文字列の中では以下の注意が必要
        #　djangoの仕様で、必ずマスターキーとなるカラムを返すように書く必要がある。
        # - strtimeの第一引数のフォーマット文字列は　%H ではなく %%Hと書く。%とその後に続く文字はエスケープシーケンスと見なされるため。
        # - datetimeの第一引数に渡される%sを'で括っていはいけない。'を使うと%sがエスケープシーケンスとして認識されなくなる。
        query_str = """
        SELECT id, strftime('%%H',datetime(start_time, '+1 hours')) AS index_hour, start_time, 
                datetime(start_time, '+1 hours', '-'||strftime('%%M',start_time)||' minutes', '-'||strftime('%%S',start_time)||' seconds') as roundedTime,
                datetime(start_time, '+'||duration||' seconds') as end_time, duration, title 
            FROM activities_activity 
              WHERE end_time > datetime(%s) AND start_time < datetime(%s) AND title != 'blank'
                AND (roundedTime BETWEEN start_time and end_time)
        """ 
        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
#        subq = Activity.objects.raw(query_str,[st_str,end_str]).query
        subq = Activity.objects.raw(query_str,[st_str,end_str])
#        subq = Activity.objects.raw(query_str, [(st_str),(end_str)])
#        print(subq.query)
        return subq

    def createHourlyData(self, query_set, sub_query_set):
        hourly_data = []
        for p in range(24):
            hourly_data.append({'hour':str(p).zfill(2), 'duration':0})
            
        # １時間ごとの作業秒数を計算する
        for d in query_set:
            print(f"obj:{d}")
            date_time = str(d['date_time'])
            index = date_time[11:13]
            hourly_data[int(index)]['duration'] += int(d['total_time'])
            
        # 正時またがりの補正をかける
        for d in sub_query_set:
            print(d.roundedTime, d.start_time)
            #roundedTimeは文字列型なので変換が必要
            td = datetime.strptime(d.roundedTime+"+0000",'%Y-%m-%d %H:%M:%S%z') - d.start_time
#            td = d['roundTime'] - d['start_time']
            before = int(td.total_seconds())
            after = int(d.duration)-before
            index = int(d.index_hour)
            if index >0:
                hourly_data[index-1]['duration'] -= after
            if index<24:
                hourly_data[index]['duration'] += after
        return hourly_data
 
          
            
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        sub_queryset = self.get_subquery()
    
        hl = self.createHourlyData(queryset,sub_queryset)
        for h in hl:
            print(f"{h['hour']} : {h['duration']}")

        serializer = self.get_serializer(hl, many=True)
        return Response(serializer.data)



# 指定された期間のイベントリストを返す。
# merged_item が指定されている場合は、タイトル(title)ごとあるいはアプリケーション(app)ごとに集計した時間を返す
# sort_byが指定されているの場合は、時間(duration)の長いもの順、あるいは開始時間(time)の早いもの順にソートをして返す
# pagenationがTrueの場合は、ページに分割した情報を返す

class MergedEventView(generics.ListAPIView):
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    serializer_class = ActivitySerializer
    pagination_class = StandardResultsSetPagination
    need_merge = False
    app_merge = False
    title_merge = False
    need_sort = False
    duration_sort = False
    time_sort = False
    need_pagination = False
        

    def evaluate_params(self):
        params = self.request.query_params
        if 'merged_item' in params:
            self.need_merge = True
            if params.get('merged_item').lower() == "app":
                self.app_merge = True
            elif params.get('merged_item').lower() == "title":
                self.title_merge = True
            else:
                self.need_merge = False
        if 'sorted_by' in params:
            self.need_sort = True
            if params.get('sorted_by').lower() =="duration":
                self.duration_sort = True
            elif params.get('sorted_by').lower() =="time":
                self.time_sort = True
            else:
                self.neet_sort = False
        if 'pagination' in params:
            if params.get('pagination').lower() == "true":
                self.need_pagination = True
            
    
    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        print(st_str)
        end_str = self.request.query_params.get("end")
        print(end_str)
        return Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str)).exclude(title="blank")
    
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        queryset = self.get_queryset()
        if self.need_merge:
            merged_activities = self.merge_activity(queryset)
        else:
            merged_activities = queryset
        if self.need_sort:
            activities = self.sort_activity(merged_activities)
        else:
            activities = merged_activities    
            
        if self.need_pagination:
            page = self.paginate_queryset(activities)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(activities, many=True)
            return Response(serializer.data)

#        print(queryset)
#        page = self.paginate_queryset(queryset)
#        serializer = self.get_serializer(page, many=True)
#        print(serializer.data)
#        serializer = self.get_serializer(queryset, many=True)
#        print(f"data : {serializer.data}")
#        if self.need_merge:
#            event_set =  self.merge_event(serializer.data)
#            return Response(event_set)
#            return self.get_paginated_response(event_set)
#        else:
#            return Response(serializer.data)
#            return self.get_paginated_response(serializer.data)


    def sort_activity(self, queryset):
        print(queryset)
        if self.duration_sort:
#            return sorted(queryset, key=lambda x:x['duration'], reverse=True)
            return sorted(queryset, key=attrgetter('duration'), reverse=True)
#            return queryset.sort(key=attrgetter('duration'), reverse=True)
        elif self.time_sort:
#            return sorted(queryset, key=lambda x:x['start_time'], reverse=True)
            return sorted(queryset, key=attrgetter('start_time'), reverse=True)
#            return queryset.sort(key=attrgetter('start_time'), reverse=True)
        else:
            return queryset

    def merge_activity(self, queryset):
        tmp_list = []
        tmp_dict = dict()
        for activity in queryset:
            app_name = activity.app
            if app_name not in tmp_dict:
                tmp_dict[app_name]=[activity]
            else:
                tmp_dict[app_name].append(activity)
                
        if self.title_merge:
            for activity_list in tmp_dict.values():
                tmp_dict2 = dict()
                for act in activity_list:
                    title_name = act.title
                    if title_name not in tmp_dict2:
                        tmp_dict2[title_name]=[act]
                    else:
                        tmp_dict2[title_name].append(act)
                tmp_list.append(tmp_dict2)
        else:
            tmp_list.append(tmp_dict)
         
        target_set = []
        for td in tmp_list:
            for key in td.keys():
                app = None
                title = None
                if self.app_merge:
                    app = key
                elif self.title_merge:
                    title = key
                    app = td[key][0].app
                duration = 0
                distance_x = 0
                distance_y = 0
                strokes = 0
                scrolls = 0
                for obj in td[key]:
                    duration += obj.duration
                    distance_x += obj.distance_x
                    distance_y += obj.distance_y
                    strokes += obj.strokes
                    scrolls += obj.scrolls
                act = Activity()
                act.start_time = None
                act.duration = duration
                act.distance_x = distance_x
                act.distance_y = distance_y
                act.strokes = strokes
                act.scrolls = scrolls
                act.app = app
                act.title = title
                target_set.append(act)
        return target_set
 
# 使っていない関数（merge_activityに書き換えた）　いずれ消去する。   
    def merge_event(self, org_set):
        tmp_list = []
        tmp_dict = dict()
        for event in org_set:
            app_name = event['app']
            if app_name not in tmp_dict: 
                tmp_dict[app_name]=[event]
            else:
                tmp_dict[app_name].append(event)
 
        if self.title_merge:
            for ev_list in tmp_dict.values():
                tmp_dict2 = dict()
                for ev in ev_list:
                    title_name = ev['title']
                    if title_name not in tmp_dict2:
                        tmp_dict2[title_name]=[ev]
                    else:
                        tmp_dict2[title_name].append(ev)
                tmp_list.append(tmp_dict2)
        else:
            tmp_list.append(tmp_dict)
            
        target_set = []
        for td in tmp_list:
            for key in td.keys():
                app = None
                title = None
                if self.app_merge:
                    app = key
                elif self.title_merge:
                    title = key
                    app = td[key][0]['app']
                duration = 0
                distance_x = 0
                distance_y = 0
                strokes = 0
                scrolls = 0
                for obj in td[key]:
                    duration += obj['duration']
                    distance_x += obj['distance_x']
                    distance_y += obj['distance_y']
                    strokes += obj['strokes']
                    scrolls += obj['scrolls']
                target_set.append({'start_time':None, 'duration':duration,
                                   'distance_x':distance_x, 'distance_y':distance_y,
                                   'strokes':strokes, 'scrolls':scrolls,'app':app, 'title':title})
        return target_set
            
             
            
        
        
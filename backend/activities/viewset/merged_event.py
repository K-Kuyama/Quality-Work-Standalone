'''
Created on 2024/06/20

@author: kuyamakazuhiro
'''


from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from operator import attrgetter

from activities.models import Activity
from activities.serializer import FormattedActivitySerializer

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.conf import settings
from activities.decolators import attach_decorator

#ページネーション情報の設定

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


# 指定された期間のイベントリストを返す。
# merged_item が指定されている場合は、タイトル(title)ごとあるいはアプリケーション(app)ごとに集計した時間を返す
# sort_byが指定されているの場合は、時間(duration)の長いもの順、あるいは開始時間(time)の早いもの順にソートをして返す
# pagenationがTrueの場合は、ページに分割した情報を返す

class MergedEventView(generics.ListAPIView):
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    serializer_class = FormattedActivitySerializer
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
        #print(st_str)
        end_str = self.request.query_params.get("end")
        #print(end_str)
        return Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str)).exclude(title="blank")

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):
        #print(request.headers)
        #print("----------------")
        #print(request.COOKIES)
        #print("----------------")
        #print(request.user)
        #print("----------------")
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
            #print(f"get serializer")
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
#        print(queryset)
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

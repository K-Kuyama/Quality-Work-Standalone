from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from operator import attrgetter
from datetime import datetime, timezone, timedelta

from activities.models import Activity

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.conf import settings
from activities.decolators import attach_decorator
from activities.serializers.working_time_serializer import WorkingTimeSerializer
from activities.modules.perspective_model import ModelCreator
from activities.modules.combined_activities import get_combined_activities

class WorkingTime:
    def __init__(self, title, color, start_time, end_time):
        self.title = title
        self.color = color
        self.start_time = start_time
        self.end_time = end_time


class WorkingTimeChartView(generics.ListAPIView):
    serializer_class = WorkingTimeSerializer
    format_str = "%Y-%m-%d %H:%M:%S.%f"
    p_id = None

    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        #print(st_str)
        end_str = self.request.query_params.get("end")
        #print(end_str)
        return Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str))

    def get_combined_queryset(self):
        st_str = self.request.query_params.get("start")
        end_str = self.request.query_params.get("end")
        show_policy = 0
        if 'show_policy' in self.request.query_params:
            show_policy = int(self.request.query_params.get("show_policy"))
        return get_combined_activities(datetime.strptime(st_str, self.format_str), 
                                       datetime.strptime(end_str, self.format_str), show_policy)    

    def createWorkingTime(self, queryset):
        s_time = None
        e_time = None
        working_list = []       
        for d in queryset:
            if d.title != "blank":
                if s_time == None:
                    s_time = d.start_time    
                if e_time and e_time + timedelta(minutes=3) <d.start_time:  #前のデータのend_timeから3分以上経っていた場合
                    wt = WorkingTime("","", s_time, e_time)
                    working_list.append(wt)
                    s_time = d.start_time
                e_time = d.start_time + timedelta(seconds=d.duration)
            else:   #ブランクタイムだった場合
                wt = WorkingTime("","", s_time, e_time)
                working_list.append(wt)
                s_time = None
                e_time = None
        if s_time != None and e_time != None:
            wt = WorkingTime("", "", s_time, e_time)
            working_list.append(wt)
        return working_list


    def createDetailedWorkingTime(self, queryset):
        working_list = []       
        pm = ModelCreator.create(self.p_id)
        for d in queryset:
            if d.title != "blank":
                color_info = pm.get_colors(d)
                wt = WorkingTime(d.app+":"+d.title, color_info['backgroundColor'], d.start_time, d.start_time + timedelta(seconds=d.duration))
                working_list.append(wt)
        return working_list
    
    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):
        params = self.request.query_params
        if params.get('p_id'):
            self.p_id = int(params.get('p_id'))
        queryset = self.get_combined_queryset()
        if self.p_id:
            wl = self.createDetailedWorkingTime(queryset)
        else:
            wl = self.createWorkingTime(queryset)
        serializer = self.get_serializer(wl, many=True)
        return Response(serializer.data)
        
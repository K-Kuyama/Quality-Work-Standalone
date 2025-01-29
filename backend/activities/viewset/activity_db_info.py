'''
Created on 2024/09/09

@author: kuyamakazuhiro
'''


from rest_framework import generics
from django.db.models import Count, Max, Min
from rest_framework.response import Response
from activities.models import Activity
from activities.serializers.activity_db_info_serializer import ActivityDbInfoSerializer
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.conf import settings
from activities.decolators import attach_decorator

class ActivityDbInfoView(generics.RetrieveAPIView):

    #最新のデータベースの状況を取得したいので、毎回評価され、キャッシュが使われないようにする。
    # queryset = Activity.objects.aggregate(Min('start_time'), Max('start_time'), Count('id'))
    #　としてしまうと、一度評価された値がキャッシュされてしまうので、Activity.objects.all()までをquerysetにする。
    # 最後に.all()が呼ばれることで、キャッシュされない。
    # .aggregate(Min('start_time'), Max('start_time'), Count('id'))は後で実行する。
    
    queryset = Activity.objects.all()  
    serializer_class = ActivityDbInfoSerializer

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def retrieve(self, request, *args, **kwargs):
        #self.queryset = self.queryset.all()
        qsall = self.get_queryset()
        qs = qsall.aggregate(Min('start_time'), Max('start_time'), Count('id'))
        # dictをオブジェクトに変換する
        instance = ActivityDbInfo(qs['start_time__min'], qs['start_time__max'], qs['id__count'])
        #instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# 一時的なオブジェクト
class ActivityDbInfo:
    def __init__(self, start_time, end_time, count):
        self.startTime = start_time
        self.endTime = end_time
        self.count = count
        
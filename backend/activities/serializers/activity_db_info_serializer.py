'''
Created on 2024/09/09

@author: kuyamakazuhiro
'''


from rest_framework import serializers
from django.conf import settings
from dateutil.tz import gettz

class ActivityDbInfoSerializer(serializers.Serializer):
    # 時刻を整形して返す
    startTime = serializers.SerializerMethodField(read_only=True)
    #startTime = serializers.DateTimeField()
    endTime = serializers.SerializerMethodField(read_only=True)
    count = serializers.IntegerField()

    def get_startTime(self, obj):
        if(obj.startTime):
            st = obj.startTime.astimezone(gettz(settings.TIME_ZONE))
            return st.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""
        
    def get_endTime(self, obj):
        if(obj.endTime):
            st = obj.endTime.astimezone(gettz(settings.TIME_ZONE))
            return st.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""
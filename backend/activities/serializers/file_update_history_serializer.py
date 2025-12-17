'''
Created on 2024/09/10

@author: kuyamakazuhiro
'''


from rest_framework import serializers
from activities.models import FileUpdateHistory
from django.conf import settings
from dateutil.tz import gettz

#writeとreadで使うシリアライザを変える

class FileUpdateHistoryReadSerializer(serializers.ModelSerializer):
        # 時刻を整形して返す
        uploadTime = serializers.SerializerMethodField(read_only=True)
        startTime = serializers.SerializerMethodField(read_only=True)
        endTime = serializers.SerializerMethodField(read_only=True)

        class Meta:
            model = FileUpdateHistory
            fields = ('fileName', 'uploadTime', 'contents',
                      'startTime', 'endTime', 'dataCount', 'status')
            
        def get_uploadTime(self, obj):
            if(obj.uploadTime):
                st = obj.uploadTime.astimezone(gettz(settings.TIME_ZONE))
                return st.strftime("%Y-%m-%d %H:%M:%S")
            else:
                return ""

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
        
class FileUpdateHistoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpdateHistory
        fields = ('fileName', 'uploadTime', 'contents',
                  'startTime', 'endTime', 'dataCount', 'status')

                    
        
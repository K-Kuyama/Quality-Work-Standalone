'''
Created on 2024/04/26

@author: kuyamakazuhiro
'''

from rest_framework import serializers
from .models import Activity, Perspective, Category, CategorizedActivity, CategorizedKeyWord
from django.conf import settings
from dateutil.tz import gettz

# アクティビティリスト用のシリアライザ

class CreateActivityListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [Activity(**attrs) for attrs in validated_data]
        Activity.objects.bulk_create(result)
        return result

class ActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Activity
        fields = ('start_time', 'duration','distance_x','distance_y','strokes','scrolls',
                  'app','title')
        list_serializer_class = CreateActivityListSerializer



class FormattedActivitySerializer(serializers.ModelSerializer):

    start_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Activity
        fields = ('start_time', 'duration','distance_x','distance_y','strokes','scrolls',
                  'app','title')
        #list_serializer_class = CreateActivityListSerializer

    def get_start_time(self, obj):
        if(obj.start_time):
            st = obj.start_time.astimezone(gettz(settings.TIME_ZONE))
            return st.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""



# 使わないので折を見て削除
#TotalEventTimeByHourで使われている。

class ByHourSerializer(serializers.Serializer):
    hour = serializers.CharField(max_length=2)
    duration = serializers.IntegerField()
#    date_time = serializers.DateTimeField()
#    total_time = serializers.IntegerField()

# グラフのためのシリアライザ
class PeriodicalGraphSerializer(serializers.Serializer):
    index = serializers.CharField(max_length=2)
    value = serializers.IntegerField()
    
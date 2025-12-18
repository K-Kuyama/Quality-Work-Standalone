'''
Created on 2024/04/26

@author: kuyamakazuhiro
'''

from rest_framework import serializers
from .models import Activity, Perspective, Category, CategorizedActivity, CategorizedKeyWord, AudioActivity, ActivityPredictor, SystemSettings
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


# オーディオアクティビティリスト用のシリアライザ

class CreateAudioActivityListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [AudioActivity(**attrs) for attrs in validated_data]
        AudioActivity.objects.bulk_create(result)
        return result
    
class AudioActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = AudioActivity
        #fields = ('start_time','end_time','duration','start_app','start_title',
        #          'longest_app','longest_title','another_app','another_title')
        fields = "__all__"
        list_serializer_class = CreateAudioActivityListSerializer

class FormattedAudioActivitySerializer(serializers.ModelSerializer):

    start_time = serializers.SerializerMethodField(read_only=True)
    end_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AudioActivity
        #fields = ('start_time','end_time','duration','start_app','start_title',
        #          'longest_app','longest_title','another_app','another_title')
        fields = "__all__"
        list_serializer_class = CreateAudioActivityListSerializer
    
    def get_start_time(self, obj):
        if(obj.start_time):
            st = obj.start_time.astimezone(gettz(settings.TIME_ZONE))
            return st.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""
    
    def get_end_time(self, obj):
        if(obj.end_time):
            et = obj.end_time.astimezone(gettz(settings.TIME_ZONE))
            return et.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return ""



# AI関連

class ActivityPredictorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ActivityPredictor
        fields = "__all__"

# システム設定用のシリアライザー

class SystemSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = SystemSettings
        fields = "__all__"

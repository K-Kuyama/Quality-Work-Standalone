from rest_framework import serializers
#from activities.viewset.daemon_settings import AudioSettings


class AudioSettingsSerializer(serializers.Serializer):
    # Audio関係の設定を返すためのシリアライザー
    Poll_time = serializers.FloatField(min_value=0)
    Loop_back_device = serializers.CharField(max_length=128)
    Host_api = serializers.CharField(max_length=128)
    FORMAT = serializers.CharField(max_length=128)
    CHANNELS = serializers.IntegerField(min_value=0)
    RATE = serializers.IntegerField(min_value=0)
    CHUNK = serializers.IntegerField(min_value=0)
    Silence_threshold = serializers.IntegerField(min_value=0)
    Start_frame_threshold = serializers.IntegerField(min_value=0)
    End_frame_threshold = serializers.IntegerField(min_value=0)
    RETRY_INTERVAL = serializers.IntegerField(min_value=0)

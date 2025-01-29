from rest_framework import serializers

class WorkingTimeSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=128)
    color = serializers.CharField(max_length=128)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()

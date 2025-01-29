'''
Created on 2024/09/09

@author: kuyamakazuhiro
'''


from rest_framework import serializers


class ActivityDbInfoSerializer(serializers.Serializer):
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()
    count = serializers.IntegerField()
    
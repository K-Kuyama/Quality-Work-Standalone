'''
Created on 2024/07/06

@author: kuyamakazuhiro
'''
from rest_framework import serializers

class KeywordCandidateSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=128)
    count = serializers.IntegerField()
    activity_list = serializers.ListField(
            child = serializers.ListField(
            child = serializers.CharField(max_length=256)
            )
        )
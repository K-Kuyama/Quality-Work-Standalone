'''
Created on 2024/07/18

@author: kuyamakazuhiro
'''

from rest_framework import serializers

class PerspectiveEditorSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=128)
    color = serializers.CharField(max_length=128)
    delete_flag = serializers.BooleanField()

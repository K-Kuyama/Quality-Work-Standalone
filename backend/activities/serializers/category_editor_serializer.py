'''
Created on 2024/09/23

@author: kuyamakazuhiro
'''

from rest_framework import serializers

class CategoryEditorSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    id = serializers.IntegerField()
    perspective = serializers.IntegerField()
    name = serializers.CharField(max_length=128)
    color = serializers.CharField(max_length=128)
    delete_flag = serializers.BooleanField()
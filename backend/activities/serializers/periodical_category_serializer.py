'''
Created on 2024/08/19

@author: kuyamakazuhiro
'''
from rest_framework import serializers
from activities.serializer import PeriodicalGraphSerializer

#class PeriodicalDataSerializer(serializers.Serializer):
#    index = serializers.CharField(max_length=128)
#    duration = serializers.IntegerField()


class PeriodicalCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=128)
    backgroundColor = serializers.CharField(max_length=128)
    data_array = PeriodicalGraphSerializer(many=True)
    

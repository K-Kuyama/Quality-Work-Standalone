'''
Created on 2024/07/30

@author: kuyamakazuhiro
'''
from rest_framework import serializers
from activities.serializer import ActivitySerializer

class ColorInfoSerializer(serializers.Serializer):
    backgroundColor = serializers.CharField(max_length=128)
    stringColor = serializers.CharField(max_length=128)
    categoryName = serializers.CharField(max_length=128)
    categoryId = serializers.IntegerField()
    eventId = serializers.IntegerField()
    


'''
class CreateAListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [Activity(**attrs) for attrs in validated_data]
        Activity.objects.bulk_create(result)
        return result

class ASerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    duration = serializers.IntegerField()
    distance_x = serializers.FloatField()
    distance_y = serializers.FloatField()
    strokes = serializers.IntegerField()
    scrolls = serializers.IntegerField()
    app = serializers.CharField(max_length=128)
    title = serializers.CharField(max_length=256)

    class Meta:
        model = Category
        fields = ('id', 'perspective', 'name', 'color')
        list_serializer_class = CreateCategoryListSerializer       
'''
    


class CASerializer(serializers.Serializer):  
    backgroundColor = serializers.CharField(max_length=128)
    stringColor = serializers.CharField(max_length=128)
    categoryName = serializers.CharField(max_length=128)
    categoryId = serializers.IntegerField()
    eventId = serializers.IntegerField()
    activities = ActivitySerializer(many=True)

class MCASerializer(serializers.Serializer):  
    backgroundColor = serializers.CharField(max_length=128)
    stringColor = serializers.CharField(max_length=128)
    categoryName = serializers.CharField(max_length=128)
    categoryId = serializers.IntegerField()
    eventId = serializers.IntegerField()
    categories = CASerializer(many=True)

'''
Created on 2024/06/25

@author: kuyamakazuhiro
'''
from rest_framework import serializers
from activities.models import Perspective, Category, CategorizedActivity, CategorizedKeyWord

# パースペクティブ用のシリアライザ

class CreatePerspectiveListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [Perspective(**attrs) for attrs in validated_data]
        Perspective.objects.bulk_create(result)
        return result

class PerspectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perspective
        fields = ('id', 'name', 'color','use_def_color', 'index', 'categorize_model')
        list_serializer_class = CreatePerspectiveListSerializer
        


    

# カテゴリ用のシリアライザ

class CreateCategoryListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [Category(**attrs) for attrs in validated_data]
        Category.objects.bulk_create(result)
        return result

class CategorySerializer(serializers.ModelSerializer):
#    perspective = PerspectiveSerializer()
    
    class Meta:
        model = Category
        fields = ('id', 'perspective', 'name', 'color', 'index')
        list_serializer_class = CreateCategoryListSerializer       
 

 
        
# カテゴライズされたアクティビティ文字列（app名、Title）のシリアライザ

class CreateCategorizedActivityListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [CategorizedActivity(**attrs) for attrs in validated_data]
        CategorizedActivity.objects.bulk_create(result)
        return result

class CategorizedActivitySerializer(serializers.ModelSerializer):
#    category = CategorySerializer()
    
    class Meta:
        model = CategorizedActivity
        fields = ('id', 'category', 'app', 'title')
        read_only_fields =['id',]
        list_serializer_class = CreateCategorizedActivityListSerializer
        
 
# カテゴライズのためのキーワードのシリアライザ 
          
class CreateCategorizedKeyWordListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        result = [CategorizedKeyWord(**attrs) for attrs in validated_data]
        CategorizedKeyWord.objects.bulk_create(result)
        return result

class CategorizedKeyWordSerializer(serializers.ModelSerializer):
#    category = CategorySerializer()
    
    class Meta:
        model = CategorizedKeyWord
        fields = ('id', 'category', 'word', 'positive')
        list_serializer_class = CreateCategorizedKeyWordListSerializer
               



# カテゴリに属するアクティビティ（app, title）やキーワードも一緒に返す
class _CategorySerializer(serializers.ModelSerializer):
    activities = CategorizedActivitySerializer(many=True, read_only=True)
    key_words = CategorizedKeyWordSerializer(many=True, read_only=True)
    
    class Meta:
        model = Category
        fields = ('id', 'perspective', 'name', 'color', 'index', 'activities', 'key_words')
        list_serializer_class = CreateCategoryListSerializer    



# パースペクティブに属するカテゴリーの情報も一緒に返す
class _PerspectiveSerializer(serializers.ModelSerializer):    
    categories = _CategorySerializer(many=True, read_only=True)
 
    class Meta:
        model = Perspective
        fields = ['id', 'name', 'color','use_def_color', 'index', 'categorize_model','categories',]
        

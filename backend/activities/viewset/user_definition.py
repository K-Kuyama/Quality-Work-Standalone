'''
Created on 2024/06/20

@author: kuyamakazuhiro
'''

#import datetime
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import F
from django.db.models import Prefetch
from activities.models import  Perspective, Category, CategorizedActivity, CategorizedKeyWord
from activities.serializers.user_definition_serializers import PerspectiveSerializer, CategorySerializer, CategorizedActivitySerializer, CategorizedKeyWordSerializer, _PerspectiveSerializer
# from activities.modules.definition_model import DefinitionModel
from django.conf import settings
from activities.decolators import attach_decorator

class PerspectiveViewSet(viewsets.ModelViewSet):
    #queryset = Perspective.objects.all()
    queryset = Perspective.objects.prefetch_related('categories').order_by(F('index').asc(nulls_last=True))
    serializer_class = PerspectiveSerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )
    
class BulkCreatePerspectiveView(generics.CreateAPIView):
    serializer_class = PerspectiveSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(BulkCreatePerspectiveView, self).get_serializer(*args, **kwargs)


# <pk>で指定されたパースペクティブに紐付く情報を取り出して返す
# 取り出した情報は、シングルトンクラスである、DefinitionModelに登録され、別のアプリケーションから参照できるようにしている
class _PerspectiveView(generics.RetrieveAPIView):
    #queryset = Perspective.objects.prefetch_related('categories').all()
    #queryset = Perspective.objects.prefetch_related('categories').order_by(F('index').asc(nulls_last=True))
    
    # 紐づく情報もソートして取り出すため、Prefetchを使う
    prefetch = Prefetch('categories', queryset=Category.objects.order_by(F('index').asc(nulls_last=True)))
    queryset = Perspective.objects.prefetch_related(prefetch).order_by(F('index').asc(nulls_last=True))
    serializer_class = _PerspectiveSerializer   
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
#        print(serializer.data)
#        DefinitionModel().setPerspective(serializer.data)
#        print(DefinitionModel().categories)
        return Response(serializer.data)
    
#   
    
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().prefetch_related()
    serializer_class = CategorySerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )


# perspective IDを指定してカテゴリーを、表示順序にソートして取り出す。
class _CategoryView(generics.ListAPIView):
    queryset = Category.objects.all().order_by(F('index').asc(nulls_last=True))
    serializer_class = CategorySerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )    
    
    def get_queryset(self):
        params = self.request.query_params
        pid = int(params.get('p_id'))
        return Category.objects.filter(perspective=pid).order_by(F('index').asc(nulls_last=True))



class BulkCreateCategoryView(generics.CreateAPIView):
    serializer_class = CategorySerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(BulkCreateCategoryView, self).get_serializer(*args, **kwargs)


    
class CategorizedActivityViewSet(viewsets.ModelViewSet):
    queryset = CategorizedActivity.objects.all()
    serializer_class = CategorizedActivitySerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )

 
class BulkCreateCategorizedActivityView(generics.CreateAPIView):
    serializer_class = CategorizedActivitySerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(BulkCreateCategorizedActivityView, self).get_serializer(*args, **kwargs)

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))       
    def post(self, request):
        result = self.create(request)
        #print(f"post result => {result}")
#        DefinitionModel().reSetPerspective()
        return result
    
    
# 登録アクティビティ情報から指定されたidを削除する。複数の削除が可能
class DeleteCategorizedActivityView(generics.ListAPIView):    
    model = CategorizedActivity

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))
    def post(self, request):
        id_list = request.data
        CategorizedActivity.objects.filter(pk__in=id_list).delete()
#        DefinitionModel().reSetPerspective()
        return Response(id_list)
        
    
    
class CategorizedKeyWordViewSet(viewsets.ModelViewSet):
    queryset = CategorizedKeyWord.objects.all()
    serializer_class = CategorizedKeyWordSerializer
    if settings.QT_MULTI:
        # セッション認証ができている場合にアクセスを許可する
        authentication_classes = (SessionAuthentication,)
        permission_classes = (IsAuthenticated, )
    
class BulkCreateCategorizedKeyWordView(generics.CreateAPIView):
    serializer_class = CategorizedKeyWordSerializer

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(BulkCreateCategorizedKeyWordView, self).get_serializer(*args, **kwargs)
    

#使っていない？
class DeleteCategorizedKeyWordView(generics.ListAPIView):    
    model = CategorizedActivity

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))   
    def post(self, request):
        id_list = request.data
        #print(f"delete word id list {id_list}")
        CategorizedKeyWord.objects.filter(pk__in=id_list).delete()
#        DefinitionModel().reSetPerspective()
        return Response(id_list)
    
    

'''
Created on 2024/07/05

@author: kuyamakazuhiro
'''
from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from activities.models import  Category
from activities.serializers.user_definition_serializers import _CategorySerializer
from activities.serializers.keyword_candidate_serializer import KeywordCandidateSerializer
from activities.modules.WordRecomender import WordRecomender

from django.conf import settings
from activities.decolators import attach_decorator

class KeywordCandidateView(generics.ListAPIView):
    serializer_class = KeywordCandidateSerializer
    category_id = None
    
    def evaluate_params(self):
        params = self.request.query_params
        if 'category_id' in params:
            self.category_id = int(params.get('category_id'))
    
    
    def get_queryset(self):
#        print(f"key is {self.category_id}")
#        return Category.objects.prefetch_related('activities').prefetch_related('key_words').all()
        return Category.objects.get(pk=self.category_id)

    def get_category_serializer(self, *args, **kwargs):
        serializer_class = _CategorySerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def list(self, request, *args, **kwargs):   
        self.evaluate_params()    
        queryset = self.get_queryset()
#        print(queryset)
        cat_serializer = self.get_category_serializer(queryset)
#        print(cat_serializer.data)
        wr = WordRecomender(cat_serializer.data)
        wr.createRecomendations()
#        print(f"recomendations =>{wr.recomendations}")
        serializer = self.get_serializer(wr.recomendations, many=True)
        return Response(serializer.data)
        
    
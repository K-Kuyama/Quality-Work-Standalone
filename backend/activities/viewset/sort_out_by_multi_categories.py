'''
Created on 2024/08/07

@author: kuyamakazuhiro
'''
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .sort_out_by_categories import SortOutByCategoriesView
from activities.serializers.ca_serializer import MCASerializer

from django.conf import settings
from activities.decolators import attach_decorator

class SortOutByMutiCategoriesView(SortOutByCategoriesView):
    serializer_class = MCASerializer
    sub_perspective = None

    def multiSortOut(self, c_list):
        cc_list = []
        for c_obj in c_list:
            acs = c_obj.activities
            cserializer = self.getCSerializer(acs, many=True, p_id=self.sub_perspective)
            cc_objs = self.sortOut(cserializer.data)
            #print(f"cc_obj :{cc_objs}")
            c_obj.categories = cc_objs
            c_obj.activities =[]
            #cc.categories = cserializer
            cc_list.append(c_obj)
        return cc_list

    def evaluate_params(self):
        super().evaluate_params()
        params = self.request.query_params
        if 'sub_p_id' in params:
            self.sub_perspective = int(params.get('sub_p_id'))
            

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))  
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        queryset = self.get_queryset()
        # カテゴリー情報追加
        cserializer = self.getCSerializer(queryset, many=True, p_id=self.perspective)
        # カテゴリー別にグルーピング
        #print("get c_list")
        c_list = self.sortOut(cserializer.data)
        #print(f"c_list:{c_list}")
        # さらにサブカテゴリー別にグルーピング
        cc_list = self.multiSortOut(c_list)
        
        # 合計値の計算
        if self.need_summarize:
            t_list = []
            for cc_obj in cc_list:
                ct_l = self.createSummary(cc_obj.categories)
                cc_obj.categories = ct_l
                t_list.append(cc_obj)
        else:
            t_list = cc_list
        # ページネーション
        if self.need_pagination:
            page = self.paginate_queryset(t_list)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(t_list, many=True)
            return Response(serializer.data)    
        
        
        
class CCategory:
    def __init__(self, perspective, name, color):
        self.perspective =perspective
        self.name = name
        self.color = color
        self.categories =[]
  

        
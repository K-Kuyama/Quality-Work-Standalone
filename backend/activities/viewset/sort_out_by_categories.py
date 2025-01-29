'''
Created on 2024/07/29

@author: kuyamakazuhiro
'''

from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .merged_event import MergedEventView
from activities.serializers.categorized_activity_serializer import CategorizedActivitySerializer
from activities.serializers.ca_serializer import CASerializer
from activities.modules.definition_model import ColorInfo
from activities.models import Activity

from django.conf import settings
from activities.decolators import attach_decorator

def to_color_info_class(d) -> ColorInfo:
    c = ColorInfo.__new__(ColorInfo)
    c.__dict__.update(d)
    return c

def to_activity_class(d) -> Activity:
    a = Activity()
    a.__dict__.update(d)
    return a

class SortOutByCategoriesView(MergedEventView):
    serializer_class = CASerializer
    
    perspective = None
    category = None
    need_summarize = False
    need_pagination = False
    need_all_categories = False

    #　getCSerializer : アクティビティ情報にカテゴリー情報を付加するCategorizedActivitySerializerを
    #　呼び出す。どのパースペクティブでカテゴライズするかを渡す必要があるので、p_idをcontextに格納し、
    # CategorizedActivitySerializerの中でこれを参照する    
    def getCSerializer(self, *args, **kwargs):
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context']['p_id']=kwargs.pop('p_id')
#        kwargs['context']['p_id']=self.request.query_params.get('p_id')
        #print(f"kwargs: {kwargs}")
        return CategorizedActivitySerializer(*args, **kwargs)

    # ColorInfoオブジェクトのリストを返す
    def sortOut(self, activities):
        c_dict = dict()
        a_dict = dict()
        for ac in activities:
            cid = ac['color_info']['categoryId']
            if cid not in a_dict:
                a_dict[cid] =[to_activity_class(ac)]
                c_dict[cid] = to_color_info_class(ac['color_info'])
            else:
                a_dict[cid].append(to_activity_class(ac))
#        print(a_dict)
#        print(c_dict)
        if self.category :
            c = c_dict[self.category]
            c.activities = a_dict[self.category]
            return [c]
        else :
            t_list = []
            for key in c_dict.keys():
                c = c_dict[key]
                c.activities = a_dict[key]
                t_list.append(c)
            return t_list
  


    
    def createSummary(self, c_list):
        target_list = []
        for c_obj in c_list:
            duration = 0
            distance_x = 0
            distance_y = 0
            strokes = 0
            scrolls = 0
            
#            print(len(c_obj.activities))
            for ac in c_obj.activities:
                duration += ac.duration
                distance_x += ac.distance_x
                distance_y += ac.distance_y
                strokes += ac.strokes
                scrolls += ac.scrolls
                
#            print(f"duration ->{duration}")
            tac = CActivity(None,duration, distance_x, distance_y, strokes, scrolls, None, None)
            
            c_obj.activities =[tac]
            target_list.append(c_obj)
        return target_list
    
    
    def evaluate_params(self):
        params = self.request.query_params
        if 'p_id' in params:
            self.perspective = int(params.get('p_id'))
        if 'c_id' in params:
            self.category = int(params.get('c_id'))
        else:
            self.need_all_categories = True
        if 'summarize' in params:
            if params.get('summarize').lower() == "true":
                self.need_summarize = True
        if 'pagination' in params:
            if params.get('pagination').lower() == "true":
                self.need_pagination = True    

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))          
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        queryset = self.get_queryset()
        # カテゴリー情報追加
#        cserializer = self.getCSerializer(queryset, many=True, p_id=self.request.query_params.get('p_id'))
        cserializer = self.getCSerializer(queryset, many=True, p_id=self.perspective)
        # カテゴリー別にグルーピング
        c_list = self.sortOut(cserializer.data)
        # 合計値の計算        
        if self.need_summarize:
            t_list = self.createSummary(c_list)
#
#                print()
        else:
            t_list = c_list
        # ページネーション
        if self.need_pagination:
            page = self.paginate_queryset(t_list)
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(t_list, many=True)
            return Response(serializer.data)
 
        
class CActivity:
    def __init__(self, start_time, duration, distance_x, distance_y, strokes, scrolls, app, title):
        self.start_time = start_time
        self.duration = duration
        self.distance_x = distance_x
        self.distance_y = distance_y
        self.strokes = strokes
        self.scrolls = scrolls
        self.app = app
        self.title = title

        
    
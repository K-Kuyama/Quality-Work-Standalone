'''
Created on 2024/08/18

@author: kuyamakazuhiro
'''

import calendar
from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .sort_out_by_categories import SortOutByCategoriesView
from .mixins import CreateIndexMixin
from activities.serializers.periodical_category_serializer import PeriodicalCategorySerializer

from django.conf import settings
from activities.decolators import attach_decorator

class PeriodicalCategoriesView(SortOutByCategoriesView, CreateIndexMixin):
    serializer_class = PeriodicalCategorySerializer

    
    def evaluate_params(self):
        super().evaluate_params()
        params = self.request.query_params
        if 'kind_of_period' in params:
            self.kind_of_period = params.get('kind_of_period').lower()
        else:
            self.kind_of_period = "day"

        if self.kind_of_period == "day":
            self.time_strings = "hour"
        elif self.kind_of_period == "week":
            self.time_strings = "day"
        elif self.kind_of_period == "month":
            self.time_strings = "day"
        elif self.kind_of_period == "year":
            self.time_strings = "month"
        else:
            self.time_strings = "hour"

        self.kind_of_value = self.DURATION 
        if 'kind_of_value' in params:
            if params.get('kind_of_value').lower() == 'duration':
                self.kind_of_value = self.DURATION
            elif params.get('kind_of_value').lower() == 'strokes':
                self.kind_of_value = self.STROKES
            elif params.get('kind_of_value').lower() == 'scrolls':
                self.kind_of_value = self.SCROLLS
            elif params.get('kind_of_value').lower() == 'distance':
                self.kind_of_value = self.DISTANCE
            else:
                self.kind_of_value = self.DURATION    

        st_str = self.request.query_params.get("start")
        self.start_datetime = datetime.strptime(st_str, "%Y-%m-%d %H:%M:%S.%f")


    def createResultData(self, c_list):
        if len(c_list) > 0:
            index_list = []
            for category in c_list:
                idxd = self.createIndexData(category.activities)
                index_list.append(PeriodicalCategory(category.categoryName, category.backgroundColor, idxd))
            return index_list
        else:
            return [PeriodicalCategory(None,None,self.createIndexData([]))]
        
        
    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))    
    def list(self, request, *args, **kwargs):
        self.evaluate_params()
        queryset = self.get_combined_queryset()
        # カテゴリー情報追加
        cserializer = self.getCSerializer(queryset, many=True, p_id=self.perspective)
        # カテゴリー別にグルーピング
        c_list = self.sortOut(cserializer.data)
        # 単位時間ごとのデータを作成
        pl = self.createResultData(c_list)
        
        serializer = self.get_serializer(pl, many=True)
        return Response(serializer.data)
        

class PeriodicalCategory:
    # カテゴリー別にアクティビティデータを整理したデータ構造
    def __init__(self, name, color, data):
        self.name = name
        self.backgroundColor = color
        self.data_array = data
        

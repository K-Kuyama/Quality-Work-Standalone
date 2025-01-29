'''
Created on 2024/06/28

@author: kuyamakazuhiro
'''
from .merged_event import MergedEventView
from activities.serializers.categorized_activity_serializer import CategorizedActivitySerializer

class CategorizedEventView(MergedEventView):
    serializer_class = CategorizedActivitySerializer

          
    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        #print(f"kwargs: {kwargs}")
        params = kwargs['context']['request'].query_params
        if 'p_id' in params:
            p_id = int(params.get('p_id'))
        kwargs['context']['p_id']=p_id
#        kwargs['context']['p_id']=self.request.query_params.get('p_id')

        return serializer_class(*args, **kwargs)


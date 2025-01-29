'''
Created on 2024/06/28

@author: kuyamakazuhiro
'''
from rest_framework import serializers
from activities.models import Activity
#from activities.modules.definition_model import DefinitionModel
from activities.modules.perspective_model import ModelCreator

class CategorizedActivitySerializer(serializers.ModelSerializer):
    
    color_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = ('start_time', 'duration','distance_x','distance_y','strokes','scrolls',
                  'app','title', 'color_info')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #r = self.context.get('request')
        #params = r.query_params
        #self.pm = PerspectiveModel(int(self.context.get('p_id').lower()))
        #self.pm = PerspectiveModel(self.context.get('p_id'))
        #print(f"create {self.context.get('p_id')}")
        self.pm = ModelCreator.create(self.context.get('p_id'))
       
    def get_color_info(self, obj):     
#        color_info = self.pm.get_colors(obj.app, obj.title)
        color_info = self.pm.get_colors(obj)        
        return color_info
    

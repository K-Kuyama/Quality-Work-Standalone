'''
Created on 2024/09/10

@author: kuyamakazuhiro
'''


from rest_framework import serializers
from activities.models import FileUpdateHistory

class FileUpdateHistorySerializer(serializers.ModelSerializer):
        class Meta:
            model = FileUpdateHistory
            fields = ('fileName', 'uploadTime', 'contents',
                      'startTime', 'endTime', 'dataCount', 'status')
        

                    
        
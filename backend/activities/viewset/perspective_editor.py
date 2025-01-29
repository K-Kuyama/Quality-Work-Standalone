'''
Created on 2024/07/18

@author: kuyamakazuhiro
'''

from rest_framework import generics
from rest_framework.response import Response
from activities.serializers.perspective_editor_serializer import PerspectiveEditorSerializer
from activities.models import  Perspective
from django.db import transaction

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.conf import settings
from activities.decolators import attach_decorator


class PerspectiveEditorView(generics.ListAPIView):
    serializer_class = PerspectiveEditorSerializer

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))  
    @transaction.atomic 
    def post(self, request):
        items = request.data
        r_items = []
        
        with transaction.atomic():
            idx = 0
            for it in items:
                if it['delete_flag'] :
                    Perspective.objects.filter(pk=it['id']).delete()
                elif it['id'] :
                    obj = Perspective.objects.get(pk=it['id'])
                    obj.name = it['name']
                    obj.color = it['color']
                    obj.save()
                    it['index'] = idx
                    idx += 1
                    r_items.append(it)
                else :
                    p = Perspective.objects.create(name=it['name'], color=it['color'], use_def_color=True)
                    it['id'] = p.id
                    it['index'] = idx
                    idx += 1
                    r_items.append(it)
                        
        serializer = self.get_serializer(r_items, many=True)
        return Response(serializer.data)
    
    
        
        
        
                
        
        
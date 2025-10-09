
from rest_framework import generics
from rest_framework.response import Response
from django.db import transaction

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.conf import settings
from activities.decolators import attach_decorator
from activities.serializers.category_editor_serializer import CategoryEditorSerializer
from activities.models import  Perspective, Category

class CategoryEditorView(generics.ListAPIView):
    serializer_class = CategoryEditorSerializer

    @attach_decorator(settings.QT_MULTI,method_decorator(login_required))  
    @transaction.atomic 
    def post(self, request):
        items = request.data
        r_items = []
        
        with transaction.atomic():
            idx = 0
            for it in items:
                if it['delete_flag'] :
                    Category.objects.filter(pk=it['id']).delete()
                elif it['id'] :
                    obj = Category.objects.get(pk=it['id'])
                    obj.name = it['name']
                    obj.color = it['color']
                    obj.index = it['index']
                    obj.save()
                    it['index'] = idx
                    idx += 1
                    r_items.append(it)
                else :
                    p = Perspective.objects.get(pk=it['perspective'])
                    c = Category.objects.create(perspective=p, name=it['name'], color=it['color'], index=it['index'])
                    it['id'] = c.id
                    #it['index'] = idx
                    idx += 1
                    r_items.append(it)
                        
        serializer = self.get_serializer(r_items, many=True)
        return Response(serializer.data)
    
    
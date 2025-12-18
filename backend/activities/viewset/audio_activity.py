from datetime import datetime, timezone, timedelta
#import datetime
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.db.models import Sum
from django.db.models.functions import Trunc

from activities.models import Activity, AudioActivity
from activities.serializer import AudioActivitySerializer, FormattedAudioActivitySerializer

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from activities.decolators import attach_decorator
from django.conf import settings

class CreateAudioActivityView(generics.CreateAPIView):
    serializer_class = AudioActivitySerializer
    format_str = "%Y-%m-%d %H:%M:%S.%f%z"
        
    @attach_decorator(settings.QT_MULTI,method_decorator(login_required)) 
    def create(self, request, *args, **kwargs):
        #print(f"create called")
        processed_data = None
        serializer = None
        if isinstance(request.data,list):
            result_list = []
            for act in request.data:
                selected_data = self.getLongestDurationInfo(act['start_time'], act['end_time'])
                if selected_data:
                    act['longest_app'] = selected_data['app']
                    act['longest_title'] = selected_data['title']
                else:
                    act['longest_app'] = None
                    act['longest_title'] = None                  
                act['another_app'] = None
                act['another_title'] = None
                result_list.append(act)
            processed_data = result_list
        else:
            act = request.data
            selected_data = self.getLongestDurationInfo(act['start_time'], act['end_time'])
            if selected_data:
                act['longest_app'] = selected_data['app']
                act['longest_title'] = selected_data['title']
            else:
                act['longest_app'] = None
                act['longest_title'] = None   
            act['another_app'] = None
            act['another_title'] = None
            processed_data = act
        #print(f"processed data {processed_data}")
        serializer = self.get_serializer(data=processed_data)
        #print(f"get serializer")
        serializer.is_valid(raise_exception=True)
        #print(f"validated")
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def getLongestDurationInfo(self, st_str, end_str):
        
        print(Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str)
                                       ).exclude(title="blank").values('app', 'title').annotate(total = Sum("duration")
                                                                                                ).order_by("-total"))
        return Activity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str)
                                       ).exclude(title="blank").values('app', 'title').annotate(total = Sum("duration")
                                                                                                ).order_by("-total").first()
    def get_serializer(self, *args, **kwargs):
        #print(f"args : {args}")
        #print(f"kargs : {kwargs}")
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super(CreateAudioActivityView, self).get_serializer(*args, **kwargs)


#class BulkCreateAudioActivityView(CreateAudioActivityView):
#    serializer_class = AudioActivitySerializer



class AudioActivityView(generics.ListAPIView):
    serializer_class = FormattedAudioActivitySerializer
    format_str = "%Y-%m-%d %H:%M:%S.%f"

    def get_queryset(self):
        st_str = self.request.query_params.get("start")
        #print(st_str)
        end_str = self.request.query_params.get("end")
        #print(end_str)
        return AudioActivity.objects.filter(start_time__gte=datetime.strptime(st_str, self.format_str),
                                       start_time__lte=datetime.strptime(end_str, self.format_str))


class AudioActicityUpdateView(generics.UpdateAPIView):
    queryset = AudioActivity.objects.all()
    serializer_class = AudioActivitySerializer